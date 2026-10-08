---
doc_meta:
  id: STD-GLB-001
  title: Enterprise API Design Standard
  owner: Architecture Review Board
  version: 1.6.0
  status: approved
  classification: public
  governed_by: [EAD-004]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_updated: 2026-10-08
  last_reviewed: 2026-10-08
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
- Responses SHOULD NOT use custom envelopes for standard data (return direct arrays/objects) to minimize payload bloat. A paginated list is the exception, because the continuation must travel with the page (§Pagination).
- Error responses MUST conform to **RFC 9457 (Problem Details for HTTP APIs)**, which obsoletes RFC 7807.

  The two are wire-compatible: RFC 9457 keeps every member 7807 defined and adds the optional `errors` array for reporting several problems in one response. A conforming 7807 document is therefore a conforming 9457 document, so no existing implementation breaks. The citation is corrected because RFC 9457 states "This document obsoletes RFC 7807" [R9], and a standard naming the obsoleted RFC sends implementers to a document that no longer defines the registry. Until 1.3.1 this sentence attributed the requirement to `EAD-004 §5.3`. That section is the AI Provider Contract and says nothing of problem details, so the attribution is withdrawn: the rule rests on RFC 9457 itself.

### Versioning

- APIs MUST be versioned at the URL path level (e.g., `/api/v1/users`).
- Header-based versioning is PROHIBITED due to complexity in CDN caching and network edge routing.

### Pagination

- List endpoints returning unbounded data MUST be paginated.
- Cursor-based pagination (e.g., `?after=xyz&limit=100`) is MANDATORY for all core entities. Offset-based pagination (`?offset=100`) is strictly PROHIBITED for large datasets due to database scanning penalties.
- **A list is paginated from its first release (1.3.0).** Adding pagination later breaks every client that read the whole list. Google: "RPCs returning collections of data **must** provide pagination _at the outset_" [R2]; Microsoft Graph says the same of "all collections" [R4].
- **The list form (1.3.0).** Every list in the estate takes and returns the same form, which identity-control and organization-control serve:

  | Part      | Form                                                                                                                    |
  | :-------- | :---------------------------------------------------------------------------------------------------------------------- |
  | Cursor    | `after`: the identifier of the last item of the previous page. Absent, the list starts at its first item                |
  | Page size | `limit`: 50 when absent, 100 at most                                                                                    |
  | Filters   | Named query parameters beside the cursor, each a closed set of values                                                   |
  | Order     | The primary key. A UUIDv7 key gives creation order                                                                      |
  | Response  | `{"<items>": [...], "next": "<identifier>" \| null}`. `next` is the `after` of the following page, and null on the last |
  - **The response wraps the array**, as every source does. Google's list response "**must** include one repeated field corresponding to the resources being returned" and the next-page token [R3]. Azure's guidelines say "**DO** structure the response to a list operation as an object with a top-level array field" [R5]. Stripe returns `data` with `has_more` [R6].
  - **The end of a list is `next` = null, and nothing else.** Google calls the empty token "the _only_ way to communicate "end-of-collection" to users" [R2]. Azure: "**DO NOT** return the `nextLink` field at all when returning the last page" [R5]. A client never infers the end from a short page.
  - **The cursor is an object identifier and the order is its key.** This is Stripe's form ("Both parameters accept an existing object ID value") [R6] and GitHub's `before`/`after` [R7]. Microsoft Graph asks the server to sort by key "to ensure that items are always ordered consistently" and to "encode the record ID of the last read record" [R4]. PostgreSQL warns that offsets "give inconsistent results unless you enforce a predictable result ordering", and that "a large OFFSET might be inefficient" [R8]. This rule is stricter than Google's on one point: the identifier is not opaque [R2], because the key is a UUID the client already holds and parses as nothing.
  - **A filter holds for every page of a list.** "**DO** use the same filtering options and sort order for all pages of a paginated list operation response" [R5]. A changed filter starts again from the first page.
  - **A time window is two filters, `from` and `to` (1.6.0).** Each is an RFC 3339 `date-time` with its offset, the form RFC 3339 gives as `date-time = full-date "T" full-time`, where a `full-time` ends in a `time-offset` [R18]. RFC 3339 adds that "all dates and times used in Internet protocols MUST be fully qualified" [R18], so an instant without an offset is refused. `from` is inclusive and `to` exclusive, so two adjacent windows share no item and leave none out. CloudTrail's lookup is the precedent for the filter, with "only events that occur after or at the specified time" for its start [R19]; it also includes its end ("before or at the specified time" [R19]), and this standard does not, so a review of one week and a review of the next cover each instant once. A `to` not after `from` is refused with `400`. The window is a filter like any other: it holds for every page, and the order is still the key.
  - **A `limit` outside 1 to 100 is refused with `400`, not coerced.** Google [R2][R3] and GitHub [R7] coerce down to the maximum. This standard departs from them: a refusal tells the client the bound at once, where a silent reduction hides it. A page shorter than asked is still never the end of the list.

