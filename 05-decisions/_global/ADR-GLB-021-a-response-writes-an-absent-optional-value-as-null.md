---
doc_meta:
  id: ADR-GLB-021
  title: ADR-GLB-021 A Response Writes an Absent Optional Value as null, Never as a Sentinel
  adr_type: foundational
  status: accepted
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: Architecture Authority
  governed_by:
    - GDC-000
  authorizes: [STD-GLB-001]
---

# ADR-GLB-021: A Response Writes an Absent Optional Value as null, Never as a Sentinel

## 1. Title

A response writes an absent optional value as `null`, never as a sentinel.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver               |
| :--------- | :------- | :----------- | :------------------------ | :--------------------- |
| 2026-10-24 | accepted | foundational | Architecture Review Board | Architecture Authority |

GDC-005 makes a governance artifact accepted when it is reviewed and merged by pull request. The owner's merge of the pull request that adds this decision is that act.

## 3. Context

`STD-GLB-001` governs the shape of a response and says nothing about a value that is not there. organization-control found the gap (its ROADMAP item 67, recorded 2026-10-22): a Membership with no Workspace is written with `workspace_id` set to `00000000-0000-0000-0000-000000000000`, and one with no end date with `valid_until` set to `0001-01-01T00:00:00Z`. Go writes the zero value of `uuid.UUID` and `time.Time` when a field has no pointer. Its `api/openapi.yaml` lists both members as required and gives them a string type, so the schema check passes, and nothing in the specification says that those two values mean "none".

Facts that bound the choice:

- **A sentinel is an ordinary value of the type.** The nil UUID is a UUID, and RFC 9562 allows it as an absence marker only "in situations that otherwise require or use a 128-bit UUID" [R1]. JSON has a value for absence, so a JSON response is not such a situation. `0001-01-01T00:00:00Z` is a valid RFC 3339 `date-time` (RFC 3339 §5.6, which `STD-GLB-001` cites as its R18). A client cannot tell the sentinel from a real value without knowing the convention, and a client that does not know it shows year 1 as a date.
- **JSON has a value for absence.** RFC 8259 §3: "A JSON value MUST be an object, array, number, or string, or one of the following three literal names: false null true" [R2].
- **OpenAPI 3.1 writes it in the `type`.** "Models are defined using the Schema Object, which is a superset of JSON Schema Specification Draft 2020-12" [R3]. JSON Schema 2020-12 §6.1.1: "If it is an array, elements of the array MUST be strings and MUST be unique", the strings may be `"null"`, and "an instance validates successfully if its type matches any of the types indicated by the strings in the array" [R4]. The word `nullable` does not occur in the OpenAPI 3.1.0 text. The OpenAPI Initiative says why: the `type` array "has also made nullable redundant", so "it was decided to remove nullable entirely instead of deprecate it" [R5].
- **Required and nullable are separate questions.** JSON Schema §6.5.3: "An object instance is valid against this keyword if every item in the array is the name of a property in the instance" [R4]. A member can be required and still carry `null`.
- **A consumer pins the specification and already reads both members as nullable.** organization-experience vendors organization-control's `api/openapi.yaml` under `contracts/` and contract-tests its client against it. Its Membership types declare `workspace_id?: string | null` and `valid_until?: string | null`, so the UI already shows "none" for `null`, and shows the sentinel as a real Workspace and a real date. A choice that adds `null` to the type widens the value set and keeps every key; one that removes a member also edits `required`.

What the sources do not say: none of them names the sentinel as forbidden for a JSON response, and none chooses between `null` and omission for a response. Zalando says the two must mean the same; Google says the distinction is rarely wanted. The choice is this estate's, made on the conservative reading below.

## 4. Decision Drivers

- A client reads one meaning for "none", from the schema alone.
- A change to a pinned specification must keep a consumer's generated types valid, or say what they must add.
- The rule must be checkable in a schema and in a handler test.
- Where a source is silent, the conservative option wins.

## 5. Decision

