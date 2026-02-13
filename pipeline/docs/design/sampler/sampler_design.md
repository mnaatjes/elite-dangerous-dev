# Data Sampler Design

This document outlines the design for a flexible and extensible data sampling utility. The primary goal is to create a system that can take a large data file (like a gzipped JSON file) and produce a smaller, representative sample for use in development, testing, or analysis.

## 1. Core Concepts & Design Patterns

The design will be based on the **Strategy Pattern** to achieve the required flexibility. We will decouple the core sampling orchestration from the specific algorithms for *how* to sample and *what* to output.

- **Sampler Context:** A main `Sampler` class will act as the context. It will be configured with a *Sampling Strategy* and an *Output Strategy*. Its role is to orchestrate the process: open the source file, feed records to the sampling strategy, and pass the sampled records to the output strategy.

- **Sampling Strategies:** These classes will contain the logic for selecting records. Each strategy will implement a common interface (e.g., an abstract base class `SamplingStrategy`).
  - `FirstNStrategy`: Samples the first N records.
  - `RandomSampleStrategy`: Samples N records randomly from the file.
  - `EveryNthStrategy`: Samples every Nth record.

- **Output Strategies:** These classes will handle the formatting and writing of the sampled data to a destination file. Each will implement an `OutputStrategy` interface.
  - `JsonOutputStrategy`: Writes records to a JSON file.
  - `CsvOutputStrategy`: Writes records to a CSV file, potentially flattening nested JSON.

This approach makes the system highly extensible. To add a new sampling algorithm or output format, we only need to create a new strategy class, without modifying the existing orchestration logic.

## 2. Proposed Architecture

### Abstract Base Classes (ABCs)

```python
from abc import ABC, abstractmethod
from typing import Iterator, List, Any
from pathlib import Path

class SamplingStrategy(ABC):
    @abstractmethod
    def sample(self, records: Iterator[Any]) -> Iterator[Any]:
        """Receives an iterator of records and yields a sampled subset."""
        pass

class OutputStrategy(ABC):
    @abstractmethod
    def write(self, records: Iterator[Any], destination_path: Path):
        """Takes an iterator of sampled records and writes them to a file."""
        pass

class Sampler(ABC):
    def __init__(self, sampling_strategy: SamplingStrategy, output_strategy: OutputStrategy):
        self.sampling_strategy = sampling_strategy
        self.output_strategy = output_strategy

    @abstractmethod
    def execute(self, source_path: Path, destination_path: Path):
        """Orchestrates the sampling process."""
        pass
```

### Concrete Implementation: `JsonGzipSampler`

This sampler will be responsible for opening a `.json.gz` file and yielding records one by one.

```python
import gzip
import json

class JsonGzipSampler(Sampler):
    def execute(self, source_path: Path, destination_path: Path):
        # 1. Open source and get record iterator
        with gzip.open(source_path, 'rt', encoding='utf-8') as f:
            records_iterator = (json.loads(line) for line in f)

            # 2. Apply the sampling strategy
            sampled_records = self.sampling_strategy.sample(records_iterator)

            # 3. Apply the output strategy
            self.output_strategy.write(sampled_records, destination_path)
```

## 3. Output Directory Structure

Sampled files should be stored in a dedicated `samples` directory within the project's data testing assets directory, structured to be descriptive and avoid collisions.

The proposed structure is:
`tests/data/samples/<source_filename_without_ext>/<sampler_name>/<timestamp>_<sampling_strategy_name>.ext`

**Example:**

- **Source:** `/path/to/downloads/2026/02/spansh_systems_FULL_...v1-0.json.gz`
- **Sampled Output:** `tests/data/samples/spansh_systems_FULL_...v1-0/JsonGzipToJsonSampler/20260214_103000_first_100.json`

This structure clearly associates samples with their source and the method used to create them.

## 4. Sampler Manifest

A manifest file should be created alongside each sampled output to provide metadata about the sampling process. This is crucial for reproducibility and debugging. The manifest will be a JSON file with the same name as the sample but with a `.manifest.json` extension.

**Example Manifest:** `.../first_100.manifest.json`

### Manifest Schema:

```json
{
  "source_details": {
    "path": "/srv/elite-dangerous-dev/pipeline/tests/data/downloads/2026/02/spansh_systems_FULL_20260213_213251_v1-0.json.gz",
    "checksum_sha256": "a1b2c3d4...",
    "total_records": 1500000
  },
  "sampler_details": {
    "sampler_class": "JsonGzipSampler",
    "sampling_strategy": "FirstNStrategy",
    "sampling_params": {
      "n": 100
    },
    "output_strategy": "JsonOutputStrategy"
  },
  "output_details": {
    "path": "/srv/elite-dangerous-dev/pipeline/tests/data/samples/spansh_systems_FULL_...v1-0/JsonGzipSampler/20260214_103000_first_100.json",
    "checksum_sha256": "e5f6g7h8...",
    "record_count": 100
  },
  "run_details": {
    "timestamp_utc": "2026-02-14T10:30:00.123456Z",
    "etl_version": "1.1"
  }
}
```

**Properties Explained:**

- **`source_details`**: Information about the original file. `total_records` may be expensive to compute and could be optional.
- **`sampler_details`**: Defines *how* the sampling was performed, including the specific classes and parameters used.
- **`output_details`**: Information about the resulting sample file.
- **`run_details`**: Context about the execution environment.
