# Extractor Class Guidance: Content-Type, Content-Encoding, and File Size

This document outlines how to effectively integrate `Content-Type` and `Content-Encoding` determination into your `Extractor` class and discusses the importance of determining file size.

### 1. Using `Content-Type` and `Content-Encoding` in Your `Extractor`

Your `Extractor` class is responsible for fetching the raw data. The `Content-Type` and `Content-Encoding` are crucial metadata that the `Extractor` should understand and handle to ensure correct processing and data integrity.

#### a. Storing and Passing Metadata

The `Extractor` should capture these properties and associate them with the data it extracts. A good pattern is for the `Extractor` to return not just the raw content, but also this critical metadata. This ensures that downstream components (like the `Transformer` and `Loader`) have all the necessary information.

```python
# In your Extractor class (e.g., etl/src/Extractor.py)
import requests
import gzip # Needed for manual decompression if Content-Encoding header is missing but inferred
import brotli # Needed for manual decompression (if used for '.br' files)
from urllib.parse import urlparse
# Assuming Utils and your warning categories are available
from etl.src.Utils import Utils, ContentEncodingMissingWarning, ContentTypeWarning, ContentTypeFallbackWarning
import warnings

# A simple data class to hold extracted content and its metadata
class ExtractedData:
    def __init__(self, content: bytes, content_type: str, content_encoding: str, original_url: str, file_size: int = None):
        self.content = content
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.original_url = original_url
        self.file_size = file_size
        # Add other metadata like headers, etc., as needed

class Extractor:
    def __init__(self, url: str):
        self.url = url
        self.final_content_type = None
        self.final_content_encoding = None
        self.file_size = None # Determined before or after download

    def _determine_metadata(self):
        """Internal method to determine content type, encoding, and file size using Utils."""
        
        # 1. Determine Content-Encoding first
        self.final_content_encoding = self._resolve_content_encoding()
        
        # 2. Determine file size (attempt pre-download)
        self._determine_file_size()

        # 3. Determine Content-Type
        self.final_content_type = self._resolve_content_type(self.final_content_encoding)

    def _resolve_content_encoding(self) -> str:
        """Applies the decision tree to determine Content-Encoding."""
        try:
            head_res = requests.head(self.url, allow_redirects=True, timeout=5)
            head_res.raise_for_status()
            header_encoding = head_res.headers.get('Content-Encoding', '').lower()

            if header_encoding and header_encoding in Utils.STANDARD_CONTENT_ENCODINGS:
                return header_encoding
            
            url_path = urlparse(self.url).path
            if url_path.endswith('.gz'):
                warnings.warn(f"Content-Encoding header missing for {self.url}; inferred as 'gzip' from extension.", ContentEncodingMissingWarning)
                return 'gzip'
            elif url_path.endswith('.br'):
                warnings.warn(f"Content-Encoding header missing for {self.url}; inferred as 'br' from extension.", ContentEncodingMissingWarning)
                return 'br'
            # Add other common compressed extensions if needed
            
            return 'identity' # Default if no header and no strong extension hint
        except requests.exceptions.RequestException as e:
            warnings.warn(f"HEAD request failed for {self.url} during encoding determination: {e}. Assuming 'identity'.", ContentEncodingMissingWarning)
            return 'identity'


    def _resolve_content_type(self, resolved_encoding: str) -> str:
        """Applies the decision tree to determine Content-Type."""
        try:
            head_res = requests.head(self.url, allow_redirects=True, timeout=5)
            head_res.raise_for_status()
            header_content_type = head_res.headers.get('Content-Type', '').lower()

            # Path 1: Header is present and specific
            if header_content_type not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                return header_content_type
            else:
                warnings.warn(f"Header Content-Type '{header_content_type}' is non-specific for {self.url}. Attempting content-based detection.", ContentTypeFallbackWarning)

            # Path 2: Attempt Content-Based Detection
            # This would require a modified Utils.get_type_from_sample that
            # handles decompression based on resolved_encoding.
            # Example:
            # content_type_from_sample = Utils.get_type_from_sample(self.url, resolved_encoding)
            # if content_type_from_sample and content_type_from_sample not in Utils.NON_SPECIFIC_CONTENT_TYPES:
            #     return content_type_from_sample
            # else:
            #     warnings.warn(f"Content-based detection for {self.url} was also non-specific or failed.", ContentTypeFallbackWarning)

            # Simplified for now, directly calling get_type_from_sample (needs modification to Utils)
            content_type_from_sample = Utils.get_type_from_sample(self.url) # Assuming this is updated to handle encoding internally
            if content_type_from_sample and content_type_from_sample not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                 return content_type_from_sample

            warnings.warn(f"Content-based detection for {self.url} failed or was non-specific. Falling back to extension guessing.", ContentTypeFallbackWarning)

            # Path 3: Fallback to Extension-Based Guessing
            url_path = urlparse(self.url).path
            extension_guessed_type, _ = mimetypes.guess_type(url_path)
            if extension_guessed_type and extension_guessed_type not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                warnings.warn(f"Relying on Content-Type ('{extension_guessed_type}') from file extension for {self.url}.", ContentTypeFallbackWarning)
                return extension_guessed_type
            else:
                warnings.warn(f"Unable to determine Content-Type for {self.url}. Defaulting to 'application/octet-stream'.", ContentTypeWarning)
                return 'application/octet-stream'

        except requests.exceptions.RequestException as e:
            warnings.warn(f"HEAD/GET request failed for {self.url} during Content-Type determination: {e}. Falling back to extension guessing.", ContentTypeFallbackWarning)
            url_path = urlparse(self.url).path
            extension_guessed_type, _ = mimetypes.guess_type(url_path)
            if extension_guessed_type and extension_guessed_type not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                return extension_guessed_type
            return 'application/octet-stream'


    def extract(self) -> ExtractedData:
        self._determine_metadata() # First determine type, encoding, and file size

        # Now, perform the actual download using determined encoding
        res = requests.get(self.url, stream=True, timeout=30)
        res.raise_for_status()

        downloaded_content = b''
        # requests automatically decompresses if Content-Encoding header was present AND understood.
        # If Content-Encoding was *inferred* (e.g., .gz extension) but header was missing,
        # requests will *not* decompress automatically. You need to handle it.

        if self.final_content_encoding == 'gzip' and res.headers.get('Content-Encoding') != 'gzip':
            # Manual decompression needed because header was missing but inferred from extension
            with gzip.GzipFile(fileobj=res.raw) as gzipped_file:
                downloaded_content = gzipped_file.read()
        elif self.final_content_encoding == 'br' and res.headers.get('Content-Encoding') != 'br':
             # Manual decompression for Brotli
            downloaded_content = brotli.decompress(res.raw.read())
        else:
            # Let requests handle it (if header was present) or assume no compression (identity)
            for chunk in res.iter_content(chunk_size=8192):
                downloaded_content += chunk
        
        # If file_size wasn't determined by Content-Length, get it now
        if self.file_size is None:
            self.file_size = len(downloaded_content)

        return ExtractedData(
            content=downloaded_content,
            content_type=self.final_content_type,
            content_encoding=self.final_content_encoding,
            original_url=self.url,
            file_size=self.file_size
        )

# Example modification to Utils.get_type_from_sample to accept encoding (as discussed)
# @staticmethod
# def get_type_from_sample(url: str, content_encoding: str) -> str:
#     res = requests.get(url, stream=True, timeout=10)
#     res.raise_for_status()
#     sample = res.raw.read(1024) # Read raw (potentially compressed) sample
#     res.close()
#
#     if content_encoding == 'gzip':
#         try:
#             sample = gzip.decompress(sample) # Decompress the sample before passing to magic
#         except Exception:
#             # Handle decompression error, maybe log and return generic type
#             pass
#     elif content_encoding == 'br':
#         try:
#             sample = brotli.decompress(sample) # Decompress Brotli sample
#         except Exception:
#             pass
#     # Add other encodings here
#     
#     return magic.from_buffer(sample, mime=True)
```