### Security & Authentication

- All requests MUST be authenticated at the API Gateway using JWT via the `Authorization: Bearer <token>` header.
- Internal machine-to-machine calls MUST use mTLS or an internal service mesh token.

### Request Header Values

- A request header this estate defines (for example `X-Administrative-Reason` or `Idempotency-Key`) SHOULD take only visible US-ASCII characters, space and horizontal tab. RFC 9110 §5.5 asks this of every newly defined field: "newly defined fields SHOULD limit their values to visible US-ASCII octets (VCHAR), SP, and HTAB" [R1].
- A service SHOULD refuse, with `400`, a value outside that range rather than store it. RFC 9110 has a recipient "treat other allowed octets in field content as opaque data" [R1], so they carry no encoding the service could rely on. Bytes stored as text are then whatever the client's library chose. In one case a Latin-1 `§` (`0xA7`) reached PostgreSQL as invalid UTF-8, and the request failed as an unexplained `503`.
- Free text that needs other characters SHOULD travel in the request body, whose media type states its encoding.

### Commands Require an `Idempotency-Key` (1.4.0)

A client that sends a `POST` and loses the response cannot tell whether it was applied. Retried without a key, it is applied twice: a second Workspace, a second grant. The IETF draft for the header states the problem: "Repeating the request multiple times can result in duplication or incorrect updates" [R10].

- **A command MUST require an `Idempotency-Key`.** A command is a `POST` that a person or an operator sends to change authoritative state.
- **A command without the header, or with a blank one, is refused `400`** with a problem that names the header. The draft gives this answer: "the resource SHOULD reply with an HTTP 400 status code" [R10]. The check runs after the caller's authority, so a caller the route does not admit is told `403`, not about a header.
- **Any other `POST` MAY honour a key without requiring one**, when a repeat cannot act twice:
  - a read carried in a body;
  - a report the receiver applies monotonically, such as a consumer's position that only moves forward;
  - a sweep or a comparison, whose repeat finds nothing left to do or the same findings;
  - a report identified by a correlation identifier it already carries.
- **Each service publishes which routes require the key, and the reason each other `POST` does not.** The draft requires it: "Resources MUST publish a idempotency related specification" [R10]. organization-control does this in `TDD-organization-control-003` 1.10.0 §The `Idempotency-Key` Is Required on Commands. identity-control already requires the key on its Principal, workload, registration and security commands.
- **The draft is work in progress.** Revision -07 expired on 18 April 2026 and is cited as such. The rule rests on what a lost response does to a retried command; the draft supplies the status code.

### A Version Where an Update Can Be Lost, a Reason Where One Acts for Another (1.5.0)

Two request parts guard different failures. A version guards a decision taken on state that someone else changed since it was read. A reason records why an actor touched a record that is not their own. Neither is a property of every command.

- **A command MUST carry the version it was decided on when another actor can change that state between the read and the command**, as `expected_version` in the body or as `If-Match`, and a stale one is refused `409`. This is the "lost update" problem: RFC 9110 has `If-Match` "prevent accidental overwrites when multiple user agents might be acting in parallel on the same resource" [R11], and RFC 6585 gives `428` for a server that requires it, whose "typical use is to avoid the "lost update" problem, where a client GETs a resource's state, modifies it, and PUTs it back to the server, when meanwhile a third party has modified the state on the server" [R12]. An administrator suspending a Principal, a provider approving a registration change, and an operator replacing a Tenant's settings are such commands. Google's People API refuses a contact update whose etag differs, "which indicates the contact has changed since its data was read" [R14].
- **A person's command on their own account MAY omit the version**, when it names one object by a handle from a fresh read and only ends or adds it: ending a session, removing an authenticator, adding or removing a notification address. There is no representation to overwrite. A repeat finds the object gone, and the service re-checks at execution what the command depends on, such as the last remaining authenticator. A handle that expires bounds how stale the read can be. Microsoft Graph's `DELETE /me/authentication/microsoftAuthenticatorMethods/{id}` takes no precondition: "Don't supply a request body for this method" [R15]. Okta's MyAccount API, a person's own "emails, phones, profile, and app authenticators", defines no `If-Match` and no reason on any operation, `deletePhone` included [R16].
- **A command on a record that is not the actor's own MUST carry a reason**, `X-Administrative-Reason`. NIST SP 800-53 AU-3 lists what an audit record establishes: the type of event, when, where, its source, its outcome, and "Identity of any individuals, subjects, or objects/entities associated with the event" [R13]. A justification is not among them. AU-3(1) lets an organization add "[Assignment: organization-defined additional information]" [R13], and this estate adds the reason where the actor and the subject differ, because a reviewer of an administrator's access to someone else's account needs to know why.
- **A person's command on their own account carries no reason.** The actor and the subject are the same Principal, and the record already names them, the object and the outcome. OWASP's "Reason" event attribute is "why the status above occurred e.g. User not authenticated in database check ..., Incorrect credentials" [R17]: the cause of the outcome, which the service records itself, not text the person types. Microsoft asks for fresh authentication instead: "When users manage their own authentication methods, the system prompts them to complete multi-factor authentication (MFA) if they last authenticated more than 10 minutes ago" [R15]. A person's command that gains access requires step-up for the same reason (`ADR-IAM-004`).
- **The tradeoff.** Requiring a version on a person's own commands, refused `428` without one, was rejected: it guards no lost update, and it would refuse the person's second command whenever the first moved the version. An optional reason was rejected: nobody fills it, and free text a person types would carry personal data into the audit store. The residual risk is a taken-over account acting without explanation. A reason an attacker types would not reduce it. Step-up and the notification sent to every address of the Principal on an authenticator change (`STD-IAM-001 §3.1`) do.

