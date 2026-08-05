---
doc_meta:
  id: STD-GLB-001
  title: Enterprise API Design Standard
  owner: Architecture Review Board
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 365
  created_date: 2026-01-01
---

# STD-GLB-001: Enterprise API Design Standard

## Objective & Scope

This standard defines the mandatory design principles and HTTP protocol usage for all synchronous REST APIs within the Scnehaux enterprise to ensure a consistent developer experience and operational reliability.

## Design Principles

- REST APIs must be predictable, stateless, and deeply consistent across all domains.
- We prioritize developer experience and explicit contracts over clever optimization.

## Normative Rules

### API Contracts & Envelope

- APIs MUST use JSON over HTTP.
- Responses SHOULD NOT use custom envelopes for standard data (return direct arrays/objects) to minimize payload bloat.
- Error responses MUST conform to **RFC 7807 (Problem Details for HTTP APIs)**.

### Versioning

- APIs MUST be versioned at the URL path level (e.g., `/api/v1/users`).
- Header-based versioning is PROHIBITED due to complexity in CDN caching and network edge routing.

### Pagination

- List endpoints returning unbounded data MUST be paginated.
- Cursor-based pagination (e.g., `?after=xyz&limit=100`) is MANDATORY for all core entities. Offset-based pagination (`?offset=100`) is strictly PROHIBITED for large datasets due to database scanning penalties.

### Security & Authentication

- All requests MUST be authenticated at the API Gateway using JWT via the `Authorization: Bearer <token>` header.
- Internal machine-to-machine calls MUST use mTLS or an internal service mesh token.

### Rate Limiting

All public-facing APIs MUST return standard rate-limit headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Exceptions

Legacy systems currently running SOAP or XML are exempt until their scheduled sunset dates.

## Enforcement Mechanism

API schema validation via the API Gateway and CI/CD spectral linters.
