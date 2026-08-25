---
doc_meta:
  id: ADR-GLB-013
  title: ADR-GLB-013 Separate Work, Workflow, Job, Schedule, Worker, and Queue Boundaries
  adr_type: foundational
  status: accepted
  created: 2026-08-23
  created_date: 2026-08-23
  created_by: Architecture Authority
  governed_by:
    - EAD-001
    - EAD-002
    - EAD-004
    - EAD-005
---

# ADR-GLB-013: Separate Work, Workflow, Job, Schedule, Worker, and Queue Boundaries

## 1. Title

Establish enterprise semantic boundaries for Work Item, Workflow, Job, Schedule, Worker, and Queue.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                                               | Approver               |
| :--------- | :------- | :----------- | :-------------------------------------------------------------------------------------- | :--------------------- |
| 2026-08-23 | accepted | foundational | Architecture Authority, Product Engineering, Workflow, Scheduling, Platform Engineering | Architecture Authority |

## 3. Context

Enterprise systems routinely use the words worker, queue, job, workflow, scheduler, case, task, and work interchangeably. That vocabulary collapse produces incorrect authority and platform boundaries.

A support queue is business-visible work inventory. A broker queue is transport. A scheduled trigger is not a Job result. A Worker is a runtime process, not a business authority. A Workflow may coordinate many Jobs and Work Items while retaining durable process state.

Without one enterprise semantic split, shared Platforms risk absorbing Product code, Product teams rebuild durable scheduling, Workflow becomes a universal execution engine, and technical queues become accidental business databases.

## 4. Decision Drivers

- HCM, Travel, future ERP, support/BPO, and Platform operations require assignable human work
- long-running processes require durable coordination
- bounded background execution is common across Products/Platforms
- Scheduling already has a distinct durable temporal authority
- technical message transport must not become business work authority
- central arbitrary Product worker execution would create release/security/blast-radius coupling
- terminology must be stable independent of runtime technology

## 5. Decision

Scnehaux SHALL use the following canonical meanings.

### 5.1 Work Item

A **Work Item** is business-visible actionable work requiring ownership, eligibility, assignment/claim, review, or completion semantics.

Work Management may own the generic Work Item lifecycle. The Product owns what the work means and its business outcome.

### 5.2 Workflow

A **Workflow** is a durable multi-step process coordination instance with persisted process position, transition semantics, human/system tasks, deadlines, compensation, or escalation.

Workflow owns process state, not participating Product business state.

### 5.3 Job

A **Job** is a bounded technical unit of execution performed by an owning Product/Platform.

Job execution may have attempts, leases, retries, timeout, cancellation, progress, and dead-letter/replay semantics. The Job handler remains within the Product/Platform authority that owns the effect.

### 5.4 Schedule

A **Schedule** is durable future temporal state whose authority is the Scheduling Platform.

Schedule produces an Occurrence/trigger. It does not prove Job or business completion.

### 5.5 Worker

A **Worker** is an execution topology/process that executes registered Product/Platform handlers.

A Worker is not an enterprise authority and does not become a Platform merely because multiple Products use background execution.

### 5.6 Queue

**Queue** is context-dependent and SHALL be qualified:

- **Work Queue** — business-visible Work Management inventory
- **Message Queue / Broker Partition** — transport buffering/ordering mechanism
- **Job Queue** — technical execution dispatch structure

A technical Queue SHALL NOT silently become the authoritative Work Item or Product record.

### 5.7 Boundary Composition

```text
Workflow Human Task
  → may create/reference Work Item

Workflow Automated Task
  → may request Product/Platform Job

Schedule Occurrence
  → may request Product/Platform Job or wake Workflow

Worker
  → executes Job handler

Message Queue
  → may carry Workflow/Job/Schedule/Work events or commands
```

Each authority remains separate.

### 5.8 Background Job Standard

Enterprise background execution semantics SHALL be standardized through STD-GLB-011 before any independent centralized Job Execution Platform Product is approved.

The standard does not require one shared runtime.

## 6. Consequences

### Positive

- clear boundary among human work, process coordination, temporal triggers, and technical execution
- Scheduling does not become a Worker Platform
- Workflow does not become a generic Job engine
- Products retain handler/business outcome ownership
- Work Management can serve HCM/Travel/ERP without absorbing workflow/process semantics
- runtime technology can change without changing enterprise vocabulary

### Negative

- architecture/designs must qualify ambiguous words such as `queue` and `task`
- Product teams may integrate multiple shared capabilities for complex journeys
- one end-to-end process can contain Work Items, Workflow tasks, Jobs, Schedules, and message queues simultaneously

### Operational

- Work Management receives an approved PAD
- Background Job Execution is added to Engineering & Runtime as a capability but not yet a separate Platform PAD
- Workflow and Scheduling PADs remain distinct
- STD-GLB-011 defines technical Job execution invariants

## 7. Compliance Impact

- aligns EAD-001, EAD-002, EAD-004, EAD-005
- requires new designs to qualify queue/job/worker/workflow semantics
- no exception to current Scheduling decision is created
- ADR-GLB-011 remains authoritative for Scheduling boundaries

## 8. Alternatives Considered

### Alternative A — One central Worker Platform

Rejected because it would host arbitrary Product code and couple release/security/dependencies.

### Alternative B — Workflow owns every background task and timer

Rejected because bounded Jobs and temporal Schedules do not require process-state semantics.

### Alternative C — Queue is the Work Item authority

Rejected because transport buffering and business work lifecycle have different correctness and ownership.

### Alternative D — Each Product defines its own vocabulary

Rejected because cross-Product architecture, observability, and platform contracts become ambiguous.
