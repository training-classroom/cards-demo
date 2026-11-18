# ADR 0003: Audit every state change and decision

**Status:** Accepted · 2025-02-24

## Context

Fraud operations and internal audit reconstruct what happened to a card from the audit trail,
including declined purchases and who changed the card's status.

## Decision

Every state change and every authorization decision adds an `AuditEvent` through `audit.record` in
the **same transaction**. The service layer records it. An event holds the time (from the injected
clock), the actor (`X-Actor`, set by the gateway or the servicing app), the action
(`<entity>.<past-tense verb>`, for example `card.closed`), the entity, and a small `details` object
with identifiers only: never a card number or token.

## Consequences

- A rollback removes the change and its event together.
- New actions follow the `<entity>.<verb>` naming and are covered by a test.