### 5.1 An Absent Optional Value Is `null`, Declared in the Schema

When a response member has no value, the service writes the member with the JSON value `null`. The member's schema declares it with an OpenAPI 3.1 type array, `type: [<type>, "null"]`, and keeps `format` and the other keywords for the non-null type. `nullable: true` is not used: it is not part of 3.1.

- A member that is always present in the object stays in `required`. Required means the key is there; `null` is the value.
- A member that a response sometimes leaves out is not `required`. It is written as in §5.2.

### 5.2 A Client Reads Absent and `null` Alike

A client MUST treat a missing member and a `null` member as the same "none". Zalando states the same rule: when a property "is defined to be not required and nullable", the rule "demands that both cases must be handled in the exact same manner" [R6]. A service therefore never gives omission and `null` different meanings in one response.

### 5.3 A Sentinel Is Never Allowed

A response never writes a value of the member's own type to mean "none": not the nil UUID, not `0001-01-01T00:00:00Z` or the Unix epoch, not `0` or `-1` for a number, not an empty string for a value whose type has no empty form. An empty string stays valid where emptiness is a real value of the member. A handler writes a pointer or a nullable type, so that the zero value of its language is never serialised as "none".

### 5.4 What Is Not Changed

- `false` for a boolean, `0` for a count and `[]` for a list that are real values stay as they are. Zalando also says not to use `null` for a boolean or an empty array [R6], and this decision does not either.
- A request that merges (JSON Merge Patch) keeps its own rule, where `null` deletes a member.
- A stored column keeps its own representation. The rule governs the wire.

### 5.5 Checks

`STD-GLB-001` §Enforcement: a service's tests assert that a response with an absent value carries `null` and not the zero value of its type, and its schema check includes a response whose optional member is absent.

## 6. Consequences

### Positive

- One meaning of "none" on every response, readable from the schema.
- A client that follows the schema handles the "none" case instead of showing year 1.
- The change keeps every key: no consumer loses a member.

### Negative

- A consumer that treats the member as non-null must change. organization-experience's types already allow `null`, so its change is its contract test and the tests that feed it the sentinel.
- Every service that wrote a zero value changes its handlers and its specification in step with its consumers.

### Operational

- Each repository's TDD and ROADMAP record what changes in it (§7). No production exists (`SAD-001` §9.1 and `SAD-004` §10.3 record the development server alone), so no data is migrated and no field is versioned.

## 7. Compliance Impact

### Related Standards

- `STD-GLB-001` 2.0.0, §A Response Writes an Absent Optional Value as `null` and §Enforcement Mechanism, which this decision authorizes.

### Compliance Status

- organization-control does not comply: ROADMAP item 67 (`workspace_id`, `valid_until`). Its TDD, `api/openapi.yaml` and handlers change, and the item cites this decision.
- organization-experience must follow: its pinned `contracts/organization-control/openapi.yaml`, its contract test and the UI that renders both members. It changes in step with organization-control's specification, not before.
- identity-control: not checked on its own branches by this decision. A search of `internal/httpapi` on `origin/main` for `time.Time{}` and `uuid.Nil` found nothing on 2026-10-24. That search finds the two literal spellings only, so identity-control's ROADMAP records a check of every optional response member.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Omit the member

**Benefits:** the smallest payload; Zalando treats it as equal to `null`.

**Not chosen as the rule because:** the pinned specification lists both members as required, so omission means editing `required` as well as the type, and a consumer's contract test that expects the key fails. It stays allowed for a member that is not required (§5.1).

### Alternative B — A documented sentinel

**Benefits:** no change to the specification's types; no change to a consumer that already reads the value.

**Rejected because:** the value is valid for its type, so no schema and no client can tell it from a real one. RFC 9562 allows the nil UUID as an absence marker only where a 128-bit UUID is required [R1], and JSON is not such a place [R2]. The convention would live in prose a client does not read.

### Alternative C — Leave it to each service

**Benefits:** no standard to adopt.

