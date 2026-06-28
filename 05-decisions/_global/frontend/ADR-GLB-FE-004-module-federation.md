---
doc_meta:
  id: ADR-GLB-FE-004
  title: ADR-GLB-FE-004 Standardizing Conditional MFE on Module Federation
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-004: Standardizing Conditional MFE on Module Federation

---

## 1. Title
Standardizing Conditional MFE on Module Federation

## 2. Status
| Date | Status | ADR Type | Reviewers | Approver |
|---|---|---|---|---|
| 2026-05-01 | accepted | foundational | Architecture Review Board | Principal Frontend Architect |


## 3. Context
As defined in **STD-GLB-FE-007 (Micro-frontend)**, large-scale applications exceeding 3 independent squads are authorized to break the Monolithic SPA default and adopt a Micro-Frontend (MFE) architecture to regain deployment autonomy. Without a standard integration methodology, teams attempt fragile Iframe bridges or heavy runtime composition wrappers.

## 4. Decision Drivers
We require a standardized technical mechanism to dynamically load remote dependencies at runtime without sacrificing the unified SPA user experience or inflating network payloads with duplicated vendor libraries. Module Federation natively solves this at the bundler level.

## 5. Decision
For all frontend applications authorized to utilize an MFE architecture, we mandate **Webpack/Rsbuild Module Federation** as the exclusive integration protocol. Cross-application communication will happen exclusively via typed React Context boundaries or Custom Events.

## 6. Consequences
- **Positive**: Zero-coordinated deployments, shared vendor chunks intelligently deduplicated, and a native SPA user experience.
- **Negative**: Configuring shared dependency maps in bundlers introduces steep learning curves for feature teams.

### Negative / Risks
- **Runtime Brittleness**: If a remote pushes a breaking contract change, the host application will crash unless strictly protected by Error Boundaries.
- **Dependency Drift**: Remotes might upgrade a shared singleton dependency (like React) asynchronously, causing version mismatch crashes at runtime.

### Operational
- Critical dependencies (e.g., `react`, `react-dom`) must be configured as strict singletons via the federation plugin.
- Any runtime failure to download a remote entrypoint must be caught at the route boundary using isolated React Error Boundaries.

## 7. Compliance Impact
### Related Standards
- [STD-GLB-FE-007 (Micro-Frontend)](../../../02-standards/_global/frontend/STD-GLB-FE-007-micro-frontend.md) - This standard establishes the normative rules and exact threshold conditions for when to adopt Module Federation.

### Compliance Status
Compliant.

### Required Waivers
None.

## 8. Alternatives Considered
- **Iframes**: Rejected. They cause severe accessibility issues, trap focus/modals, hinder SEO, and make sharing state extremely cumbersome and insecure.
- **Single-SPA**: Rejected. Requires invasive wrappers around every application and enforces a heavy, centralized orchestration layer.
- **Nginx Route Redirection**: Rejected. Redirecting forces a full page reload, destroying the SPA feel and resetting client state.
