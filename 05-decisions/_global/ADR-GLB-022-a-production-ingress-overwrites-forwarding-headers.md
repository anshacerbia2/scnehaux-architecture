---
doc_meta:
  id: ADR-GLB-022
  title: ADR-GLB-022 A Production Ingress Overwrites Client-Sent Forwarding Headers, and the Service Behind It Trusts One Hop
  adr_type: foundational
  status: accepted
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: Architecture Authority
  governed_by:
    - GDC-000
  authorizes: [STD-GLB-009]
---

# ADR-GLB-022: A Production Ingress Overwrites Client-Sent Forwarding Headers, and the Service Behind It Trusts One Hop

## 1. Title

A production ingress overwrites client-sent forwarding headers, and the service behind it trusts exactly one hop.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver               |
| :--------- | :------- | :----------- | :------------------------ | :--------------------- |
| 2026-10-24 | accepted | foundational | Architecture Review Board | Architecture Authority |

GDC-005 makes a governance artifact accepted when it is reviewed and merged by pull request. The owner's merge of the pull request that adds this decision is that act.

## 3. Context

`STD-GLB-009` governs the development server's deployment and one production ingress rule (the legacy realm endpoint, 2.0.0). It does not say how an ingress treats the headers that carry the client's address. identity-experience's TDD-001 1.24.0 §Enrolment From an Invitation (`ADR-IAM-011` §5.8) already records how its BFF reads the address and what the ingress in front of it must do, and reports that no document defines the ingress. A rate limit and an audit record that rest on the client address are only as good as that address.

Facts that bound the choice:

- **A forwarding header is client-writable.** RFC 7239 §8.1: the header "cannot be relied upon to be correct, as it may be modified, whether mistakenly or for malicious reasons, by every node on the way to the server, including the client making the request" [R1].
- **Whitelisting the proxies helps once, not along the chain.** RFC 7239 §8.1: verifying and whitelisting proxies "has at least two weaknesses. First, the chain of IP addresses listed before the request came to the proxy cannot be trusted. Second, unless the communication between proxies and the endpoint is secured, the data can be modified by an attacker with access to the network" [R1].
- **The address is personal data.** RFC 7239 §8.3: "The client's IP address, that may be forwarded in the "for" parameter of this header field, is considered to be privacy sensitive by many people" [R1].
- **Caddy replaces the values by default.** "By default, Caddy passes through incoming headers—including Host—to the backend without modifications, with three exceptions: It sets or augments the X-Forwarded-For header field. It sets the X-Forwarded-Proto header field. It sets the X-Forwarded-Host header field. For these X-Forwarded-\* headers, by default, the proxy will ignore their values from incoming requests, to prevent spoofing." [R2]. So other headers, `Forwarded` and `X-Real-IP` among them, reach the backend as the client sent them.
- **`trusted_proxies` turns the replacement off for the listed ranges.** "If Caddy is not the first server being connected to by your clients (for example when a CDN is in front of Caddy), you may configure trusted_proxies with a list of IP ranges (CIDRs) from which incoming requests are trusted to have sent good values for these headers." [R2]. It is a deliberate opt-in to a chain, and Caddy warns of the Cloudflare case: "you may be vulnerable to spoofing of the X-Forwarded-For header" [R2].
- **`header_up` can delete a header.** "header_up sets, adds (with the + prefix), deletes (with the - prefix), or performs a replacement ... in a request header going upstream to the backend"; "To delete a request header, preventing it from reaching the backend: header_up -Some-Header" [R2].
- **Keycloak's guide asks for overwrite, and says why.** "make sure your reverse proxy properly sets and overwrites the Forwarded or X-Forwarded-\* headers respectively"; "If these headers are incorrectly configured, rogue clients can inject false values and trick Keycloak into thinking the client is connecting from a different IP address than the actual one"; of the header family, "Overwrite these headers rather than stripping them" [R3]. That advice is for a backend that reads those headers.
- **Reading the wrong source is a weakness class.** MITRE CWE-348 describes it as using "the source that has less support for verification, is less trusted, or is less resistant to attack", and lists as observed examples a "Web product uses the IP address in the X-Forwarded-For HTTP header instead of a server variable that uses the connecting IP address, allowing filter bypass" [R4].

