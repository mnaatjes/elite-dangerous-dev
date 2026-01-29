# Elite Dangerous Development

This repository is for development related to Elite Dangerous.

## Data Setup

The routing application requires a data file containing star system information. Due to its size, the data file is not tracked in this repository.

To download and decompress the required data, follow these steps:

1.  **Create the data directory:**
    ```bash
    mkdir -p data/spansh/dumps
    ```

2.  **Download the neutron systems data (154M):**
    ```bash
    wget -O data/spansh/dumps/systems_neutron.json.gz https://downloads.spansh.co.uk/systems_neutron.json.gz
    ```

3.  **Decompress the file:**
    ```bash
    gunzip -k data/spansh/dumps/systems_neutron.json.gz
    ```
