
# --- Libraries ---
import httpx
import magic
from typing import Any
from pydantic import BaseModel

# --- Source ---
from ..source_probe.model import ProbeResult
from ..source_probe.checksum_metadata import ChecksumMetadata

class SourceProber(BaseModel):
    # --- Pydantic Validated Init Parameters ---
    user_agent:str
    chunk_size: int
    timeout: int = 5
    follow_redirects: bool = True
    max_retries: int = 1
    sample_size: int = 1024

    def model_post_init(self, context: Any) -> None:
        pass

    def execute(self, url:str):
        """
        Performs "explratory" check on remote source to identify content
        - HEAD request for headers
        - Partial GET for sample to evaluate
        - Values collected and returned for Download Strategy evaluation

        url -- Source URL to be probed
        Return: ProbeResult object will values populated
        """
        # --- Perform HTTP HEAD and GET ---
        with httpx.Client(timeout=self.timeout, follow_redirects=self.follow_redirects) as client:

            # --- Collect Headers ---
            res_head = client.head(url=url)

            # Abandon if head error
            if res_head.is_error:
                return ProbeResult(
                    url=url, 
                    status_code=res_head.status_code,
                    checksum_metadata=ChecksumMetadata(),
                    probe_error=f"HTTP Error: {res_head.reason_phrase}"
                )
                
            # Collect Checksum Metadata as obj
            checksum_metadata = ChecksumMetadata.from_headers(res_head.headers)
            
            # TODO: Determine course of action if false
            # TODO: Utilize value
            range_supported = res_head.headers.get("Accept-Ranges") == "bytes"

            # --- Take Sample | Collect Response Data---

            mime_type = "unknown"
            try:
                # Grab Sample
                res_get = client.get(
                    url=url,
                    headers={"Range": f"bytes=0-{self.sample_size - 1}"}
                )

                # Check 200, 206 [request processed]
                if res_get.status_code in (200, 206):
                    # Assign Mimetype from magic
                    mime_type = magic.from_buffer(res_get.content, mime=True)

                # Form and Return completed Object
                return ProbeResult(
                    url=url,
                    status_code=res_head.status_code,
                    content_length=int(res_get.headers.get("Content-Length", 0)),
                    last_modified=res_head.headers.get("Last-Modified"),
                    mime_type=mime_type,
                    is_range_supported=range_supported,
                    checksum_metadata=checksum_metadata
                )

            except (httpx.HTTPError, Exception) as e:
                # Form classname of exception (e.g. Connection Timeout) and message
                error_msg = f"{type(e).__name__}: {str(e)}"

                # Return Object with Errors
                return ProbeResult(
                    url=url, 
                    status_code=0, # Denotes network/protocol failure
                    mime_type="error",
                    checksum_metadata=checksum_metadata,
                    probe_error=error_msg
                )