### Rate Limiting

All public-facing APIs MUST return standard rate-limit headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Exceptions

Legacy systems currently running SOAP or XML are exempt until their scheduled sunset dates.

## Enforcement Mechanism

API schema validation via the API Gateway and CI/CD spectral linters.

## References

- **[R1]** IETF RFC 9110, _HTTP Semantics_, §5.5 Field Values, June 2022. <https://www.rfc-editor.org/rfc/rfc9110.html#section-5.5>. "Field values are usually constrained to the range of US-ASCII characters"; "newly defined fields SHOULD limit their values to visible US-ASCII octets (VCHAR), SP, and HTAB"; a recipient "SHOULD treat other allowed octets in field content as opaque data."
- **[R2]** Google, _AIP-158: Pagination_, accessed 2026-10-07. <https://google.aip.dev/158>. "RPCs returning collections of data **must** provide pagination _at the outset_, as it is a backwards-incompatible change to add pagination to an existing method"; "If the end of the collection has been reached, the `next_page_token` field **must** be empty. This is the _only_ way to communicate "end-of-collection" to users"; "Page tokens provided by APIs **must** be opaque"; "the API **should** coerce down to the maximum permitted page size."
- **[R3]** Google, _AIP-132: Standard methods: List_, §Response message, accessed 2026-10-07. <https://google.aip.dev/132>. "The response message **must** include one repeated field corresponding to the resources being returned"; the `next_page_token` "**must** be set if there are subsequent pages, and **must not** be set if the response represents the final page."
- **[R4]** Microsoft, _Microsoft Graph REST API Guidelines: Collections_, §4 and §8.3, accessed 2026-10-07. <https://github.com/microsoft/api-guidelines/blob/vNext/graph/articles/collections.md>. "Services SHOULD support server-side pagination from day one even for all collections, as adding pagination is a breaking change"; "The server MUST supplement any specified order criteria with additional sorts (typically by key) to ensure that items are always ordered consistently"; "The server SHOULD always encode the record ID of the last read record."
- **[R5]** Microsoft, _Azure REST API Guidelines_, §Collections, accessed 2026-10-07. <https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md>. "**DO** structure the response to a list operation as an object with a top-level array field containing the set (or subset) of resources"; "**DO NOT** return the `nextLink` field at all when returning the last page of the collection"; "**DO** use the same filtering options and sort order for all pages of a paginated list operation response."
- **[R6]** Stripe, _API Reference: Pagination_, accessed 2026-10-07. <https://docs.stripe.com/api/pagination>. "Stripe's list API methods use cursor-based pagination through the starting_after and ending_before parameters. Both parameters accept an existing object ID value"; `limit` "ranging between 1 and 100"; the list response carries `data` and `has_more`.
- **[R7]** GitHub, _Using pagination in the REST API_, accessed 2026-10-07. <https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api>. "each paginated endpoint will use the `page`, `before`/`after`, or `since` query parameters"; "If you specify a value greater than the maximum, GitHub does not return an error. Instead, the value is automatically reduced to the maximum."
- **[R8]** PostgreSQL Global Development Group, _PostgreSQL 18 Documentation_, §7.6 LIMIT and OFFSET, accessed 2026-10-07. <https://www.postgresql.org/docs/current/queries-limit.html>. "using different LIMIT / OFFSET values to select different subsets of a query result will give inconsistent results unless you enforce a predictable result ordering with ORDER BY"; "a large OFFSET might be inefficient."
- **[R9]** IETF RFC 9457, _Problem Details for HTTP APIs_, July 2023. <https://www.rfc-editor.org/rfc/rfc9457>. Abstract: it "defines a "problem detail" to carry machine-readable details of errors in HTTP response content to avoid the need to define new error response formats for HTTP APIs"; "This document obsoletes RFC 7807."
- **[R10]** IETF HTTPAPI Working Group, J. Jena and S. Dalal, _The Idempotency-Key HTTP Header Field_, Internet-Draft draft-ietf-httpapi-idempotency-key-header-07, 15 October 2025 (expired 18 April 2026; work in progress), accessed 2026-10-07. <https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/07/>.
  - §1: "Repeating the request multiple times can result in duplication or incorrect updates. Consider a scenario where the client sent a POST request to the server, but the request timed out."
  - §2.5.2: "Resources MUST publish a idempotency related specification."
  - §2.7: "If the Idempotency-Key request header is missing for a documented idempotent operation requiring this header, the resource SHOULD reply with an HTTP 400 status code with body containing a link pointing to relevant documentation."