#### b. Implications for Downstream

*   **`Transformer`:** The `Transformer` will receive the `ExtractedData` object. It should then use `extracted_data.content_type` to decide how to parse `extracted_data.content`. For example, if `content_type` is `application/json`, it calls `json.loads()`; if `text/xml`, an XML parser; if `image/jpeg`, an image processing library.
*   **`Loader`:** The `Loader` can use `extracted_data.content_type` to determine the correct file extension for saving the processed data, and `extracted_data.file_size` for reporting or storage management.

### 2. Determining the Size of the Target File

It is generally **highly recommended to determine the size of the target file *before* initiating the full download process.**

#### a. Pre-Download Size Determination (Recommended)

1.  **Method:** Perform a `HEAD` request to the URL. This request only fetches headers, not the entire body.
2.  **Header to Check:** Look for the `Content-Length` header in the response from the `HEAD` request.

```python
# In your Extractor class, in _determine_metadata or a separate method
def _determine_file_size(self):
    try:
        head_res = requests.head(self.url, allow_redirects=True, timeout=5)
        head_res.raise_for_status()
        content_length_str = head_res.headers.get('Content-Length')
        if content_length_str:
            self.file_size = int(content_length_str)
            # Example pre-check:
            # if self.file_size > MAX_ALLOWED_FILE_SIZE:
            #     raise ValueError(f"File {self.url} is too large ({self.file_size} bytes).")
        else:
            self.file_size = None
            warnings.warn(f"Content-Length header not found for {self.url}. Cannot determine file size before download.", ContentTypeWarning)
    except requests.exceptions.RequestException as e:
        self.file_size = None
        warnings.warn(f"HEAD request failed for {self.url}: {e}. Cannot determine file size before download.", ContentTypeWarning)
```

#### b. During/Post-Download Size Determination (Fallback)

If the `Content-Length` header is missing or unavailable, you will have to determine the size during or after the actual `GET` request:

*   **During:** If you're streaming the content, you can keep a running count of bytes received.
*   **After:** If you load the entire content into memory (e.g., `downloaded_content = res.content`), simply use `len(downloaded_content)`.

**Recommendation:**

Always attempt to get the `Content-Length` via a `HEAD` request first. It's a quick, efficient way to gather crucial information for better management of your ETL pipeline. Use the post-download methods as a fallback if `Content-Length` is not provided.
