# Changelog

All notable changes to this service are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the service uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.1.0] - 2025-09-30

### Added
- Blocked merchant categories (`CARDS_BLOCKED_MERCHANT_CATEGORIES`), declined with
  `merchant_category_blocked`.

## [2.0.0] - 2025-06-16

### Changed
- Declined authorizations are stored with their decline code, and listed by
  `GET /cards/{id}/authorizations` together with approvals.
- Authorization responses include `decline_reason`.

## [1.1.0] - 2025-04-01

### Added
- `POST /cards/{id}/close`.
- `GET /audit-events`.

## [1.0.0] - 2025-03-10

### Added
- Cards, authorization decisions with per-tier caps, and the audit trail.
