## Probe and Download Strategy

**1. Data Models & Interface**

- [x] Implement ProbeResult: Create a Pydantic BaseModel to store the URL, status code, content length, ETag, last modified date, MIME type, and range support status.

- [x] Define DownloadStrategy (ABC): Create an abstract base class with a required download(url, destination, client) method that returns a SHA-256 hex digest string.

**2. Probing Logic**

- [ ] Implement SourceProber:

- [ ] HEAD Request: Logic to fetch metadata without the body.

- [ ] Partial GET Request: Logic to request the first 1KB using the Range: bytes=0-1023 header.

- [ ] MIME Type Sniffing: Integrate python-magic to inspect the byte buffer of the sample.

- [ ] Probe Method: Orchestrate the steps to return a populated ProbeResult.

**3. Download Regimes (Strategies)**

- [ ] Implement GzipRegime:

- [ ] Setup streaming via httpx.Client.stream.

- [ ] Implement on-the-fly hashlib.sha256 updates during chunk iteration.

- [ ] Handle decompression/saving to disk.

- [ ] Implement JsonRegime: Tailor streaming and hash calculation for raw JSON files.

- [ ] Implement BinaryRegime: Create a robust fallback for unknown or generic octet-stream types.

**4. Orchestration & Integration**

- [ ] Implement DownloadContext:

- [ ] Strategy Map: Define the dictionary mapping MIME types (e.g., application/gzip) to their respective Regime classes.

- [ ] execute_regime: Logic to select the strategy based on ProbeResult and manage the httpx.Client lifecycle.

- [ ] Manifest Integration: Create the final bridge to update the local manifest with the returned SHA-256 hash upon successful download.

**5. Environment & Dependencies**

- [ ] Install required Linux libraries (libmagic-dev or similar) and Python packages (httpx, python-magic, pydantic).