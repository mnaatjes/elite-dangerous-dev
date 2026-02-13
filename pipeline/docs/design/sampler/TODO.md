# Sampler Implementation To-Do List

This document outlines the tasks required to implement, integrate, and test the data sampler as designed in `sampler_design.md`.

## Phase 1: Core Class Implementation

-   [ ] **Create Abstract Base Classes:**
    -   In a new file `etl/src/sampling/base.py`, define the ABCs:
        -   `SamplingStrategy(ABC)`
        -   `OutputStrategy(ABC)`
        -   `Sampler(ABC)`

-   [ ] **Implement Concrete Sampling Strategies:**
    -   In `etl/src/sampling/strategies.py`, create the initial set of strategies:
        -   `FirstNStrategy(SamplingStrategy)` (Parameter: `n`)
        -   `RandomSampleStrategy(SamplingStrategy)` (Parameters: `n`, `seed`)

-   [ ] **Implement Concrete Output Strategies:**
    -   In `etl/src/sampling/outputs.py`, create the initial output strategies:
        -   `JsonOutputStrategy(OutputStrategy)`
        -   `CsvOutputStrategy(OutputStrategy)` (Consider how to handle nested JSON, perhaps requiring a `fieldnames` parameter).

-   [ ] **Implement the `JsonGzipSampler`:**
    -   In `etl/src/sampling/samplers.py`, create the `JsonGzipSampler(Sampler)` class.
    -   Implement the `execute` method to read from a `.json.gz` file and orchestrate the sampling and output process.

## Phase 2: Unit Testing

-   [ ] **Test Sampling Strategies:**
    -   Create `etl/tests/sampling/test_strategies.py`.
    -   For each strategy, write tests to verify it correctly selects records from a mock iterator.
    -   Test edge cases (e.g., `n` is larger than the number of records, `n` is 0).

-   [ ] **Test Output Strategies:**
    -   Create `etl/tests/sampling/test_outputs.py`.
    -   Use `unittest.mock.patch` to mock `open`.
    -   Verify that each strategy writes the correct data in the expected format.

-   [ ] **Test `JsonGzipSampler`:**
    -   Create `etl/tests/sampling/test_samplers.py`.
    -   Write an integration test for the sampler.
    -   Use a real (but small) `.json.gz` test asset.
    *   Verify that the `execute` method calls the `sample` and `write` methods of its strategies correctly.

## Phase 3: Integration

-   [ ] **Create a CLI/Entrypoint:**
    -   Create a script `etl/tools/create_sample.py` that can be run from the command line.
    -   Use `argparse` to allow the user to specify:
        -   Source file path.
        -   Sampler to use (e.g., `jsongzip`).
        -   Sampling strategy (e.g., `first_n`).
        -   Strategy parameters (e.g., `--n 100`).
        -   Output strategy (e.g., `json`).
        -   Output file path (optional, can be derived).

-   [ ] **Integrate `PathManager`:**
    -   Use the `PathManager` (from the previous refactoring) to resolve paths and handle file I/O within the output strategies.
    -   The CLI tool should use the `PathManager` to determine the correct output directory for the sample and its manifest.

-   [ ] **Implement Manifest Generation:**
    -   After a sample is successfully created, the entrypoint script should generate and save the corresponding `.manifest.json` file.
    -   This will involve gathering metadata from the source file, the strategies, and the output file.

## Phase 4: Documentation & Finalization

-   [ ] **Update Project Documentation:**
    -   Add a section to the main `README.md` or a new document in `docs/technical/` explaining how to use the sampling tool.

-   [ ] **Code Review:**
    -   Conduct a final code review of all new sampler-related code.
    -   Ensure the design principles have been followed and the code is clean, tested, and documented.