**Rejected because:** that is how two services came to differ in what "none" looks like, and `STD-GLB-001` exists to keep the API "deeply consistent across all domains".

## 9. References

### Normative

- **[R1]** IETF RFC 9562, _Universally Unique IDentifiers (UUIDs)_, §5.9 Nil UUID, May 2024. <https://www.rfc-editor.org/rfc/rfc9562.html#section-5.9>. "The Nil UUID is special form of UUID that is specified to have all 128 bits set to zero."; "A Nil UUID value can be useful to communicate the absence of any other UUID value in situations that otherwise require or use a 128-bit UUID."; "A Nil UUID can express the concept "no such value here"." Accessed 2026-10-24. RFC 9562 permits the nil UUID as an absence marker; reading that as limited to a place that must hold a UUID is this decision's inference, not RFC 9562's words.
- **[R2]** IETF RFC 8259, _The JavaScript Object Notation (JSON) Data Interchange Format_, §3 Values, December 2017. <https://www.rfc-editor.org/rfc/rfc8259.html#section-3>. "A JSON value MUST be an object, array, number, or string, or one of the following three literal names: false null true"; "The literal names MUST be lowercase. No other literal names are allowed."
- **[R3]** OpenAPI Initiative, _OpenAPI Specification v3.1.0_, §4.4 Data Types, accessed 2026-10-24. <https://spec.openapis.org/oas/v3.1.0.html>. "Data types in the OAS are based on the types supported by the JSON Schema Specification Draft 2020-12."; "Models are defined using the Schema Object, which is a superset of JSON Schema Specification Draft 2020-12."
- **[R4]** IETF JSON Schema, _JSON Schema Validation: A Vocabulary for Structural Validation of JSON_, draft 2020-12, §6.1.1 type and §6.5.3 required, accessed 2026-10-24. <https://json-schema.org/draft/2020-12/json-schema-validation>. "The value of this keyword MUST be either a string or an array. If it is an array, elements of the array MUST be strings and MUST be unique."; "String values MUST be one of the six primitive types ("null", "boolean", "object", "array", "number", or "string"), or "integer" which matches any number with a zero fractional part."; "If the value of "type" is an array, then an instance validates successfully if its type matches any of the types indicated by the strings in the array."; "An object instance is valid against this keyword if every item in the array is the name of a property in the instance."

### Informative

- **[R5]** OpenAPI Initiative, _Migrating from OpenAPI 3.0 to 3.1.0_, §Swap nullable for type arrays, accessed 2026-10-24. <https://www.openapis.org/blog/2021/02/16/migrating-from-openapi-3-0-to-3-1-0>. "the `type` keyword can now define multiple types for a schema with an array. This is useful new functionality, but has also made nullable redundant."; "it was decided to remove nullable entirely instead of deprecate it."
- **[R6]** Zalando, _RESTful API Guidelines_, §MUST use same semantics for null and absent properties, accessed 2026-10-24. <https://opensource.zalando.com/restful-api-guidelines/>. "OpenAPI 3.x allows to mark properties as required and as nullable to specify whether properties may be absent ({}) or null ({"example":null})."; "If a property is defined to be not required and nullable (see 2nd row in Table below), this rule demands that both cases must be handled in the exact same manner by specification."; "we explicitly decide against that option, because we think that any gain in expressiveness is far outweighed by the risk of clients not understanding and implementing the subtle differences incorrectly"; "MUST not use null for boolean properties"; "SHOULD not use null for empty arrays".
- **[R7]** Google, _AIP-149: Unset field values_, accessed 2026-10-24. <https://google.aip.dev/149>. "In most cases, there is no meaningful difference between setting it to a default value (such as 0) as opposed to not setting it at all; however, occasionally this distinction is meaningful."; "Services should not need to distinguish between the default value and unset most of the time; if an alternative design does not require such a distinction, it is usually preferred." AIP-149 is written for protocol buffers; it is cited for the point that a default value and "unset" are different states, not for a JSON rule.
