# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-24
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