- **[R11]** IETF RFC 9110, _HTTP Semantics_, §13.1.1 If-Match, June 2022. <https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1>. "If-Match is most often used with state-changing methods (e.g., POST, PUT, DELETE) to prevent accidental overwrites when multiple user agents might be acting in parallel on the same resource (i.e., to prevent the "lost update" problem)."
- **[R12]** IETF RFC 6585, _Additional HTTP Status Codes_, §3 428 Precondition Required, April 2012. <https://www.rfc-editor.org/rfc/rfc6585#section-3>. "The 428 status code indicates that the origin server requires the request to be conditional. Its typical use is to avoid the "lost update" problem, where a client GETs a resource's state, modifies it, and PUTs it back to the server, when meanwhile a third party has modified the state on the server, leading to a conflict."
- **[R13]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_, AU-3 Content of Audit Records and AU-3(1) Additional Audit Information. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. AU-3: "Ensure that audit records contain information that establishes the following: a. What type of event occurred; b. When the event occurred; c. Where the event occurred; d. Source of the event; e. Outcome of the event; and f. Identity of any individuals, subjects, or objects/entities associated with the event." AU-3(1): "Generate audit records containing the following additional information: [Assignment: organization-defined additional information]." Quoted from NIST's OSCAL catalog, <https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>, accessed 2026-10-08.
- **[R14]** Google, _People API: people.updateContact_, accessed 2026-10-08. <https://developers.google.com/people/api/rest/v1/people/updateContact>. "The server returns a 400 error with reason "failedPrecondition" if person.metadata.sources.etag is different than the contact's etag, which indicates the contact has changed since its data was read. Clients should get the latest person and merge their updates into the latest person."
- **[R15]** Microsoft, _Delete microsoftAuthenticatorAuthenticationMethod_, Microsoft Graph v1.0, accessed 2026-10-08. <https://learn.microsoft.com/en-us/graph/api/microsoftauthenticatorauthenticationmethod-delete?view=graph-rest-1.0>. `DELETE /me/authentication/microsoftAuthenticatorMethods/{microsoftAuthenticatorAuthenticationMethodId}`; request headers: `Authorization` only; "Don't supply a request body for this method." "When users manage their own authentication methods, the system prompts them to complete multi-factor authentication (MFA) if they last authenticated more than 10 minutes ago in the current session."
- **[R16]** Okta, _MyAccount Management_ API, OpenAPI specification version 2026.09.2, <https://github.com/okta/okta-management-openapi-spec/blob/master/dist/current/idp-minimal.yaml>, read 2026-10-08. "APIs for managing a user's own emails, phones, profile, and app authenticators." `DELETE /idp/myaccount/phones/{id}`, `deletePhone`: "Deletes the current user's phone information by ID", answering `204`. The specification defines no `If-Match` header and no reason parameter on any operation.
- **[R17]** OWASP, _Logging Cheat Sheet_, §Event attributes, accessed 2026-10-08. <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>. "The application logs must record "when, where, who and what" for each event"; among the attributes to consider, "Result status - whether the ACTION aimed at the OBJECT was successful" and "Reason - why the status above occurred e.g. User not authenticated in database check ..., Incorrect credentials".
- **[R18]** IETF RFC 3339, _Date and Time on the Internet: Timestamps_, July 2002. <https://www.rfc-editor.org/rfc/rfc3339.txt>. §5.6: "date-time = full-date "T" full-time", "full-time = partial-time time-offset", "time-offset = "Z" / time-numoffset". §3: "all dates and times used in Internet protocols MUST be fully qualified."
- **[R19]** Amazon Web Services, _LookupEvents_, AWS CloudTrail API Reference, accessed 2026-10-08. <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_LookupEvents.html>. StartTime: "Specifies that only events that occur after or at the specified time are returned." EndTime: "Specifies that only events that occur before or at the specified time are returned." NextToken: "This token must be passed in with the same parameters that were specified in the original call."
