---
doc_meta:
  id: ADR-ORG-004
  title: Bulk Membership Actions Previewed by the Server, and Revocation Shown by Its Evidence
  adr_type: foundational
  status: accepted
  created: 2026-10-07
  created_date: 2026-10-07
  created_by: Core Platform Team
---

# ADR-ORG-004: Bulk Membership Actions Previewed by the Server, and Revocation Shown by Its Evidence

## 1. Title

Bulk Membership Actions Previewed by the Server, and Revocation Shown by Its Evidence.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-07 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Two obligations reach the Organization Control API from its administrative experience, and
neither is served.

**Bulk actions.** `SAD-004 §8.3` requires that "bulk operations validate each item independently
and return per-item outcome". `TDD-organization-experience-001` §Bulk Operations specifies what the
operator sees:

- a preview with each item's current state, its resulting state and any refusal;
- an execution that commits the set the operator was shown;
- an outcome per item, reported as succeeded, failed or not attempted;
- a resubmission of the failed subset only.

The API has one Membership command per request and no preview.

**Revocation.** `TDD-organization-control-002` is explicit that a transition's acceptance is not
its enforcement:

- the response carries `accepted_at` and "MUST NOT be read as enforced";
- the enforcement interval is the projection propagation, budgeted under 10 s, plus the
  remaining access token lifetime.

`TDD-organization-experience-001` §Presenting Revocation Honestly asks for four states: accepted,
propagating, enforced, over budget. The evidence for them exists but nothing reads it:

- the outbox records when each event was published;
- `platform.delivery_receipt` records, per consumer, `transport_accepted` or `consumer_applied`
  (`foundation-platform`);
- dead letters record what was not delivered.

## 4. Decision Drivers

- **A preview must be the operation's own validation, not a guess beside it.**
  - AIP-163: a validate-only request "**must** perform permission checks and any other validation
    that would be performed on a "live" request" [R2].
  - Kubernetes: "Authorization for dry-run and non-dry-run requests is identical" [R5].
- **What the operator was shown is what is committed.**
  - AIP-154: a mismatched etag "**must**" be refused [R3].
  - RFC 9110: a server "MUST NOT perform the requested method if the condition evaluates to false"
    [R6].
- **Partial failure is the expected outcome of a large action.**
  - AIP-193: failing a whole request for one entry is "hostile to users" [R4].
  - SCIM: "The service provider MUST continue performing as many changes as possible and
    disregard partial failures", with each operation's status the one "that would have been
    returned if a single HTTP request would have been used" [R1].
- **Accepted, delivered and enforced are three facts.**
  - RFC 9110 §15.3.3: an accepted request "might or might not eventually be acted upon" [R6].
  - RFC 8936: an acknowledgement means "delivery has succeeded and redelivery is no longer
    required" [R8]. Delivery is not enforcement.
  - Vendors publish the gap as a window, among them:
    - Entra: "latency of up to 15 minutes might be observed" [R9];
    - Google Cloud: "eventually consistent", "Typically 2 minutes, potentially 7 minutes or
      longer" [R10];
    - Google Workspace's console warns of "an expected delay" [R11].

## 5. Decision

### 5.1 A Bulk Action Is a Batch the Server Previews, Then Executes

A Tenant administrator's bulk action on Memberships (suspend, restore or revoke) is a batch
resource of the Organization Control API, in two steps.

**The preview.** `POST /v1/membership-batches` names the action and up to 500 Membership
identifiers, with the reason the action requires (a revocation always requires one).

| Part       | What the server does                                                                                                    |
| :--------- | :---------------------------------------------------------------------------------------------------------------------- |
| Validation | Each item runs through the single command's own validation, permissions included, and nothing is written (AIP-163 [R2]) |
| Per item   | The current status, the version read, and either the resulting status or the refusal the single command would return    |
| Totals     | The count that would change and the count that would not                                                                |
| Record     | The batch is stored with each item's version, and expires after a bounded time                                          |

**The execution.** `POST /v1/membership-batches/{id}/execute`, with an `Idempotency-Key`, which
it requires as every command does (`STD-GLB-001` 1.4.0), commits the preview:

- **Each item is its own transaction**, held to the version the preview read. An item changed
  since then fails with the single command's `409 version-conflict` and is not applied
  ([R3][R6]). The operator commits the set they were shown, never the set as it stands at
  submit time.
