# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


# [1.5.0] - 2026-07-15
- **Removed NetQ SaaS support.** NetQ SaaS reached end-of-life in December 2025 and has been removed from DSX Air. If you still need NetQ support in DSX Air, please use the NetQ image instead. The following NetQ-SaaS API surface has been removed:
  - **`Simulation` fields** — `auto_netq_enabled`, `netq_username`, and `netq_password`. These are no longer present on `Simulation` objects (not returned by the API) and are no longer accepted in `create()` / `update()` payloads.
  - **`Simulation` methods** — `enable_auto_netq()` and `disable_auto_netq()`. Removed from both the `Simulation` model and `SimulationEndpointAPI`.
  - **`simulations.list()` filter** — the `auto_netq_enabled` keyword argument. Simulations can no longer be filtered by NetQ status.

# [1.4.0] - 2026-05-26
- Added new Image Sharing and Checkpoints sections to Jupyter Notebook examples.

# [1.3.1] - 2026-05-06
- Redacted a real looking registration token after it was flagged by GitHub.

# [1.3.0] - 2026-04-23
- Updated the SDK models and parsing to match the current API contract.
- Rebranded SDK docs to DSX Air.
- Renamed disable_auto_oob_dhcp to enable_dhcp and "attributes" to "labels" for the Node and Interface endpoints.
- Updated SDK Jupyter Notebook examples.
- Added org_id and ngc_org_name fields to the Organization dataclass given recent API changes.

# [1.2.0] - 2026-03-25
- Added `Checkpoint` model and `CheckpointEndpointAPI` to the SDK, enabling users to list, retrieve, update, and delete simulation checkpoints.
- Changed stubs of delete method in `ServiceEndpointAPI` to accept service ID only
- Introduced the Links endpoint as a proper RESTful resource, replacing the legacy connect()/disconnect() interface methods
- Interface connection handling is now managed by the Links API
- Fixed inconsistencies between the Manifest API and the SDK
- Improved SDK warnings

# [1.1.0] - 2026-02-24
- Added support for breaking out network interfaces into sub-interfaces and reverting them back, implementing the v3 API breakout endpoints as interface actions
- Added backward compatibility with legacy Air and to provide users with a way to store custom metadata
- Fixed an issue that we were printing the user API key in ⁠with_ngc_config function
- Due to the design of the SDK we could interacting with the management MAC's and IP's without needing to update the SDK but the existence of those fields wasn't shown to the users so this MR is here to fix this
- Implemented comprehensive SDK support for the new Training API endpoints
- Implemented automatic PATCH requests when setting model attributes, restoring backward compatibility with the v1 SDK behavior where attribute assignments would automatically sync with the API.
- Fixed an issue that some of Image fields are marked as remove fields and they is exist
- Fixed handling of API fields conflicting with model properties
- Fixes for node + node instructions + system node endpoints

## [1.0.0] - 2026-01-26
- Added initial functionality
