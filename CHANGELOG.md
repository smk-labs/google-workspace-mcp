# Changelog

All notable changes to **google-workspace-mcp** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Plugin releases are driven by the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json): users receive an update
only when it is bumped.

## [Unreleased]

## [0.7.2] - 2026-11-10

### Security

- Enforce the `GWM_ACCOUNTS` allowlist before reading a token, including when a
  token for an unlisted account already exists on disk.
- Validate the OAuth callback's `state` before exchanging the authorization
  code.

### Fixed

- Enable Tasks and People in the guided setup and check for the server binary
  without starting it.
- Point installation, marketplace, issue, and release links at the public
  `smk-labs` repository.
- Correct the Gmail and Contacts documentation and remove duplicate tool rows.
- Include both marketplace version fields in the CI version check and release
  instructions.
- Remove project-specific details and personal-looking fixtures from the
  public source tree.

## 0.7.1 - 2026-08-09

### Fixed

- Refresh tokens against the scopes they were actually granted, rather than
  the full current scope list. Existing accounts keep working when a new
  service adds scopes.
- Tools that need a missing scope now identify it and provide the exact
  re-authorization command.
- Add regression tests for granted-scope refresh behavior.

## 0.7.0 - 2026-08-09

### Added

- **Google Contacts** support via the People API: seven read-only tools for
  saved contacts, other contacts, contact groups, search, and batch fetch.
- Read-only Contacts OAuth scopes and People API setup documentation.
- Contact summary helpers and the first unit-test suite.
- Pytest in the CI workflow alongside lint and import checks.

## 0.6.0 - 2026-07-06

### Added

- `drive_file_link_access` to create or revoke anyone-with-the-link access and
  return a direct download URL for temporary server-side file handoffs.

## 0.5.0 - 2026-07-04

### Added

- `gmail_label_create` with nested-label support and idempotent handling of
  existing labels.
- `gmail_attachment_download` for attachments referenced by a full Gmail
  message payload.

## 0.4.0 - 2026-06-09

### Added

- Changelog, security policy, code of conduct, and contribution guide.
- Continuous integration, issue forms, a pull-request template, and Dependabot.
- Editor and line-ending configuration.

### Changed

- Reworked the README into an installation, setup, security, and tool reference.
- Added Tasks to the plugin, marketplace, and package descriptions.
- Expanded ignore rules for local secrets and settings.

## 0.3.0 - 2026-06-09

### Added

- **Google Tasks** support with ten tools for task lists and tasks.
- The Google Tasks OAuth scope and re-authorization documentation.

## 0.2.0 - 2026-06-09

### Added

- Initial multi-account Google Workspace MCP server for Claude Code, packaged
  as a plugin that is also its own marketplace.
- Gmail, Calendar, and Drive tools.
- Runtime account registry, per-project account scoping, and OAuth CLI.
- The `/google-workspace-setup` guided-setup command.

[Unreleased]: https://github.com/smk-labs/google-workspace-mcp/compare/v0.7.2...HEAD
[0.7.2]: https://github.com/smk-labs/google-workspace-mcp/releases/tag/v0.7.2