What the sources do not say: OWASP's cheat sheets say nothing on the matter (the Logging, Authentication, Denial of Service, HTTP Headers, Input Validation, Session Management, REST Security, Credential Stuffing Prevention and Forgot Password cheat sheets contain no mention of `X-Forwarded-For`, checked 2026-10-24), and no source says how many hops a service should trust. The count is this estate's choice, on the conservative reading below.

## 4. Decision Drivers

- The client address a service stores or limits on is the one its own edge accepted.
- The rule is checkable in the ingress configuration and in the service's tests.
- It costs a deployment one proxy and one setting.
- Where a source is silent, the conservative option wins.

## 5. Decision

### 5.1 The Ingress Overwrites Every Client-Sent Forwarding Header

A production ingress in front of a service that reads the client address MUST write that address itself and MUST NOT pass on a value a client sent:

- For each forwarding header it sets (`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`), the value is the ingress's own, replacing the client's. Caddy does this by default [R2]. The ingress declares no `trusted_proxies`, because that setting trusts an upstream chain, which §5.2 does not allow.
- For each other header of the family that the service does not read (`Forwarded`, `X-Real-IP`, `X-Original-Forwarded-For`), the ingress deletes it before the request goes upstream (`header_up -Forwarded`, `header_up -X-Real-IP`), because Caddy passes it through [R2].
- An ingress of another kind MUST give the same result: the service sees one address, written by the ingress, and no forwarding header a client wrote.

This follows Keycloak's "Overwrite these headers rather than stripping them" for a header the backend reads [R3]; a header no one reads is removed so that a later reader cannot be fed a forged one.

### 5.2 The Service Trusts Exactly One Hop

A service reads the client address from the forwarding header only on a connection from the one configured ingress address or range, and then it reads one value:

- **Nothing configured:** the service is the edge, and the client address is that of the connection.
- **One ingress configured:** on a connection from it, the address is the single `X-Forwarded-For` value the ingress wrote. On a connection from any other address, the header is not read.
- **A list, a second header, a value that is not an address, or no header** on a connection from the ingress is a misconfigured ingress. The service refuses the request and logs the fault, and does not guess.

No service reads the leftmost value of a list, and none counts hops. RFC 7239 §8.1: the chain before the proxy "cannot be trusted" [R1].

The BFF of identity-experience is the first case: `IDENTITY_EXPERIENCE_TRUSTED_INGRESS` names the ingress's address or CIDR range, and the BFF answers `503` for the misconfigured cases (TDD-identity-experience-001 1.24.0).

### 5.3 The Address Is Handled as Personal Data

A service passes the address on in the form its next hop needs and logs it only where a purpose requires it, as RFC 7239 §8.3 asks implementers and deployers to "consider whether, and how, deploying this extension affects user privacy" [R1].

### 5.4 Checks

`STD-GLB-009` §5: a production deployment pipeline sends a request with each of the forwarding headers set to a value of its own and asserts that the service saw the ingress's address, not the value sent. It runs once before the service serves anyone and again after every ingress upgrade. A service's tests assert the three cases of §5.2.

## 6. Consequences

### Positive

- A client cannot choose the address that a rate limit, a lockout or an audit record keeps.
- The rule is one proxy setting, one service setting and one test.

### Negative

- A deployment that wants a CDN or a second proxy in front of the ingress cannot trust its header under this rule. It records a new decision that names the chain and the way each hop is verified, and the standard is revised.
- A misconfigured ingress makes the service refuse requests instead of guessing.

### Operational

- The development server has no ingress in front of the BFF (identity-experience TDD-001 1.24.0, §Deployment Edge), so nothing is deployed under this rule yet; no production exists (`SAD-001` §9.1 and `SAD-004` §10.3). identity-experience's `deploy/dev` is where the first ingress would be declared, and its ROADMAP records it.

## 7. Compliance Impact

### Related Standards

- `STD-GLB-009` 4.0.0, §Security & Access Governance (the ingress rule) and §5 item 10, which this decision authorizes.
- [ADR-IAM-011](../identity-access-platform/ADR-IAM-011-an-invitee-without-an-account-enrols-at-redemption.md) §5.8: the first service that reads the address this way.

### Compliance Status

identity-experience's BFF complies with §5.2 (TDD-001 1.24.0). The ingress it needs is not deployed, so §5.1 and §5.4 are not yet met by any environment. Its TDD and ROADMAP cite this decision and `STD-GLB-009` as the place the ingress is governed.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Trust a chain: `trusted_proxies` and the rightmost untrusted entry

