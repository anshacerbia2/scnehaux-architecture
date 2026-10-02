---
doc_meta:
  id: ADR-GLB-018
  title: ADR-GLB-018 Deliver One Outbox to Several Named Consumers, Each with Its Own Outcome
  adr_type: foundational
  status: accepted
  created: 2026-10-02
  created_date: 2026-10-02
  created_by: Architecture Authority
  governed_by:
    - EAD-004
    - EAD-005
---

# ADR-GLB-018: Deliver One Outbox to Several Named Consumers, Each with Its Own Outcome

## 1. Title

Deliver one outbox to several named consumers, each with its own subscription, delivery state, evidence and dead letters, on the Direct Durable Delivery profile.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver               |
| :--------- | :------- | :----------- | :------------------------ | :--------------------- |
| 2026-10-02 | accepted | foundational | Architecture Review Board | Architecture Authority |

## 3. Context

`ADR-GLB-016 §5.4` already requires the relay to record delivery evidence "per message and per named consumer", and to attribute debt "to the consumer that refused the message". The implementation cannot do more than one consumer:

- `platform.outbox` has one `published` flag per event, so an event owed to two consumers cannot record two outcomes. `foundation-platform`'s dispatcher says so in its own configuration: "One dispatcher, one destination … the fan-out that would need -- one delivery row per (event, consumer) -- is deliberately not built."
- `platform.dead_letter` is keyed by `event_id`, so one consumer's refusal parks the event for every consumer.
- Organization Control refuses a second active projection consumer (`consumer_single_active`), and SAD-004 §7.6 records that "a second active projection consumer is refused until one is named".

Two consumers are now named. `foundation-reference` consumes Membership and Tenant events. The Identity Control Service consumes provider grants and activations for `provider:identity-control` (`ADR-ORG-002 §5.3`), and later the Membership projection into the kernel (`ADR-ORG-001 §5.4`). Every consumer of Organization's authority needs its own outcome, because the enforcement delay a consumer declares under `ADR-ORG-001 §5.7` is that consumer's, not the estate's.

## 4. Decision Drivers

- **Each consumer has its own outcome.** A consumer that is down, slow or refusing does not delay, park or close another consumer's delivery.
- **No event is skipped.** A consumer receives every event it subscribes to that commits after it subscribed, whatever order transactions commit in.
- **Evidence stays the consumer's own** (`ADR-GLB-016 §5.4`): `consumer_applied` is derivable only from the consumer's assertion, and debt and closure are per consumer.
- **No broker.** The Direct Durable Delivery profile stays (`STD-GLB-004 §3.2`), and an intermediary that would degrade every receipt to `transport_accepted` is not introduced.
- **The producer's commit path does not call out** (`STD-GLB-004 §3.3`).

## 5. Decision

### 5.1 A Consumer Subscribes to Event Types

A producer records each named consumer's **subscription**: the consumer's name, the event types it receives, and when it subscribed. This is how a managed messaging service divides one stream: "Each of the subscriber applications gets the same set of published messages from the topic" [R1], and a subscription may filter, with messages that do not match "automatically acknowledged" [R2]. An event type a consumer does not subscribe to is never delivered to it. It therefore cannot be refused as unknown, so a new event type for one consumer cannot park as poison at another.

A subscription is changed by replacing it, as Google's subscription filter "is an immutable property of a subscription" [R2]. A consumer that needs a type it did not receive re-bootstraps from the producer's snapshot (`STD-GLB-004 §3.12`), so what it holds is still the producer's state at a mark.

### 5.2 One Delivery Row per Event and Subscribed Consumer, Written with the Event

When an event is appended to the outbox, the same transaction writes one **delivery** row for each active subscription whose types include the event's. A delivery carries everything that was per event before:

- the publication state;
- attempts, the next attempt and the failure class;
- the lease;
- the lane, copied from the event.

The dispatcher for a consumer claims only that consumer's deliveries, by lane and then by sequence, with `FOR UPDATE SKIP LOCKED`, as it claims events today (`ADR-GLB-016 §5.2`).

**Why rows written at append, not a per-consumer position in the outbox.** A Kafka-style offset, one position per consumer over a single sequence, would be the smaller change. It is unsafe on PostgreSQL. A sequence value is taken when a row is inserted, not when its transaction commits, so a transaction holding a lower value can commit after one holding a higher value. A consumer whose position has passed the higher value would then never see the lower one, and the event is lost without an error. PostgreSQL states that sequences "cannot be used to obtain gapless sequences" [R3], and commit order is not sequence order either. A delivery row written in the event's own transaction exists exactly when the event does, so nothing commits without the deliveries it owes.

**A consumer subscribed after an event committed does not receive it.** It bootstraps from the snapshot and its high-water mark (`STD-GLB-004 §3.12`, SAD-004 §7.7), which is already how a first consumer begins.

