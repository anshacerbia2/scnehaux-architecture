# Architectural Decision Records (ADR) Index

This is the authoritative index of all Architectural Decision Records within the Scnehaux enterprise.

| ID | Title | Type | Status | Created | Expiry Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [ADR-GLB-001](_global/ADR-GLB-001-modular-monolith.md) | ADR-GLB-001 Enterprise Adoption of Modular Monolith Architecture | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-002](_global/ADR-GLB-002-postgresql-rls.md) | ADR-GLB-002 Enterprise PostgreSQL Row-Level Security for Isolation | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-004](_global/ADR-GLB-004-atlas-schema.md) | ADR-GLB-004 Atlas Schema Governance for Deterministic Data Migrations | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-005](_global/ADR-GLB-005-load-shedding.md) | ADR-GLB-005 Adopting Load Shedding and Resilience Invariants | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-006](_global/ADR-GLB-006-event-versioning.md) | ADR-GLB-006 Enforcing Event Versioning and Schema Evolution Contracts | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-007](_global/ADR-GLB-007-ddd-boundaries.md) | ADR-GLB-007 Standardizing Domain-Driven Design Boundaries and Data Ownership | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-008](_global/ADR-GLB-008-go-project-structure.md) | ADR-GLB-008 Go Project Structure and Layer Enforcement | foundational | accepted | 2026-08-11 | N/A |
| [ADR-GLB-009](_global/ADR-GLB-009-repository-topology.md) | Repository Boundaries Follow Change, Release, Security, and Ownership Cohesion | foundational | accepted | 2026-08-12 | N/A |
| [ADR-GLB-010](_global/ADR-GLB-010-application-mechanics-in-process.md) | Application Mechanics Stay In-Process; Network Mechanics Move to Infrastructure | foundational | proposed | 2026-08-12 | N/A |
| [ADR-GLB-012](_global/ADR-GLB-012-separate-ai-knowledge-and-product-authority.md) | ADR-GLB-012 Separate Product, Knowledge, and AI Execution Authority | foundational | accepted | 2026-08-23 | N/A |
| [ADR-GLB-013](_global/ADR-GLB-013-work-workflow-job-schedule-boundaries.md) | ADR-GLB-013 Separate Work, Workflow, Job, Schedule, Worker, and Queue Boundaries | foundational | accepted | 2026-08-23 | N/A |
| [ADR-GLB-014](_global/ADR-GLB-014-background-worker-network-boundary.md) | ADR-GLB-014 Minimize Inbound Network Surface for Background Workers | foundational | accepted | 2026-08-23 | N/A |
| [ADR-GLB-015](_global/ADR-GLB-015-separate-model-inference-and-agent-runtime.md) | ADR-GLB-015 Separate Model & Inference from Agent Runtime | foundational | accepted | 2026-08-23 | N/A |
| [ADR-GLB-016](_global/ADR-GLB-016-durable-messaging-substrate-profiles.md) | ADR-GLB-016 Separate Transactional Publication from Durable Messaging Substrate Selection | foundational | accepted | 2026-08-24 | N/A |
| [ADR-GLB-017](_global/ADR-GLB-017-durable-scheduling-profiled-dispatch.md) | ADR-GLB-017 Preserve Enterprise Durable Scheduling Boundary with Profiled Dispatch | foundational | accepted | 2026-08-24 | N/A |
| [ADR-GLB-018](_global/ADR-GLB-018-per-consumer-delivery-from-one-outbox.md) | ADR-GLB-018 Deliver One Outbox to Several Named Consumers, Each with Its Own Outcome | foundational | accepted | 2026-10-02 | N/A |
| [ADR-GLB-019](_global/ADR-GLB-019-data-changes-in-migrations.md) | ADR-GLB-019 A Migration Changes Existing Data Only as a Bounded Data Migration, and Never Seeds | foundational | accepted | 2026-10-03 | N/A |
| [ADR-GLB-FE-001](_global/ADR-GLB-FE-001-react-ecosystem.md) | ADR-GLB-FE-001 Standardization on React and Framework Paved Road | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-002](_global/ADR-GLB-FE-002-build-toolchain.md) | ADR-GLB-FE-002 Standardization on Next-Generation Build Toolchains | foundational | superseded | 2026-01-01 | N/A |
| [ADR-GLB-FE-003](_global/ADR-GLB-FE-003-meta-framework.md) | ADR-GLB-FE-003 Standardization on Enterprise Meta-Framework | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-004](_global/ADR-GLB-FE-004-module-federation.md) | ADR-GLB-FE-004 Standardizing Conditional MFE on Module Federation | foundational | superseded | 2026-01-01 | N/A |
| [ADR-GLB-FE-005](_global/ADR-GLB-FE-005-state-management.md) | ADR-GLB-FE-005 Dual-Engine State Management (Zustand & TanStack Query) | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-006](_global/ADR-GLB-FE-006-zero-runtime-css.md) | ADR-GLB-FE-006 Zero-Runtime CSS and Utility-First Compilation | foundational | superseded | 2026-01-01 | N/A |
| [ADR-GLB-FE-007](_global/ADR-GLB-FE-007-nextgen-testing-toolchain.md) | ADR-GLB-FE-007 Next-Generation Frontend Testing Toolchain | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-008](_global/ADR-GLB-FE-008-graphql-protocol.md) | ADR-GLB-FE-008 Standardization on GraphQL as Primary Data Protocol | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-009](_global/ADR-GLB-FE-009-realtime-communication.md) | ADR-GLB-FE-009 Real-Time Communication and Push Strategy | foundational | accepted | 2026-01-01 | N/A |
| [ADR-GLB-FE-010](_global/ADR-GLB-FE-010-evidence-based-frontend-contracts.md) | Evidence-Based Frontend Contracts and UI Platform Alignment | conflict_resolution | accepted | 2026-09-28 | N/A |
| [ADR-GLB-FE-011](_global/ADR-GLB-FE-011-rspack-based-federated-toolchains.md) | Rspack-Based Toolchains for Federated Applications | replacement | accepted | 2026-09-28 | N/A |
| [ADR-GLB-FE-012](_global/ADR-GLB-FE-012-module-federation-runtime-contract.md) | Module Federation Runtime Contract | replacement | accepted | 2026-09-28 | N/A |
| [ADR-GLB-FE-013](_global/ADR-GLB-FE-013-static-css-output-and-token-bound-styling.md) | Static CSS Output and Token-Bound Styling | replacement | accepted | 2026-09-28 | N/A |
| [ADR-IAM-001](identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) | Adopt Keycloak as the Scnehaux Identity Protocol and Authentication Kernel | foundational | accepted | 2026-08-06 | N/A |
| [ADR-IAM-002](identity-access-platform/ADR-IAM-002-token-signing.md) | ADR-IAM-002 Token Signing Algorithm and Key Lifecycle Management | foundational | accepted | 2026-01-01 | N/A |
| [ADR-IAM-003](identity-access-platform/ADR-IAM-003-client-registration-ownership.md) | Client Registration Ownership and the Developer Console's Authority | foundational | accepted | 2026-10-01 | N/A |
| [ADR-IAM-004](identity-access-platform/ADR-IAM-004-authentication-assurance-and-step-up.md) | Authentication Assurance Levels and Step-Up | foundational | accepted | 2026-10-03 | N/A |
| [ADR-IAM-005](identity-access-platform/ADR-IAM-005-account-recovery-and-guessing-limits.md) | Account Recovery and Guessing Limits | foundational | accepted | 2026-10-04 | N/A |
| [ADR-IAM-006](identity-access-platform/ADR-IAM-006-tenant-context-in-tokens.md) | Tenant Context in Tokens, Selected per Sign-In | foundational | accepted | 2026-10-04 | N/A |
| [ADR-IAM-007](identity-access-platform/ADR-IAM-007-account-security-notifications.md) | Account Security Notifications, Decided by Identity and Delivered by Notification | foundational | accepted | 2026-10-06 | N/A |
| [ADR-ORG-001](organization-tenancy-platform/ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) | Separate Organization Authority from Identity and Use Keycloak as a Projection Target | foundational | accepted | 2026-08-06 | N/A |
| [ADR-ORG-002](organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md) | Eligible Provider Authority, Activated for a Bounded Time and Approved by Another Provider | foundational | accepted | 2026-10-02 | N/A |
| [ADR-ORG-003](organization-tenancy-platform/ADR-ORG-003-tenant-administration-grant.md) | Tenant Administration Is a Recorded Grant, Checked with Current Membership | foundational | accepted | 2026-10-04 | N/A |
| [ADR-SCH-002](scheduling-platform/ADR-SCH-002-postgresql-profiled-durable-dispatch.md) | ADR-SCH-002 PostgreSQL Temporal Authority and Replaceable Durable Dispatch | implementation | accepted | 2026-08-24 | N/A |
| [ADR-UIP-BLD-001](ui-platform/ADR-UIP-BLD-001-deferred-minification.md) | Deferred Minification | foundational | accepted | 2026-01-01 | N/A |
| [ADR-UIP-BLD-002](ui-platform/ADR-UIP-BLD-002-tsdown-package-build.md) | tsdown Replaces tsup as the UI Platform Package Builder | foundational | accepted | 2026-10-03 | N/A |
| [ADR-UIP-PLT-001](ui-platform/ADR-UIP-PLT-001-verifiable-platform-contract.md) | Verifiable UI Platform Package and Release Contract | conflict_resolution | accepted | 2026-09-28 | N/A |
| [ADR-UIP-SEC-001](ui-platform/ADR-UIP-SEC-001-supply-chain-evidence.md) | Supply-Chain Evidence with CycloneDX SBOMs and SLSA Build L2 Attestations | foundational | accepted | 2026-10-02 | N/A |
| [ADR-UIP-TKN-001](ui-platform/ADR-UIP-TKN-001-three-tier-isolation-architecture.md) | ADR-UIP-TKN-001 Three-Tier Design Token Isolation Architecture | foundational | accepted | 2026-01-01 | N/A |
| [ADR-UIP-TKN-002](ui-platform/ADR-UIP-TKN-002-oklch-and-dual-engine-alpha.md) | ADR-UIP-TKN-002 OKLCH Gamut and Dual-Engine Alpha Blending Architecture | foundational | accepted | 2026-01-01 | N/A |
| [ADR-UIP-TKN-003](ui-platform/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md) | ADR-UIP-TKN-003 Token Taxonomy & Naming Convention | foundational | accepted | 2026-01-01 | N/A |
| [ADR-UIP-WKS-001](ui-platform/ADR-UIP-WKS-001-storybook-component-workshop.md) | Storybook Component Workshop with Story Tests and Chromatic Visual Review | foundational | accepted | 2026-10-01 | N/A |
