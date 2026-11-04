---
doc_meta:
  id: ADR-PRV-004
  title: Provisioning Acts as Its Own Workload, with Narrow Cloud Roles Organization Control Never Holds
  adr_type: foundational
  status: proposed
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-004: Provisioning Acts as Its Own Workload, with Narrow Cloud Roles Organization Control Never Holds

## 1. Title

The provisioning service authenticates to Organization Control as its own registered workload, with its own key. It acts on the cloud through short-lived roles that are split by task and limited to resources tagged as provisioning's. Organization Control holds no infrastructure credential, and the provisioning service holds no person's token.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                             | Approver                         |
| :--------- | :------- | :----------- | :-------------------------------------------------------------------- | :------------------------------- |
| 2026-11-04 | proposed | foundational | Architecture, Core Platform, Platform Engineering, Security, Identity | Architecture Authority (pending) |

## 3. Context

`ADR-ORG-001 §5.11` already decides how the provisioning system reports: one workload client registered through identity-control with an owner, a client-credentials token obtained with a signed client assertion, admitted by a reporter registry row for `provisioning`, and reaching the three report routes and nothing else. That decision was taken before the system was designed, and it is marked "not yet built" in `SAD-004 §8.1`.

The design adds four things a reporter does not do today:

- it reads the outstanding requests (`ADR-PRV-001 §5.1`);
- it receives Organization Control's command event (`ADR-PRV-001 §5.2`);
- it reports progress (`ADR-PRV-001 §5.4`, Phase 2);
- it enforces a provider scope of its own, `provider:provisioning` (`ADR-PRV-002 §5.3`).

It also holds what no other service in the estate holds: credentials that create and delete cloud databases and keys. A leak of them affects every dedicated Tenant.

## 4. Decision Drivers

- Least privilege for the service, as for any process [`ADR-ORG-001` R14, R15].
- Organization Control must not be able to build or delete infrastructure, even if it is compromised.
- No long-lived cloud secret in a file or an environment variable.
- A planning step that cannot change anything.
- Development uses the same identity path as production (`STD-GLB-009` rule 13).

## 5. Decision

### 5.1 Toward Organization Control: One Registered Workload

- **One workload client, `provisioning-control`**, registered through identity-control's workload registration with Platform Engineering as owner. It authenticates with a client assertion signed by its own key (RSA, at least 3072 bits), exactly as `ADR-ORG-001 §5.11` describes. Its private key is in the environment's secret store, never in the repository or the image.
- **One reporter row, `provisioning`.** Its reach widens from three routes to five, and only these:

| Route                                                   | Since    | Purpose                                        |
| :------------------------------------------------------ | :------- | :--------------------------------------------- |
| `POST /v1/provisioning/realized`                        | existing | report an outcome                              |
| `POST /v1/provisioning/failed`                          | existing | report an outcome, with a cause                |
| `POST /v1/offboardings/{offboarding_id}/deprovisioning` | existing | report a deprovisioning outcome                |
| `GET /v1/provisioning/requests`                         | Phase 1  | read outstanding requests (`ADR-PRV-001 §5.1`) |
| `POST /v1/provisioning/progress`                        | Phase 2  | report stage and `expected_by`                 |

- **Delivery the other way uses Organization Control's identity.** The command event reaches the service's acceptance endpoint with Organization Control's workload token (`ADR-GLB-018 §5.4`). The service accepts it only from Organization Control's `principal_id` and only for the provisioning target it is registered as.
- **Provider scope enforced here.** `provider:provisioning` grants are recorded by Organization Control and projected to this service, which reads them for each approval or panel action (`ADR-PRV-002 §5.3`). A person's token reaches the service only through the panel's back end, with `aud` naming this service.

### 5.2 Toward the Cloud: Short-Lived Roles, Split by Task

- **No access keys.** The service obtains short-lived credentials from its runtime's workload identity: a Kubernetes service account bound to an AWS IAM role. `STD-GLB-009` §Security & Access Governance already forbids permanent credentials.
- **Three roles, each assumed only for its task:**