### 5.3 Outcomes Are per Delivery

- **Evidence.** A delivery receipt is keyed by event and consumer, as `platform.delivery_receipt` already is, and records `consumer_applied` or `transport_accepted` (`ADR-GLB-016 §5.4`).
- **Dead letters.** A dead letter is keyed by event and consumer. One consumer's permanent refusal parks that consumer's delivery and no other. A security-priority delivery is never parked for unavailability, as before.
- **Debt.** A consumer's security debt counts its own unresolved dead letters. A dead letter that records no consumer, written before this decision, counts for every consumer (`ADR-GLB-016 §5.4`).
- **Closure.** Replay, resolution as delivered or as superseded, and waivers name the consumer whose delivery they act on, and evidence is read from that consumer's receipts.
- **Retention.** An event is retained while any of its deliveries is unpublished or dead-lettered and not abandoned (§5.5), as a managed service keeps a message until "at least one subscriber for each subscription has acknowledged" it [R1].

### 5.4 One Dispatcher per Consumer

Each consumer is served by its own dispatcher instance, named by the consumer and configured with that consumer's acceptance endpoint and credential, as the current dispatcher is configured for one. A dispatcher claims only its consumer's deliveries, so its leases, backoff and lane workers are that consumer's. Two consumers never share a lease, and one slow endpoint never holds another's priority lane.

### 5.5 A Retired Consumer's Owed Deliveries Are Abandoned

Retiring a consumer retires its subscription, and the deliveries still owed to it are closed as **abandoned**: marked published, with the reason recorded, and no receipt. Nothing will ever deliver them. The retired consumer's dispatcher refuses to start, and a consumer rebuilt under a new identity bootstraps from a snapshot (`STD-GLB-004 §3.12`). Left owed, they would hold retention for every event they belong to (§5.3) for as long as the estate runs. This is how a managed service treats a deleted subscription: "Even if the deleted subscription had many unacknowledged messages, a new subscription created with the same name would have no backlog" [R5].

An abandoned delivery is not a dead letter and resolves nothing. It is neither evidence nor debt: no receipt is written, so no closure can cite it. Abandoning applies only to a consumer with no active subscription, so a consumer that is still enforcing never has a delivery it is owed abandoned.

### 5.6 Appending Needs No Read of the Outbox

The statement that appends an event writes its deliveries from values it computes itself, not by reading back the inserted row. PostgreSQL requires "`SELECT` privilege on all columns mentioned in `RETURNING`" [R6], so reading the row back would grant every role that appends the right to read the outbox. The request roles that publish events hold `INSERT` on the outbox today and nothing more. The statement reads only the active subscriptions, and since "if you use the _query_ clause to insert rows from a query, you of course need to have `SELECT` privilege on any table or column used in the query" [R6], an appending role holds `SELECT` on `platform.subscription`'s `consumer`, `event_types` and `retired_at` columns, and `INSERT` on `platform.outbox_delivery`.

### 5.7 What Does Not Change

- At-least-once delivery, consumer deduplication by event and consumer in `platform.processed_event`, and version-guarded application (`STD-GLB-004 §3.9`, §3.11). A relay may still deliver an event more than once, and a consumer "must be idempotent" [R4].
- The producer's commit path writes rows and calls nothing (`STD-GLB-004 §3.3`).
- The envelope, event types and versions (`ADR-GLB-006`).

## 6. Consequences

### Positive

- Organization Control serves more than one projection consumer, each with its own enforcement delay, debt and closure, which the Identity Control Service needs.
- A new event type reaches only the consumers that subscribe to it.
- The lost-event failure a per-consumer position would carry never exists.

### Negative

- **Writes grow with consumers.** Each appended event writes one delivery row per subscribed consumer, inside the producer's transaction.
- **The dead-letter key changes** from event to event and consumer. Replay, resolution, waivers and the frontier change with it, in `foundation-platform` and in Organization Control.
- **Each consumer is a deployment.** A dispatcher runs per consumer, with its own endpoint and credential.
- **A subscription change is a re-bootstrap,** not an edit.
- **Retirement discards a consumer's backlog** (§5.5). A consumer retired by mistake does not resume where it stopped; it is registered again and bootstraps from a snapshot.
- **Appending roles read the subscriptions** (§5.6). They learn which consumers exist and what each subscribes to, which is configuration rather than authority data.

### Operational

- Lane lag, oldest unpublished age and security debt are reported per consumer.
- Retention removes an event only once every delivery it owes is published, dead-lettered and closed or waived, or abandoned at its consumer's retirement.

## 7. Compliance Impact

### Related Standards

