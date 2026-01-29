# V1 Engine Development Plan

This document tracks the actionable steps for building and testing the V1 routing engine data pipeline.

## Data Pipeline (ETL)

- [ ] Create Python ETL script for data transformation.
- [ ] Download `systemsWithCoordinates.json.gz` from EDSM.
- [ ] Stream-parse the gzipped JSON to extract `id64` and `coords`.
- [ ] Generate a custom binary file with the extracted system data.
- [ ] (Optional) Compress the final binary file using Zstandard.
- [ ] Update the C++ `DataLoader` to read the binary file.
- [ ] Integrate and test the full pipeline from download to R-tree build.
