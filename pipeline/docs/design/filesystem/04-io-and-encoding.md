# I/O, Encoding, and Streams

At its core, all data on a disk consists of bytes (1s and 0s). The distinction between writing in text mode (`"w"`) versus binary mode (`"wb"`) is about who handles the process of **encoding**—translating abstract characters into bytes.

## Text Mode ("w", "r") vs. Binary Mode ("wb", "rb")

### The "Interface" Bridge: Encoding

The bridge between a Python string and the disk is **Encoding**. A string is an abstract Unicode concept; a disk understands numbers (e.g., 65 for 'A' in UTF-8).

*   **Text Mode (`"w"`)**: A "Smart" stream. Python uses a `TextIOWrapper` to automatically encode strings into bytes on write and decode bytes into strings on read, based on a specified or system-default encoding. It also handles universal newlines.
*   **Binary Mode (`"wb"`)**: A "Raw" stream. Python assumes the data is already in bytes and performs no translation. Trying to write a string to a `"wb"` stream will cause a `TypeError`.

### Why the FilesystemAdapter should prefer `wb`

For a low-level adapter in a backend system, binary mode is preferred:
1.  **Explicitness**: It forces higher layers (like a `PersistenceManager`) to explicitly define the encoding (e.g., `data.encode('utf-8')`), preventing bugs caused by different environment locales.
2.  **Universality**: A `"wb"` stream can handle any file type (JSON, images, PDFs), whereas a `"w"` stream is only for text.
3.  **Performance**: It avoids the overhead of text-mode features like newline translation.

## Library Behavior: `json` vs. `ijson`

Different libraries expect different stream types:

| Library         | Input/Output Type | Recommended Mode | Why?                                                     |
|-----------------|-------------------|------------------|----------------------------------------------------------|
| `json.dump()`   | Text              | `"w"`            | Expects a file-like object that accepts strings.         |
| `json.dumps()`  | String            | N/A              | Returns a string, which you must then `.encode()` for `wb`. |
| `ijson`         | Bytes             | `"rb"`           | A streaming parser that reads the raw byte stream directly.|
| `pickle`        | Bytes             | `"wb"`/`"rb"`     | A binary format that never uses text mode.               |

**Pro Tip**: In an ETL pipeline, always use `"wb"` for writing and handle encoding explicitly (e.g., `f.write(json.dumps(data).encode('utf-8'))`). This ensures consistency across different systems. **UTF-8** is the industry standard.

## The I/O Stack Flow

1.  **Your Code**: Holds an object, like a Python `dict`.
2.  **Persistence Layer**: Serializes the object into a string (`json.dumps(dict)`).
3.  **Encoding Bridge**: Encodes the string into bytes (`string.encode('utf-8')`).
4.  **Adapter Layer**: Writes the bytes to a file opened in binary mode (`open(path, 'wb').write(bytes)`).
5.  **Linux Kernel**: Receives the bytes and writes them to the physical disk.

## Standard vs. Streaming Writes

*   **Standard (Batch)**: `json.dump()` typically builds the entire string representation in RAM before writing to disk. This is memory-intensive for large objects. The process is **Sequential and Buffered**: Object -> String -> Bytes -> OS Buffer -> Disk.
*   **Streaming**: Libraries like `ijson` or a custom encoder process the data in chunks, keeping memory usage low and constant regardless of file size.

### Does "Write to Bytes" mean the file is Binary or Text?

"Binary" describes the *method* of writing, while "ASCII/UTF-8" describes the *content*.

-   If you write bytes corresponding to a character table (e.g., `b'{"status": "ok"}'`), the resulting file is a **Text File**.
-   If you write arbitrary byte values (e.g., `b'\xff\xd8\xff\xe0'`), the resulting file is a **Binary File** (like a JPEG).

Using `wb` simply tells the system: "Write these exact bytes to disk without interpretation."