- **Each item has one outcome:**
  - `succeeded`, with its `accepted_at` and the event it published;
  - `failed`, with the problem the single command would return [R1];
  - `not_attempted`: refused at preview, past the batch's error allowance (SCIM's
    `failOnErrors` [R1]), or past its expiry.
- **The batch never reports one aggregate success.** The response carries every item's
  outcome, as SCIM's does [R1].
- **The failed subset** is resubmitted as a new preview of those items, which names the batch it
  continues and keeps its correlation identifier.

**Synchronous, within a bound.** The batch is bounded at 500 items, as SCIM requires a declared
maximum [R1]. A preview naming more is refused with `413 Payload Too Large`, and the refusal names the
limit, as SCIM requires of an exceeded maximum [R1] and RFC 9110 defines the status [R6]
(2026-10-07; until foundation-platform v0.4.1 the problem registry had no 413 type, and the
refusal was a `400`). The execute request returns when every item has an outcome. AIP-234 would make a
synchronous batch atomic [R4]. Here the per-item outcome is carried in the body, as SCIM and
Graph do [R1][R7], and the HTTP status of the execute request reports only the request.

### 5.2 Revocation Is Shown by Its Evidence

A Membership transition's state is derived from recorded evidence, never from the response alone.

| State         | Evidence                                                                                                                                                                                        |
| :------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accepted`    | The transition committed. The response's `accepted_at`, and nothing else yet                                                                                                                    |
| `propagating` | Published, and not yet applied by every consumer subscribed to the event                                                                                                                        |
| `enforced`    | Every subscribed consumer recorded `consumer_applied` for the event                                                                                                                             |
| `over_budget` | Not enforced once the propagation budget (`TDD-organization-control-002` §Enforcement Budget, under 10 s) has elapsed since `accepted_at`, or a subscribed consumer's delivery is dead-lettered |

**Why `consumer_applied` is enforcement.**

- **The resource checks current state.** Every resource accepting a Tenant context refuses a
  token unless its own projection shows the Membership and the Tenant active (`ADR-IAM-006
