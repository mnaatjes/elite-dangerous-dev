# Configuration

The `etl` component is configured via a combination of a `.env` file and environment variables, managed by the Pydantic `ETLConfig` model. This approach provides a robust and type-safe way to manage application settings.

## 1. Loading Mechanism

-   **File:** The system loads settings from a `.env` file located at the root of the `etl` component (`etl/.env`).
-   **Environment Variables:** It can also read variables directly from the system's environment.
-   **Prefix:** All environment variables must be prefixed with `ETL_`. For example, to set the `version`, you would use `ETL_VERSION=1.0.1`.
-   **Nested Delimiter:** Nested configuration objects are accessed using a double underscore (`__`). For example, to set the `dry_run` flag in the `orchestration` settings, you would use `ETL_ORCHESTRATION__DRY_RUN=true`.

## 2. Main Configuration (`ETLConfig`)

This is the primary configuration class defined in `etl/src/config/model.py`.

| Key | Environment Variable | Type | Default | Description |
| :-- | :--- | :--- | :--- | :--- |
| `root_dir` | (not settable) | `Path` | (component root) | The automatically determined root directory of the `etl` component. |
| `version` | `ETL_VERSION` | `str` | `"1.0"` | The version of the ETL application. |
| `environment` | `ETL_ENVIRONMENT` | `str` | `"dev"` | The runtime environment (`dev`, `staging`, or `production`). |
| `db_connection_string` | `ETL_DB_CONNECTION_STRING` | `str` | `None` | The connection string for the target database. |
| `user_agent` | `ETL_USER_AGENT` | `str` | `"ED-ETL-Pipeline"` | The default User-Agent for HTTP requests. |

`ETLConfig` also contains the following nested configuration objects.

### 2.1. Orchestration Settings (`orchestration`)

These are boolean flags that control the execution flow of the pipeline, defined in `etl/src/config/orchestration.py`.

| Key | Environment Variable | Type | Default | Description |
| :-- | :--- | :--- | :--- | :--- |
| `dry_run` | `ETL_ORCHESTRATION__DRY_RUN` | `bool` | `False` | If `True`, the pipeline will only probe sources and not perform downloads. |
| `force_refresh`| `ETL_ORCHESTRATION__FORCE_REFRESH` | `bool` | `False` | If `True`, forces re-downloading of all sources, ignoring manifest state. |
| `skip_validation`| `ETL_ORCHESTRATION__SKIP_VALIDATION`| `bool` | `False` | If `True`, skips the validation step after download. |
| `strict_mode` | `ETL_ORCHESTRATION__STRICT_MODE` | `bool` | `False` | A general-purpose strict mode flag for future use. |
| `testing_mode`| `ETL_ORCHESTRATION__TESTING_MODE` | `bool` | `True` | If `True`, resolves data paths to within the `etl/tests/` directory. |

### 2.2. Download Settings (`downloads`)

Settings specific to the download process, defined in `etl/src/config/downloads.py`.

| Key | Environment Variable | Type | Default | Description |
| :-- | :--- | :--- | :--- | :--- |
| `raw_dir` | `ETL_DOWNLOADS__RAW_DIR` | `Path` | `"data/raw"` | Relative path for storing raw, unprocessed downloaded files. |
| `destination_dir`| `ETL_DOWNLOADS__DESTINATION_DIR`| `Path` | `"data/downloads"` | Relative path for storing final, processed downloaded files. |
| `manifest_dir`| `ETL_DOWNLOADS__MANIFEST_DIR` | `Path` | `"data/manifests"` | Relative path for storing manifest files. |
| `timeout` | `ETL_DOWNLOADS__TIMEOUT` | `int` | `30` | Default timeout in seconds for download requests. |
| `chunk_size` | `ETL_DOWNLOADS__CHUNK_SIZE` | `int` | `131072` | The size of chunks (in bytes) to use when streaming downloads. |

### 2.3. Network Settings (`network`)

Global settings for network clients, defined in `etl/src/config/network.py`.

| Key | Environment Variable | Type | Default | Description |
| :-- | :--- | :--- | :--- | :--- |
| `user_agent` | `ETL_NETWORK__USER_AGENT` | `str` | `"Elite-Dangerous-ETL/1.0"` | A more specific User-Agent, can override the main one. |
| `pool_max_connections`| `ETL_NETWORK__POOL_MAX_CONNECTIONS`| `int` | `10` | Maximum number of connections for the HTTP client pool. |
| `default_retry_count`| `ETL_NETWORK__DEFAULT_RETRY_COUNT` | `int` | `3` | Default number of retries for failed network requests. |
| `checksum_priority`| `ETL_NETWORK__CHECKSUM_PRIORITY` | `list[str]` | `["x-amz-meta-sha256", ...]` | The preferred order of headers to use for checksum validation. |

## 3. Example `.env` file

Create this file at `etl/.env` to configure the application.

```env
# Sample .env file for the ETL Component

ETL_VERSION="1.1.0"
ETL_ENVIRONMENT="dev"
ETL_DB_CONNECTION_STRING="postgresql://user:password@localhost:5432/elitedata"

# --- Orchestration Overrides ---
ETL_ORCHESTRATION__DRY_RUN=false
ETL_ORCHESTRATION__FORCE_REFRESH=false
ETL_ORCHESTRATION__TESTING_MODE=true

# --- Download Overrides ---
ETL_DOWNLOADS__TIMEOUT=60
```