- [ADR-GLB-016](ADR-GLB-016-durable-messaging-substrate-profiles.md) §5.2 and §5.4: relay claim, per-consumer evidence and debt, closure, waivers.
- STD-GLB-004 §3.2, §3.3, §3.4, §3.9, §3.11 and §3.12: profiles, the commit path, publication state, deduplication, ordering, and snapshot bootstrap.
- [ADR-ORG-001](../organization-tenancy-platform/ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.7: each consumer declares its freshness and enforcement delay.
- [ADR-ORG-002](../organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md) §5.3: the Identity Control Service as a consumer of provider authority.

### Compliance Status

Compliant. STD-GLB-004 §3.4 requires publication state and no longer a single `published` boolean. SAD-004 §7.6 is amended in the same change.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — A Per-Consumer Position over the Outbox Sequence

**Benefits:** no delivery rows; each consumer keeps one number, as a Kafka consumer group keeps an offset.

**Rejected because:** of §5.2. On PostgreSQL a transaction can commit a lower sequence value after a higher one, so a position can pass an event that has not yet committed, and that event is never delivered. Making positions safe would require a commit-ordered log, which is a broker.

### Alternative B — A Broker Between the Outbox and the Consumers

**Benefits:** fan-out, retention and per-subscription dead letters come with the product [R1][R2].

**Rejected because:** a broker between relay and consumer "yields `transport_accepted` only" (`ADR-GLB-016 §5.4`), so no security dead letter could ever close on `consumer_applied` evidence. `STD-GLB-004 §3.2` also forbids a higher-complexity profile without a concrete driver, and the consumers are few.

### Alternative C — One Outbox per Consumer

**Benefits:** each outbox keeps the single-destination dispatcher unchanged.

**Rejected because:** the producer would write the same event once per consumer, in different tables, and nothing would tie the copies to one event identity. Closure by supersession compares versions of one event history, which several copies would fork.

### Alternative D — Keep One Consumer; the Second Reads the First

**Benefits:** nothing changes in the producer.

**Rejected because:** the second consumer's enforcement would depend on the first consumer's availability and correctness, and its evidence would be the first consumer's assertion. `ADR-GLB-016 §5.4` requires evidence from the consumer the enforcement depends on.

### Alternative E — Keep a Retired Consumer's Deliveries Owed

**Benefits:** a consumer retired by mistake could be revived and resume where it stopped.

**Rejected because:** nothing delivers to a retired consumer, so its deliveries would stay owed for as long as the estate runs and hold retention for every event they belong to. A revived consumer's model is also older than its own declared freshness allows, and the bootstrap contract already rebuilds it from a snapshot. A managed service discards a deleted subscription's backlog for the same reason [R5].

### Alternative F — Read the Inserted Event Back to Write Its Deliveries

**Benefits:** the deliveries copy the event's columns exactly as stored, including the database-assigned `created_at`.

**Rejected because:** `RETURNING` requires `SELECT` on the columns it names [R6], which would give every role that appends the right to read the outbox. The statement computes the creation instant and the position itself, writes both into the event and its deliveries, and so the two still cannot disagree.

## 9. References

### Informative

- **[R1]** Google Cloud, _Overview of the Pub/Sub service_, accessed 2026-10-02. <https://docs.cloud.google.com/pubsub/docs/pubsub-basics>. "Each of the subscriber applications gets the same set of published messages from the topic"; "After at least one subscriber for each subscription has acknowledged the message, Pub/Sub deletes the message from storage."
- **[R2]** Google Cloud, _Filter messages from a subscription_, accessed 2026-10-02. <https://docs.cloud.google.com/pubsub/docs/subscription-message-filter>. "The Pub/Sub service automatically acknowledges the messages that don't match the filter"; "The filter is an immutable property of a subscription."
- **[R3]** PostgreSQL 18, _Sequence Manipulation Functions_, accessed 2026-10-02. <https://www.postgresql.org/docs/current/functions-sequence.html>. "PostgreSQL sequence objects cannot be used to obtain 'gapless' sequences."
- **[R4]** Chris Richardson, _Pattern: Transactional outbox_, accessed 2026-10-02. <https://microservices.io/patterns/data/transactional-outbox.html>. "The Message relay might publish a message more than once … a message consumer must be idempotent."
- **[R5]** Google Cloud, _Subscription overview_, accessed 2026-10-02. <https://docs.cloud.google.com/pubsub/docs/subscription-overview>. "Although you can create a new subscription with the same name as a deleted one, the new subscription has no relationship to the old one"; "Even if the deleted subscription had many unacknowledged messages, a new subscription created with the same name would have no backlog (no messages waiting for delivery) at the time it's created."
- **[R6]** PostgreSQL 18, _INSERT_, accessed 2026-10-02. <https://www.postgresql.org/docs/current/sql-insert.html>. "Use of the `RETURNING` clause requires `SELECT` privilege on all columns mentioned in `RETURNING`"; "If you use the _query_ clause to insert rows from a query, you of course need to have `SELECT` privilege on any table or column used in the query."