§5.4`). Once it has applied the event, the next request is refused whatever the token's
  remaining lifetime.
- **New tokens stop at the kernel.** identity-control removes the Principal from the Keycloak
  Organization when it applies the event.
- **Delivery is not enough.** `transport_accepted` is delivery, which RFC 8936 and the Shared
  Signals Framework treat as distinct from acting on an event [R8][R12]. It counts as
  propagating.

**The read.**

- The transition response names its event.
- `GET /v1/memberships/{id}/enforcement` returns:
  - the latest transition's evidence, per subscribed consumer;
  - the budget;
  - the derived state.

  It is Tenant-scoped under the same row security as the Membership.

- **A provider reads it too (2026-10-09)**, at
  `GET /v1/tenants/{tenant_id}/memberships/{membership_id}/enforcement`, with
  `X-Administrative-Reason`, and gets the same document. An operator answering an over-budget
  revocation otherwise asks the Tenant or reads the tables.
  - **The Tenant is in the path, not inferred from the Membership.** The read records the access
    with the provider's reason and that Tenant before it reads, so the Tenant's administrator sees it
    in the privileged-access record (`ADR-ORG-002 §5.6`). A route keyed on the Membership alone would
    first read it across Tenants, and record no Tenant.
  - **It reads under that Tenant's row security**, as the Tenant-scoped read does, with no new
    grant. A Membership of another Tenant is `404` whatever the path carries: the server "did not
    find a current representation for the target resource" [R6].

- **`over_budget` carries an escalation path** in the administrative experience, as RFC 9110 asks
  a status monitor to estimate when a request will be fulfilled [R6].

### 5.3 An Interrupted Execution Is Resumed Under a Lease

The execution runs inside its HTTP request. A request that ends mid-batch, by a crash or by the
request timeout, leaves the batch `executing`: some items have an outcome and the rest have none.
Without a resume, the batch stays that way for ever, and every retry is refused as in progress.

**The lease.**

- The transaction that starts the execution gives the request a lease: a fresh `lease_id` and a
  `heartbeat_at`.
- Every item's transaction begins by renewing it, and only where the row still holds this
  request's `lease_id`.
- The lease lasts 30 seconds. A request's timeout must be shorter, and the service refuses to
  start otherwise. A heartbeat 30 seconds old therefore belongs to a request that has ended.
- Gray and Cheriton define a lease as "a contract that gives its holder specified rights over
  property for a limited period of time" [R13]. They add that
  "Non-Byzantine failures affect performance, not correctness" [R13]. A dead request delays the
  batch by one lease, and never blocks it.

**The resume.** An execute on an `executing` batch:

- with a live lease is refused `409`, and writes nothing. The first request may still be running;
- with a stale lease takes it over, in one transaction under the batch's row lock, and records
  who resumed it and when. It then runs only the items without an outcome, each still held to the
  version its preview read. The error allowance is the one fixed when execution began;
- may carry the key of the request that began the execution. That key's claim was committed and
  never completed, so the resume adopts it. A new key resumes the batch too.

**The fence.** The `lease_id` is a fencing token.

- A request whose lease was taken over finds no row to renew, rolls back the item it was on, and
  stops. The final transaction that marks the batch `executed` is fenced the same way.
- Each item's transition and its outcome commit together. An item with an outcome is skipped, so
  no item is applied twice.
- Kleppmann: "the storage server remembers that it has already processed a write with a higher
  token number (34), and so it rejects the request with token 33" [R14]. He warns that a check of
  the lease "just before writing back to storage" does not fix the problem [R14]. Here the fence
  is the first statement of the write's own transaction, and its row lock is held until the item
  commits, so a takeover waits for that item to finish.
- **The token is compared for equality, not order.** Kleppmann's storage compares each write's
  token with the highest it has seen, so his tokens must strictly increase [R14]. Here the lease
  is held on the row the fence updates, so the row knows the one current lease, and any other
  token is stale.

### 5.4 An Expired Preview Is Purged

- A batch still `previewed` whose `expires_at` passed more than 24 hours ago is deleted, with
  its items, in one transaction. The day lets an operator who left the screen open read the
  preview as `expired` rather than as absent.
- A batch that began executing is never purged. It is the record of what a bulk action did.
- **The purge runs as the migration role, under row security.**
  - No runtime role holds `DELETE` on either table. The daily maintenance stage, which already
    runs retention, runs the purge.
  - Both tables are under `FORCE ROW LEVEL SECURITY` (`ADR-GLB-002`). PostgreSQL says "Table
    owners normally bypass row security as well, though a table owner can choose to be subject to
    row security with ALTER TABLE ... FORCE ROW LEVEL SECURITY" [R15]. The migration role, the
    tables' owner, is bound by their policies too.
  - Each table has one policy for that role, `FOR ALL`, `USING` an expired preview and
    `WITH CHECK (false)`.
  - `USING` admits the delete and the read it needs: "the appropriate SELECT or ALL policies will
    be applied in addition to the DELETE policies" [R15].
  - `WITH CHECK (false)` refuses every insert and update: "An error will be thrown if the
    expression evaluates to false or null" [R15]. The role can delete an expired preview and
    rewrite no batch.

## 6. Consequences

### Positive

- One code path validates the single command, the preview and the execution. A preview cannot
  promise what the command would refuse.
- An operator sees which items changed, which failed and why, and which were never tried, and
  recovers by resubmitting the failed items alone.
- A revocation is never presented as enforced on the API's answer. The operator sees the
  evidence and the budget it is measured against.

### Negative

- **Batches are a resource with storage and expiry**, and cost more than a client loop. A client
  loop cannot make the preview binding, or report a not-attempted item, from evidence the server
  holds.
- **"Enforced" depends on every consumer recording `consumer_applied`.** A consumer that records
  only `transport_accepted` keeps its revocations propagating until it does.
- **A synchronous batch of 500 items holds one request open** for the time 500 transactions take.
- **A resume waits out the lease.** After a request ends, the batch cannot continue for up to 30
  seconds.

### Operational

- Batches past their expiry are refused at execution, and purged a day later by the maintenance
  stage (§5.4).
- A batch left `executing` is finished by the next execute past its lease (§5.3). Its view names
  who resumed it and when.
- Over-budget revocations alert through the dead-letter and frontier signals, and from 2026-10-09
  through the age of each consumer's oldest unapplied priority-lane delivery
  (`TDD-organization-control-002` 1.15.0 §Operational Notes). The per-Membership read adds no
  signal.

## 7. Compliance Impact

### Related Standards

- `SAD-004 §8.3`: per-item validation and outcome, realized.
- `STD-GLB-001` 1.3.0: the batch's items are bounded and the resource is versioned under `/v1/`.
- `STD-GLB-001` 1.4.0: the preview and the execution are commands, and require an
  `Idempotency-Key`.
- [ADR-GLB-002](../_global/ADR-GLB-002-postgresql-rls.md): `FORCE ROW LEVEL SECURITY`, which
  binds the purge to its policy.
- [ADR-IAM-006](../identity-access-platform/ADR-IAM-006-tenant-context-in-tokens.md) §5.4: the
  current-state check that makes `consumer_applied` enforcement.
- `TDD-organization-control-002`, `TDD-organization-experience-001` change to implement it.
  `TDD-organization-control-002` 1.13.0 implements §5.3 and §5.4.

### Compliance Status

Compliant once the batch resource and the enforcement read are served, and the administrative
experience presents both.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — The Experience Fans Out Single Commands

**Benefits:** no new API.

**Rejected because:**

- A preview computed in the browser is not the command's validation [R2][R5]. It can show a
  change the command will refuse.
- "Not attempted" would be the browser's bookkeeping rather than the server's record.
- `SAD-004 §8.3` places per-item validation and outcome in the API.

### Alternative B — An Atomic Batch

**Benefits:** one outcome, no partial state. AIP-234 requires it of a synchronous batch [R4].

**Rejected because:**

- One stale or refused item would undo every other. AIP-193 calls that "hostile to users" in
  bulk operations [R4], and SCIM's default is to continue past partial failures [R1].

### Alternative C — An Asynchronous Long-Running Operation

**Benefits:** AIP-234's form for partial success [R4], with no request held open.

**Deferred because:**

- A bound of 500 items completes within one request.
- The batch resource is already the status monitor RFC 9110 describes [R6]; making execution
  asynchronous later changes the response code, not the resource.

### Alternative D — Show Revocation as Done at `202`

**Rejected because:** acceptance is not enforcement in this design or in any source above
[R6][R8][R9][R10]. It is the failure `TDD-organization-experience-001` exists to prevent.

### Alternative E — Leave an Interrupted Batch `executing`

**Rejected because:** the items without an outcome could never be attempted, and the operator
could not resubmit them as failed. A lease bounds the wait to 30 seconds [R13].

### Alternative F — Resume Without a Fence

**Rejected because:** a request that was only slow, not dead, would keep writing after the takeover,
and two requests would apply the same items. Expiry alone does not stop it [R14].

## 9. References

### Normative

- **[R1]** IETF RFC 7644, _System for Cross-domain Identity Management: Protocol_, September 2015.
  <https://www.rfc-editor.org/rfc/rfc7644>.
  - §3.7: "The service provider MUST continue performing as many changes as possible and
    disregard partial failures. The client MAY override this behavior by specifying a value for
    the "failOnErrors" attribute."
  - §3.7.3: "The service provider response MUST include the result of all processed operations
    ... The status attribute MUST include the code attribute that holds the HTTP response code
    that would have been returned if a single HTTP request would have been used."
  - §3.7.4: "The service provider MUST define the maximum number of operations and maximum
    payload size a client may send in a single request." / "If either limit is exceeded, the
    service provider MUST return HTTP response code 413 (Payload Too Large). The returned response
    MUST specify the limit exceeded in the body of the error response."
- **[R6]** IETF RFC 9110, _HTTP Semantics_, June 2022. <https://www.rfc-editor.org/rfc/rfc9110>.
  - §15.5.14: the 413 (Content Too Large) status code "indicates that the server is refusing to
    process a request because the request content is larger than the server is willing or able to
    process."
  - §13.1.1: "An origin server that evaluates an If-Match condition MUST NOT perform the
    requested method if the condition evaluates to false."
  - §15.5.5: "The 404 (Not Found) status code indicates that the origin server did not find a
    current representation for the target resource or is not willing to disclose that one exists."
  - §15.3.3: "the request has been accepted for processing, but the processing has not been
    completed. The request might or might not eventually be acted upon"; the representation
    "ought to describe the request's current status and point to (or embed) a status monitor
    that can provide the user with an estimate of when the request will be fulfilled."
- **[R8]** IETF RFC 8936, _Poll-Based Security Event Token (SET) Delivery Using HTTP_, November 2020.
  <https://www.rfc-editor.org/rfc/rfc8936>. §2.1: "The purpose of the acknowledgement is to inform
  the SET Transmitter that delivery has succeeded and redelivery is no longer required."

### Informative

- **[R2]** Google, _AIP-163: Change validation_, accessed 2026-10-07. <https://google.aip.dev/163>.
  "The API **must** perform permission checks and any other validation that would be performed
  on a "live" request; a request using `validate_only` **must** fail if it determines that the
  actual request would fail."
- **[R3]** Google, _AIP-154: Resource freshness validation_, accessed 2026-10-07.
  <https://google.aip.dev/154>. "If a user sends back an etag which does not match the current
  etag value, the service **must** send an `ABORTED` error response."
- **[R4]** Google, _AIP-234: Batch methods: Update_, and _AIP-193: Errors_, accessed 2026-10-07.
  <https://google.aip.dev/234>, <https://google.aip.dev/193>. AIP-234: "Synchronous batch update
  **must** be atomic." / "Asynchronous batch update **may** support atomic or partial success."
  AIP-193: "occasionally partial errors are necessary, particularly in bulk operations where it
  would be hostile to users to fail an entire large request because of a problem with a single
  entry."
- **[R5]** Kubernetes, _API Concepts: Dry-run_, accessed 2026-10-07.
  <https://kubernetes.io/docs/reference/using-api/api-concepts/>. "Kubernetes guarantees that
  dry-run requests will not be persisted in storage or have any other side effects";
  "Authorization for dry-run and non-dry-run requests is identical."
- **[R7]** Microsoft, _Combine multiple HTTP requests using JSON batching_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/graph/json-batching>. "A 200 status code on the batch response
  headers doesn't indicate that the individual requests inside the batch succeeded. This is why
  each individual response in the responses property has a status code."
- **[R9]** Microsoft, _Continuous access evaluation_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation>.
  "The goal for critical event evaluation is for response to be near real time, but latency of up
  to 15 minutes might be observed because of event propagation time."
- **[R10]** Google Cloud, _Access change propagation_, accessed 2026-10-07.
  <https://cloud.google.com/iam/docs/access-change-propagation>. "In IAM, access changes, such as
  granting a role or denying a permission, are eventually consistent"; changing a policy:
  "Typically 2 minutes, potentially 7 minutes or longer."
- **[R11]** Google Workspace Admin Help, _How changes propagate to Google services_, accessed
  2026-10-07. <https://support.google.com/a/answer/7514107>. "Some changes can take up to 24 hours
  to take effect. Sometimes, you'll see a warning message if there's an expected delay."
- **[R12]** OpenID Foundation, _OpenID Shared Signals Framework 1.0_, Final, §8.1.4.
  <https://openid.net/specs/openid-sharedsignals-framework-1_0-final.html>. "The acknowledgment of
  a Verification Event also confirms to the Event Transmitter that end-to-end delivery is working".
- **[R13]** C. G. Gray and D. R. Cheriton, _Leases: An Efficient Fault-Tolerant Mechanism for
  Distributed File Cache Consistency_, SOSP '89, ACM, 1989, accessed 2026-10-07.
  <https://doi.org/10.1145/74850.74870>; text read at
  <https://pages.cs.wisc.edu/~remzi/Classes/739/Fall2015/Papers/leases89.pdf>.
  - §2: "A lease is a contract that gives its holder specified rights over property for a limited
    period of time."
  - Abstract: "Non-Byzantine failures affect performance, not correctness, with their effect
    minimized by short leases."
- **[R14]** M. Kleppmann, _How to do distributed locking_, 8 February 2016, accessed 2026-10-07.
  <https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html>.
  - "You cannot fix this problem by inserting a check on the lock expiry just before writing back
    to storage."
  - "you need to include a fencing token with every write request to the storage service"; "the
    storage server remembers that it has already processed a write with a higher token number
    (34), and so it rejects the request with token 33."
  - "provided that the lock service generates strictly monotonically increasing tokens, this makes
    the lock safe."
- **[R15]** PostgreSQL Global Development Group, _PostgreSQL 17 Documentation_, accessed
  2026-10-07.
  - §5.9 Row Security Policies, <https://www.postgresql.org/docs/17/ddl-rowsecurity.html>: "Table
    owners normally bypass row security as well, though a table owner can choose to be subject to
    row security with ALTER TABLE ... FORCE ROW LEVEL SECURITY."
  - CREATE POLICY, <https://www.postgresql.org/docs/17/sql-createpolicy.html>: for `DELETE`, "the
    appropriate SELECT or ALL policies will be applied in addition to the DELETE policies"; of the
    `WITH CHECK` expression, "Only rows for which the expression evaluates to true will be
    allowed. An error will be thrown if the expression evaluates to false or null for any of the
    records inserted or any of the records that result from the update."