**Benefits:** allows a CDN or several proxies in front.

**Rejected because:** RFC 7239 says the chain before a proxy "cannot be trusted" [R1] and the estate has no such chain. Caddy's `trusted_proxies` is for "incoming requests ... trusted to have sent good values" [R2], and a range listed by mistake trusts every client in it.

### Alternative B — Read a header the ingress alone writes, and drop the forwarding family

**Benefits:** no list to parse, and no ambiguity about a leftmost value.

**Not chosen because:** it replaces a standard header with a private one in every service, and `X-Forwarded-For` is what Caddy writes by default [R2]. The one-value rule of §5.2 gives the same guarantee with the default configuration.

### Alternative C — Leave the ingress to each deployment

**Benefits:** no standard.

**Rejected because:** this is the gap. Without a rule, a deployment that adds `trusted_proxies` for convenience, or leaves `Forwarded` passing through, is conforming, and CWE-348 lists the resulting bypass [R4].

## 9. References

### Normative

- **[R1]** IETF RFC 7239, _Forwarded HTTP Extension_, §8.1 Header Validity and Integrity and §8.3 Privacy Considerations, June 2014. <https://www.rfc-editor.org/rfc/rfc7239.html#section-8>. "The "Forwarded" HTTP header field cannot be relied upon to be correct, as it may be modified, whether mistakenly or for malicious reasons, by every node on the way to the server, including the client making the request."; "One approach to ensure that the "Forwarded" HTTP header field is correct is to verify the correctness of proxies and to whitelist them as trusted. This approach has at least two weaknesses. First, the chain of IP addresses listed before the request came to the proxy cannot be trusted. Second, unless the communication between proxies and the endpoint is secured, the data can be modified by an attacker with access to the network."; "The client's IP address, that may be forwarded in the "for" parameter of this header field, is considered to be privacy sensitive by many people"; "Implementers and deployers of such proxies need to consider whether, and how, deploying this extension affects user privacy." Accessed 2026-10-24. RFC 7239 defines `Forwarded`; its reasoning is applied to `X-Forwarded-For` here by this decision.

### Informative

- **[R2]** Caddy, _reverse_proxy (Caddyfile directive)_, §Headers and §Defaults, accessed 2026-10-24. <https://caddyserver.com/docs/caddyfile/directives/reverse_proxy>. "header_up sets, adds (with the + prefix), deletes (with the - prefix), or performs a replacement (by using two arguments, a search and replacement) in a request header going upstream to the backend."; "To delete a request header, preventing it from reaching the backend: header_up -Some-Header"; "By default, Caddy passes through incoming headers—including Host—to the backend without modifications, with three exceptions: It sets or augments the X-Forwarded-For header field. It sets the X-Forwarded-Proto header field. It sets the X-Forwarded-Host header field. For these X-Forwarded-\* headers, by default, the proxy will ignore their values from incoming requests, to prevent spoofing."; "If Caddy is not the first server being connected to by your clients (for example when a CDN is in front of Caddy), you may configure trusted_proxies with a list of IP ranges (CIDRs) from which incoming requests are trusted to have sent good values for these headers."; "If you're using Cloudflare in front of Caddy, be aware that you may be vulnerable to spoofing of the X-Forwarded-For header."
- **[R3]** Keycloak, _Configuring a reverse proxy_, Server Guide, accessed 2026-10-24. <https://www.keycloak.org/server/reverseproxy>. "If either forwarded or xforwarded is selected, make sure your reverse proxy properly sets and overwrites the Forwarded or X-Forwarded-\* headers respectively."; "If these headers are incorrectly configured, rogue clients can inject false values and trick Keycloak into thinking the client is connecting from a different IP address than the actual one."; for Forwarded, X-Forwarded-For and the rest of the family, "Clients can spoof their IP address, protocol, or host, affecting access control and audit logging."; "Overwrite these headers rather than stripping them."
- **[R4]** MITRE, _CWE-348: Use of Less Trusted Source_, accessed 2026-10-24. <https://cwe.mitre.org/data/definitions/348.html>. "The product has two different sources of the same data or information, but it uses the source that has less support for verification, is less trusted, or is less resistant to attack."; observed example CVE-2004-1950: "Web product uses the IP address in the X-Forwarded-For HTTP header instead of a server variable that uses the connecting IP address, allowing filter bypass."
