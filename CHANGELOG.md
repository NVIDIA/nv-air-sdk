# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [1.8.0] - 2026-09-08
- Added a NOS Manifest API for platform injection: new `os_image_manifests`, `os_templates`, and `platform_information` endpoints, exposed as `api.os_image_manifests`, `api.os_templates`, and `api.platform_information`.
- Added resource-level history access. `Simulation`, `Node`, `Image`, and `MarketplaceDemo` objects now expose `list_history()` and `get_history_filters()` for reading that specific resource's change history and its available filter values, without going through the top-level `histories` endpoint.

# [1.7.1] - 2026-09-02
- Raised the default `wait_for_state()` timeout from 2 minutes to 10 minutes, so waiting on a slow simulation start or shutdown no longer times out on a healthy simulation. The timeout is only an upper bound - the call still returns as soon as the target state is reached - so this does not slow down fast transitions. Pass `timeout=` for a tighter bound.

# [1.7.0] - 2026-08-27
- Added compute hour balances to `Organization` / `ResourceBudget`. `total_compute_hours` reports the compute hours the organization has been granted (including hours already consumed, and excluding voided or expired grants), and `remaining_compute_hours` reports a cached estimate of the compute hours it has left to spend. Both are read-only and are `None` when read from an Air deployment that does not yet report them.
- Addressed high-severity OSS vulnerabilities identified by internal security scanning.
- Fixed spurious warnings on Python 3.13 caused by stricter `typing.ForwardRef` handling when parsing `NodeInstruction.data`.
- Fixed `Simulation.documentation` still being returned by `GET` requests after the API dropped support for setting it via `POST`.
- Fixed incorrect return-type annotations in the ZTP script example notebook.

# [1.6.1] - 2026-08-09
- Fixed `Node.management_ip` / `Node.management_mac` returning `None` on nodes whose only management interface is not named `eth0` - most visibly `oob-mgmt-server`, which manages over `eth1`. The deprecated aliases now fall back to the node's sole management interface, restoring the pre-1.6.0 value. Nodes with several management interfaces and no `eth0` still return `None`; read `management_interfaces` for those. Assignment is unchanged and still raises, since a flat write always targets `eth0`.

# [1.6.0] - 2026-08-05
- Added `expected_resource_usage` as a read-only field to the MarketplaceDemo-related features.
- Added support for multiple management interfaces per node. `Node` now exposes a `management_interfaces` field mapping each interface name (e.g. `eth0`, `eth1`) to its `{ip, mac_address}`, and `nodes.create()` / `update()` / `patch()` accept `management_interfaces`.
- Deprecated the `management_ip` and `management_mac` node attributes. They continue to work as backward-compatible aliases for the default (`eth0`) management interface but now emit a `DeprecationWarning`; use `management_interfaces` instead. Assigning them on a node with multiple management interfaces raises an error to avoid silently diverging from the server.
- Added Publish Access Record (PAR) support for `Image` and `MarketplaceDemo`, via a new `image_publish_access_records` endpoint, letting organizations control which other organizations can access their published images and demos.
- Addressed high-severity OSS vulnerabilities identified by internal security scanning.


# [1.5.0] - 2026-07-15
- **Removed NetQ SaaS support.** NetQ SaaS reached end-of-life in December 2025 and has been removed from DSX Air. If you still need NetQ support in DSX Air, please use the NetQ image instead. The following NetQ-SaaS API surface has been removed:
  - **`Simulation` fields** — `auto_netq_enabled`, `netq_username`, and `netq_password`. These are no longer present on `Simulation` objects (not returned by the API) and are no longer accepted in `create()` / `update()` payloads.
  - **`Simulation` methods** — `enable_auto_netq()` and `disable_auto_netq()`. Removed from both the `Simulation` model and `SimulationEndpointAPI`.
  - **`simulations.list()` filter** — the `auto_netq_enabled` keyword argument. Simulations can no longer be filtered by NetQ status.
- Added support for dynamically changing a node's boot order.
- Added `Training.get_workbenches()` for listing the workbench simulations tied to a training.
- Added `Training.display_name`.
- Added a cloud-init usage example notebook.

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
- Restored `Interfaces.connect()` / `.disconnect()` as backward-compatible (v1/v2-style) methods, backed by a new `set-connection` action, alongside no-op handling for other deprecated interface connect/disconnect call patterns so old code degrades gracefully instead of erroring.
- Restored backward-compatible `mgmt_ip` / `mgmt_mac` values inside `Node.metadata` for v1/v2 consumers that read them from metadata rather than the top-level `management_ip` / `management_mac` fields.
- Fixed an import error in the Links endpoint caused by a `typing_extensions` dependency.

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

# [1.0.0] - 2026-01-26
- Added initial functionality
