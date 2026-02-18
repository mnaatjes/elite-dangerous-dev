# Strategy Selection Logic

The Persistence Orchestrator acts as a "Validator of Intent," using a set of concrete parameters to select the appropriate I/O strategy. This ensures that every persistence operation is not only correct but also safe for the given system resources and data profile.

## 1. The Generator as a Signal

The most critical input for strategy selection is the shape of the data itself. By using the input type as a selection parameter, the system can react dynamically without requiring explicit flags from the user.

- **If the Repository passes a `list` or `dict`**: The Orchestrator uses an **Atomic Save** strategy.
- **If the Repository passes a `generator` or `iterator`**: The Orchestrator uses a **Streaming Save** strategy.

This "self-documenting" approach makes the architecture robust, as the code naturally adapts to the data's memory footprint.

## 2. Strategy Selection Parameters

The Orchestrator "harvests" parameters from different layers of the application to build a complete picture of the I/O operation.

| Parameter         | Source             | Type                  | Purpose                                                              |
|-------------------|--------------------|-----------------------|----------------------------------------------------------------------|
| `target`          | Repository         | `str`                 | The logical name (e.g., "Sol") used to resolve the final path.       |
| `data`            | Repository         | `Any`                 | The payload itself (Dict, Bytes, or Generator).                      |
| `write_mode`      | Repository         | `Literal["w", "wb"]`  | Explicitly sets Text vs. Binary I/O, filtering serializer choices.   |
| `policy_key`      | Repository         | `str`                 | The "Label" (e.g., "star_data") used to look up the persistence profile. |
| `checksum_algo`   | Profile            | `Strategy`            | The specific integrity algorithm (e.g., SHA256, CRC32) to be used.    |
| `max_atomic_mb`   | Profile            | `int`                 | The RAM safety threshold. If `payload_size` exceeds this, streaming is forced. |
| `available_ram`   | `SystemMonitor`    | `int`                 | The real-time available memory on the host machine.                  |
| `payload_size`    | `ItemCounter`      | `int`                 | The actual size of the data to be written.                           |

## 3. Logic Table for I/O Decisions

These parameters feed into a logic gate that determines the final execution path.

| Parameter         | Selection Influence   | Logic / Threshold                                                                        |
|-------------------|-----------------------|------------------------------------------------------------------------------------------|
| `write_mode`      | Serializer Choice     | If `"wb"`, filter for Binary strategies (e.g., MsgPack). If `"w"`, filter for Text strategies (e.g., JSON). |
| `payload_size`    | I/O Regime            | If `payload_size` > `max_atomic_mb`, force Streaming/Chunked mode.                       |
| `available_ram`   | Safety Gate           | If `payload_size` > `available_ram`, abort the I/O operation to prevent a system crash.    |
| `checksum_algo`   | Integrity Choice      | Dictates which algorithm object is instantiated from the integrity checking library.     |
| `Adapter Type`    | Execution Path        | Determines if the final step is a filesystem `write()` or a database `execute()`.        |

The Orchestrator's job is to compare the constraints defined in the **Profile** against the ground truth reported by the **Core Monitors** (`SystemMonitor`, `ItemCounter`) and execute the operation using the mode and data provided by the **Repository**.