| Role                   | Used for                         | Can                                                                                                  | Cannot                                                                |
| :--------------------- | :------------------------------- | :--------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| `provisioning-plan`    | `tofu plan`, drift check         | read the resources the modules manage; read and lock state                                           | create, change or delete anything                                     |
| `provisioning-apply`   | `tofu apply` of an approved plan | create and change resources of the module types, only with the tag `managed-by=provisioning-control` | touch untagged resources; change IAM; read secrets other than its own |
| `provisioning-destroy` | deprovisioning (`ADR-PRV-005`)   | delete tagged resources; schedule key deletion                                                       | delete untagged resources; cancel a legal hold                        |

- **A permission boundary** caps all three, so no change to a role's policy can exceed it. Changing the boundary is an infrastructure change through a pull request, approved by the Information Security Officer.
- **Per-Tenant key policies** let the Tenant's application role use the key for encryption and decryption, and let `provisioning-destroy` schedule its deletion. The provisioning roles cannot decrypt Tenant data.
- **Every cloud call is logged** by the cloud's audit trail, and each apply is linked to its request and approval by a tag carrying the `provisioning_request_id`.

### 5.3 Organization Control Holds None of It

Organization Control's deployment has no cloud role that can create, change or delete a Tenant's resources, and no access to the state bucket. A test in the service's infrastructure module asserts that Organization Control's role has no permission on resources tagged `managed-by=provisioning-control`.

### 5.4 Development

The development service authenticates to Organization Control as a development workload registered the same way, with its own key, as the stand-in scripts do today (`ADR-ORG-001 §5.11`). In Phase 1 it needs no cloud role, because the pooled path writes only to its own database. From Phase 2 its local stand-ins (`ADR-PRV-003 §5.4`) accept a fixed local credential that works for nothing else; this is a stated difference.

## 6. Consequences

### Positive

- A compromised Organization Control cannot build or delete infrastructure.
- A compromised planning step cannot change anything.
- The service cannot read Tenant data with its own roles.
- Revoking the service at Organization Control is one change to a record (`ADR-ORG-001 §5.11`).

### Negative

- Three cloud roles, a boundary and per-Tenant key policies to maintain and test.
- The reporter's reach grows from three routes to five; each addition is a change to Organization Control's route table and its tests.

### Operational

- The workload's owner reviews its reports and reads, as for every reporter (`ADR-ORG-001 §5.11`).
- Role and boundary changes are reviewed in the 90-day infrastructure access review (`ISMS-005` T43).

## 7. Compliance Impact

### Related Standards and Artifacts

- `ADR-ORG-001 §5.11` — reporter workloads, extended here.
- `ADR-ORG-002` — provider grants, for `provider:provisioning`.
- `ADR-IAM-003 §5.8` — workload registration with an owner.
- `STD-GLB-009` §Security & Access Governance — no permanent credentials.
- `ISMS-005` — A.5.15, A.8.2, A.8.18.

### Compliance Status

Proposed. Extends `ADR-ORG-001 §5.11` in a compatible way: the three existing routes keep their meaning.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Provisioning as a Module of Organization Control

**Benefits:** one deployment, no new workload, no network contract.

**Rejected because:** Organization Control would hold cloud credentials that create and delete databases and keys, and a fault in any of its modules would reach them. `ADR-ORG-001 §5.8` allows extraction on evidence of security isolation; this is that evidence.

### Alternative B — One Cloud Role for Everything

**Benefits:** simpler to set up.

**Rejected because:** planning and drift checks run daily for every Tenant and need only read access; giving them delete rights widens every run's damage.

### Alternative C — A Person's Provider Token for Reports

**Benefits:** works today.

**Rejected by `ADR-ORG-001` Alternative J:** a machine would use a person's privilege.

### Alternative D — Long-Lived Cloud Access Keys in the Secret Store

**Benefits:** works on any host, including the development server.

**Rejected because:** a leaked key works until someone notices; `STD-GLB-009` forbids permanent credentials.

## 9. References

The normative sources for workload authentication, least privilege and unique identification are cited in `ADR-ORG-001 §9` ([R10]–[R15]) and are not repeated here.
