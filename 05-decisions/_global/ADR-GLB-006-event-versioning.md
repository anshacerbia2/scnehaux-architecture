---
doc_meta:
  id: ADR-GLB-006
  title: ADR-GLB-006 Enforcing Event Versioning and Schema Evolution Contracts
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-GLB-006: Standardizing on Backward Compatibility, Centralized Schema Registries, and Dual-Field Publishing for Asynchronous Event Schemes

---

## 1. Title

Standardizing on Backward Compatibility, Centralized Schema Registries, and Dual-Field Publishing for Asynchronous Event Schemes

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Scnehaux services communicate asynchronously using publish-subscribe and event streaming paradigms. When a publisher service modifies the schema of an event payload (e.g. renaming a database-mapped field or changing data formats), downstream consumer services compiled against older schema definitions frequently fail to parse the updated payload, resulting in parsing exceptions, message consumer failure, and transaction backlogs. We need a strict compatibility contract that permits services to update schemas independently without disrupting downstream consumers.

## 4. Decision Drivers

Enforcing backward compatibility decouples service lifecycles. It eliminates the need for coordinated deployments, enabling teams to release publisher updates at any time. The dual-field publishing pattern provides a safe, incremental migration window for consumers. Centralizing verification in the Schema Registry automates governance, blocking schema violations before they reach production.

## 5. Decision

We officially establish a mandatory event schema evolution policy governed by three rules:

1.  **Backward Compatibility Default**: Every schema modification must maintain backward compatibility. Consumers compiled against version `N` must successfully parse payloads emitted under version `N+1`.
2.  **Schema Registry Verification**: All event schemas must register in the enterprise Schema Registry. CI pipelines must validate new schema drafts against registry histories to block breaking changes (e.g., removing fields, changing data types, or adding mandatory properties).
3.  **Dual-Field Publishing Pattern**: When renaming a field, publishers must write both properties concurrently (e.g., populating both `"name"` and `"full_name"`) in the payload. This dual-publishing state must remain active until all downstream consumers have transitioned to reading the new property, after which the old property is deprecated and removed in a promoted major version.
4.  **Major Version Promotion**: Breaking modifications require promoting the event namespace to a new major version (e.g., `com.scnehaux.iam.user.created.v2`).

## 6. Consequences

### Positive

- **Independent Deployments**: Teams release services autonomously without coordinate deployments.
- **Automated Validation**: Schema registry integration stops breaking modifications during the CI phase.
- **Data Integrity**: Consumer services parse payloads predictably without encountering type exceptions.

### Negative

- **Payload Duplication**: The dual-publishing pattern increases network transit bytes and database storage requirements during migrations.
- **Registry Dependency**: Introduces dependency on a Schema Registry system.

### Tradeoffs

- We trade payload storage and transit byte size (due to temporary field duplication) for deployment velocity and system stability.

### Operational Impact

- Simplifies operations by eliminating consumer crashes during deployments. Requires monitoring schema registry query rates and sync states.

### Security Impact

- Ensures that schema modifications do not bypass encryption policies. Tier 1/2 fields must remain mapped correctly under schema updates.

### Scalability Impact

- Enhances scaling capability by preventing queue backups caused by crashing consumer groups.

### Operational

- Codified in the Enterprise Event-Driven Architecture Standard (`STD-E016`).
- Implemented using JSON Schema drafts in a registry matching the CloudEvents envelope pattern.

## 7. Compliance Impact

### Related Standards

- Enterprise Event-Driven Architecture & Messaging Standard (STD-E016)
- Enterprise Data Classification, Governance & Retention Standard (STD-E017)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Coordinated Multi-Service Deployments

- **Pros**: Zero payload duplication; clean schema state transitions.
- **Cons**: Requires blocking deployments, locking release pipelines, and deploying publishers and consumers simultaneously.
- **Why Rejected**: Introduces massive release coordination friction, increases deployment risks, and violates microservice autonomy principles.

### Alternative B: Schema-less Event Payloads (Generic JSON maps)

- **Pros**: High flexibility; zero validation checks.
- **Cons**: Leads to silent data corruption, makes debugging runtime errors difficult, and forces consumers to write complex defensive code to verify field existence.
- **Why Rejected**: Fails to meet the enterprise reliability and predictability targets, shifting integration bugs to production.
