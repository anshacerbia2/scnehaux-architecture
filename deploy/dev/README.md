# Development Server Runbook

This page takes a development server from an empty host to the three Scnehaux stacks running and wired, with both BFFs signing in from a laptop. It also covers updating the server, resetting it, and restoring it.

It says what to do in which order, across repositories. Each repository's `deploy/dev/README.md` owns the details: the exact commands, the variables, and what each script checks. Each step names the README section to follow. The rules every `deploy/dev` follows, and their sources, are [STD-GLB-009 §Development Server Deployment](../../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment). One server's own facts, such as its addresses, ports, subnets and tunnel, are on its environment page, for example [imam-station](imam-station.md).

The repositories:

| Repository              | Kind            | `deploy/dev`                                                                                     |
| :---------------------- | :-------------- | :----------------------------------------------------------------------------------------------- |
| identity-kernel         | server-deployed | [README](https://github.com/anshacerbia2/identity-kernel/blob/main/deploy/dev/README.md)         |
| identity-control        | server-deployed | [README](https://github.com/anshacerbia2/identity-control/blob/main/deploy/dev/README.md)        |
| organization-control    | server-deployed | [README](https://github.com/anshacerbia2/organization-control/blob/main/deploy/dev/README.md)    |
| identity-experience     | laptop-run      | [README](https://github.com/anshacerbia2/identity-experience/blob/main/deploy/dev/README.md)     |
| organization-experience | laptop-run      | [README](https://github.com/anshacerbia2/organization-experience/blob/main/deploy/dev/README.md) |

A section name below in the form "identity-control §First start" means that heading in that repository's `deploy/dev/README.md`. Those READMEs are current, and this page gives the order and the hand-offs, never a copy of their commands. When a command here and in a README differ, the README is right and this page is the one to fix. The step numbers below are cited by those READMEs (identity-experience's client is step 4, organization-experience's is step 8), so a new step is added as a sub-item and never renumbers one.

Every image build on the server sets `BUILD_REVISION=$(git rev-parse HEAD)`, for example `BUILD_REVISION=$(git rev-parse HEAD) docker compose up -d --build`. It records the commit as the image's `org.opencontainers.image.revision` label (`unknown` without it), and each repository's `deploy-dev` sets it and checks it.

## Where each part runs

| Part                                                                                                | Runs on               | Notes                                                                                                            |
| :-------------------------------------------------------------------------------------------------- | :-------------------- | :--------------------------------------------------------------------------------------------------------------- |
| identity-kernel: Keycloak, Caddy, `realm-apply`, and the signing keystore                           | the server            | Docker only. Its scripts are `bash`; no `pwsh`                                                                   |
| identity-control: the API, its database, and Mailpit, the development mail catcher (`smtp-catcher`) | the server            | `pwsh` for its scripts. Mailpit's interface is on `127.0.0.1:8025`, and its SMTP is on the internal network only |
| organization-control: the API, its database, its dispatcher and sweeps                              | the server            | `pwsh` for the wiring and the stand-in scripts                                                                   |
| The dev tunnel and its watchdog                                                                     | the server            | The only way anything off the server reaches it                                                                  |
| The operator's procedure scripts: adoption, registration, wiring, provisioning, obligations         | the server            | They call the APIs on `127.0.0.1`, from the checkouts there                                                      |
| identity-experience BFF, on `127.0.0.1:8090`, with its session store                                | each developer laptop | No compose stack on the server. Reaches the kernel on port 8080 and identity-control on owner-only 8082          |
| organization-experience BFF, on `127.0.0.1:8091`, with its session store                            | each developer laptop | Reaches the kernel on port 8080 and organization-control on owner-only 8083                                      |
| Each BFF's private key and sign-in client                                                           | its laptop            | One client and one key per device. Only the public JWK leaves the laptop                                         |

foundation-reference has no `deploy/dev`, and nothing of it runs on a server or a laptop.

## 0. Prerequisites

On the server:

- **Docker with Compose v2** (`docker compose`, not `docker-compose`), and your user in the `docker` group.
- **PowerShell 7 (`pwsh`).** The procedure scripts are PowerShell, because CI runs the same files: identity-control's `scripts/dev-token.ps1`, `dev-adopt-caller.ps1` and `dev-production-switches.ps1`, organization-control's `scripts/dev-wire.ps1`, `dev-wiring-proof.ps1`, `dev-provisioning.ps1`, `dev-obligation.ps1` and `dev-deprovisioning.ps1`, organization-experience's `scripts/dev-register-bff.ps1`, and identity-experience's `scripts/dev-wire-enrolment.ps1`. A server without `pwsh` cannot run steps 4 to 9 and 13 as written. The kernel needs Docker alone.
- **The devtunnel CLI**, logged in with the account that will own the tunnel: `devtunnel user login -g -d` (GitHub, device code).
- **Git checkouts** of identity-kernel, identity-control and organization-control, and, for the operator's scripts, of identity-experience and organization-experience.
- **Somewhere outside Docker for backups**, such as a second disk (STD-GLB-009 rule 9).
- **Two people and a change ticket for the ceremonies.** The kernel's signing-key ceremony (step 2) and identity-control's bootstrap ceremony (step 3) each need an operator and a witness, never the same person, and a third person, the reviewer, reviews each record (STD-IAM-001 §3.10). Registering the first signing key in identity-control (step 3.5) needs the operator and a second holder of the ceremony role as approver, who for the activation is also not the key's generating operator (identity-kernel `docs/runbooks/signing-key-rotation.md` §Who performs it). The ticket's identifier is each ceremony's reason, and the records are kept with it. Who they are is the owner's decision and is never written in a public repository (identity-control `docs/runbooks/bootstrap-ceremony.md` §Who performs it).

On each laptop that runs a BFF: Node.js 24 and pnpm 10, `pwsh` (for `scripts/dev-local.ps1`), a local PostgreSQL for the BFF's sessions, and the devtunnel CLI, logged in with the same account when the laptop needs an owner-only port.

## 1. The dev tunnel

The tunnel is how anything off the server reaches it. Every stack publishes on `127.0.0.1` only (STD-GLB-009 rule 6). Follow identity-kernel [§Behind a dev tunnel instead of a DNS name]: it has the commands and the five mistakes to avoid.

| Port | Serves                                    | Access                                | `--origin-header unchanged` |
| :--- | :---------------------------------------- | :------------------------------------ | :-------------------------- |
| 8080 | Caddy, then Keycloak: the public issuer   | anonymous                             | yes                         |
| 8081 | Keycloak directly, with the Admin Console | owner only                            | yes                         |
| 8082 | the Identity Control API                  | owner only                            | no                          |
| 8083 | the Organization Control API              | owner only                            | no                          |
| 5433 | identity-control's Postgres               | owner only, only for a laptop replica | no                          |
| 8025 | identity-control's Mailpit interface      | owner only, only to read a code       | no                          |

- **Persistent, never temporary.** `devtunnel create` once. The tunnel's host is the issuer, so a new tunnel means a new issuer for every token and every application's configuration.
- **Anonymous access on port 8080 alone:** `devtunnel access create <tunnel> -p 8080 --anonymous`.
- **Ports 8082, 8083, 5433 and 8025** are added without `--anonymous`, for example `devtunnel port create <tunnel> -p 8082`. The identity BFF on a laptop needs 8082, and the organization BFF needs 8083. 5433 is only for a laptop replica (identity-control [§Running the code from a laptop]), and 8025 only to read a proof code from a laptop (identity-control [§Reading a code in the mail catcher]).
- **Host it as a systemd user service, with lingering enabled** (`loginctl enable-linger <user>`), so it starts at boot and survives logouts. Add a **watchdog timer** that requests the issuer's public discovery URL and restarts the service when it stops answering, because the host can lose its relay while its process stays alive (STD-GLB-009 rule 10). The unit files are on the server and in no repository. Their names are on the environment page.

## 2. identity-kernel

Follow identity-kernel §First start, in tunnel mode as [§Behind a dev tunnel instead of a DNS name] describes:

1. Copy `deploy/dev/.env.example` to `deploy/dev/.env`. `KEYCLOAK_HOSTNAME` is the tunnel's host for port 8080, without `https://`.
2. **The signing-key ceremony, before the first `up`.** With the operator and the witness both present, from the root of the identity-kernel checkout, follow identity-kernel `docs/runbooks/signing-key-ceremony.md` (identity-kernel §First start):

   ```sh
   scripts/signing-key-ceremony.sh deploy/dev/keys "<operator>" "<witness>" "<change ticket>"
   ```

   It makes the realm's signing keystore in the pinned image with no network. Every file is named by the key's `kid`: the keystore is `deploy/dev/keys/signing/realm-signing-<kid>.p12`, its password is `deploy/dev/keys/vault/scnehaux_realm-signing-<kid>`, and its certificate and the ceremony record, with the `kid`, are beside them (`keys/realm-signing-<kid>.crt`, `keys/realm-signing-<kid>.ceremony.json`; identity-kernel §Keys). It refuses a witness equal to the operator and a keys directory that already holds a keystore. **The kernel refuses to start without the keystore** (`ADR-IAM-002 §5.3`), so this step comes before item 3. The witness reads the record it prints.

3. Start the stack, with `BUILD_REVISION=$(git rev-parse HEAD)` set for the build. When `.env` sets `COMPOSE_FILE` to list the tunnel file and a local file, run plain `docker compose up -d --wait`, with no `-f` (pitfall 12). Otherwise run `docker compose -f compose.yaml -f compose.tunnel.yaml up -d --wait`.
4. `docker compose logs realm-apply`. It ends in `applied revision ... signs with the custody key`.
5. **The witness compares the `kid`.** `curl -fsS https://<KEYCLOAK_HOSTNAME>/realms/scnehaux/protocol/openid-connect/certs` lists exactly one `PS256` key, whose `kid` is the record's. Any other `PS256` key, such as `fallback-PS256`, stops the ceremony (identity-kernel `docs/runbooks/custody-outage.md`). Attach the record and the terminal output to the change ticket, never to chat. The reviewer reviews them there.
6. `./new-client-key.sh realm-apply`, then `./create-apply-client.sh`. Put the line it prints in `.env`, then start the stack again.
7. `./tunnel-admin.sh`, so the Admin Console's login stays on port 8081 (pitfall 6).
8. **Schedule the daily backup** in the operator's crontab, as identity-kernel §Backups gives it:

   ```text
   45 2 * * * <identity-kernel checkout>/deploy/dev/backup.sh <backup directory>/identity-kernel >/dev/null
   ```

   `backup.sh` writes the roles and the database as one set, verifies the dump, and keeps the newest 14 complete sets by count. **It never copies the signing keystore or its vault file** (STD-GLB-009 rule 9). Check it runs: the line is in `crontab -l`, `journalctl -u cron` shows today's run, and today's set is in the directory.

The issuer is now `https://<KEYCLOAK_HOSTNAME>/realms/scnehaux`. The keystore stays in `deploy/dev/keys/signing` until a rotation retires it. A lost one is not restored: the server is built from zero (step 15), with a new ceremony and a new `kid`.

`realm-apply` made this first key active on the empty realm. It is registered in identity-control's registry once identity-control runs (step 3.5), and every later key is staged, activated and retired by identity-kernel `docs/runbooks/signing-key-rotation.md`, never by hand.

## 3. identity-control, and the ceremony once

Follow identity-control §Before you start and §First start. In order:

1. Copy `.env.example` to `.env`, and fill in `KEYCLOAK_ISSUER` (the issuer of step 2, exactly), the passwords, `KC_BOOTSTRAP_ADMIN_PASSWORD` copied from the kernel's `.env`, and `KERNEL_DEPLOY_DIR`. **Keep `IDENTITY_NOTIFICATION_DELIVERY=smtp-catcher`**, which `.env.example` sets: the stack's Mailpit, the development mail catcher, then receives every account security notification, proof codes included, and relays nothing. A code is read in its interface on `127.0.0.1:8025` (step 10.5).
2. Run `./create-kernel-clients.sh >> .env`, then `./create-registration-client.sh`, then `./create-security-ref-key.sh`.
3. `BUILD_REVISION=$(git rev-parse HEAD) docker compose up -d --build`, then `curl -fsS http://127.0.0.1:8082/readyz`.
4. `./bootstrap.sh "<operator>" "<witness>" "<reason>"`, with both people present (identity-control `docs/runbooks/bootstrap-ceremony.md`, STD-IAM-001 §3.10). The witness is required and is never the operator: `identity-bootstrap` and the database both refuse the same name, compared trimmed and case-folded. The reason names the change ticket. Keep the printed output, with the `principal_id`, with that ticket. **The ceremony succeeds once per Control Database.** A second run is refused by design; a ceremony that failed after creating its Principal is resumed, never rerun (identity-control §One-off tasks).
5. **Register the kernel's first signing key.** The key `realm-apply` made active (step 2) is staged, approved and activated in identity-control's registry with the three `scripts/signing-key-rotation.sh` commands of identity-kernel `docs/runbooks/signing-key-rotation.md` §The first key, run from the kernel's checkout with `IDENTITY_CONTROL_DEPLOY_DIR` set. The `kid` is the one in the ceremony record. The operator and a second ceremony-role holder, the approver, are present; the approver is never the operator or the key's generating operator. The activation finds the key already active and alone, and changes nothing in the realm. Identity-control's `signing-key` task, which the script runs, is behind a profile and never starts with `up` (identity-control §One-off tasks).
6. **Schedule the daily backup:** identity-control §Backups gives the cron line for its `backup.sh`, which keeps the newest 14 complete sets.

The ceremony's record is reviewed later, in step 7, by a third person: the reviewer reads it with a provider's sign-in, and Organization Control grants that only once it is wired.

A network that intercepts TLS to the Go module proxy breaks the build at `go mod download`. Set `GOPROXY=direct` (STD-GLB-009 rule 7). Until the repository's compose passes `GOPROXY` from `.env`, it goes in a local `compose.override.yaml` (identity-control §First start).

## 4. The identity-experience BFF client, and its enrolment workload

The BFF runs on a laptop and signs in as its own confidential client, with a key the laptop makes. **One client per device**: `identity-experience-bff-<device>`, for example `identity-experience-bff-ada-laptop` (STD-GLB-009 rule 15, `ADR-IAM-001 §5.12`). Follow identity-experience §First start. The registrations of items 2 to 4 are provider calls at `aal2`, so they are sent once step 5.1 has bound the server's TOTP. Make the keys now, register in step 5.2. Until item 2 is registered, no browser can sign in: the owner's own TOTP waits for it (step 5.3).

1. **On the laptop:** `node scripts/new-client-key.mjs`. The private key stays there, and only the public JWK leaves.
2. **On the server, the operator registers the client.** On a new server the client does not exist, so identity-experience §First start step 2, "It does not exist (a new server)", registers it through identity-control's `POST /v1/registrations` as `privileged`, in the `provider-scope` form, with audience `identity-control-api` and the redirect URI below. `create-bff-client.sh` is superseded and never run on a server built from zero. The laptop sets `IDENTITY_EXPERIENCE_CLIENT_ID` to its own client.
3. **Each further device registers its own client** the same way, with its own key and the same redirect URI. A registration holds one active key, and a second only while a rotation overlaps, so `set-client-key.sh` is never given two devices' keys and one client is never adopted with two devices' keys (identity-control §Several developer devices). A key is rotated through identity-control (`POST /v1/registrations/{registration_id}/keys`, as organization-experience §Rotating the key shows). A device that is lost is suspended without touching the others. Record each device's client on the server's environment page.
4. **The enrolment workload, for the enrolment page** (identity-experience §First start, step 4; `ADR-IAM-011 §5.8`). A person invited to a Tenant who holds no account enrols from the invitation, and the BFF calls identity-control's enrolment routes as a workload of its own, never with a person's token. It is optional: without it the page says that enrolment is unavailable. Each device has its own, `identity-experience-enrolment-<device>`:
   - **On the laptop:** `node scripts/new-client-key.mjs identity-experience-enrolment`, and send the public JWK.
   - **On the server, the operator** runs identity-experience's `scripts/dev-wire-enrolment.ps1 -IdentityRepo <identity-control checkout> -Device <device> -JwkFile <the public JWK>`, with the secrets identity-control's `dev-smoke.ps1` reads. It creates the workload (`POST /v1/workloads`) and admits it as an enrolment caller (`POST /v1/enrolment-callers`), the steps of identity-control §Enrolment from an invitation, and prints the client. `GET /v1/enrolment-callers` lists the record.
   - **On the laptop,** the printed client goes in `.env` as `IDENTITY_EXPERIENCE_ENROLMENT_CLIENT_ID`, and `./scripts/dev-local.ps1` runs again.
   - The page resolves the invitation through organization-control, which step 7.2 wires (item 6c). Without that entry an enrolment is counted and answered `503`.

The redirect URI is `http://127.0.0.1:8090/auth/callback`, on `127.0.0.1` and not `localhost:8080` (pitfall 7).

## 5. The operator's TOTP, then the owner's

Every provider route requires `acr` `aal2`: a password and a TOTP code. On a server from zero the server's TOTP comes first and the owner's second, because no browser can sign in until a provider call at `aal2` has registered the identity BFF's client ([ADR-IAM-004 §5.5](../../05-decisions/identity-access-platform/ADR-IAM-004-authentication-assurance-and-step-up.md#55-a-development-servers-operator-automation)).

1. **The server's TOTP, on the first adoption run.** From identity-control's checkout, run the adoption plan with `IDENTITY_OPERATOR_TOTP_FILE=deploy/dev/keys/operator-totp.json` (identity-control §First start, step 8). The bootstrap operator holds no second factor yet, so that sign-in binds a TOTP labelled `dev-server` at the account's level, `aal1`, and writes its secret to the file, mode 0600, never printed. Every later script in identity-control's `scripts/` finds the file without being told. The plan changes nothing else; step 6.1 applies it.
2. **Send steps 4.2 to 4.4 now.** The operator's scripts sign in at `aal2` with the server's TOTP.
3. **The owner's own TOTP, in a browser.** On the laptop, with the identity BFF running against its new client, sign in to the account application (`http://127.0.0.1:8090/account/`), and choose **Add an authenticator app**. The step-up asks for a code: read one computed from the server's TOTP, on the server, in your own session (identity-control §The server's own TOTP for the bootstrap operator). Never relay it through chat or a ticket. The kernel's page then shows the QR code: scan it with your authenticator app. From then on the browser signs in with your own code.

A server where the owner's TOTP is bound already, and the server's file is missing, binds the server's at `aal2` with one of the owner's codes instead (identity-control §The server's own TOTP for the bootstrap operator).

## 6. Adopt the caller, then end in the production settings

One client was made by a script before identity-control could register clients: `identity-control-caller`, by `create-kernel-clients.sh`. It is adopted, as `privileged` in the `provider-scope` form, never `internal`. The BFFs are registered in steps 4 and 8, so there is nothing of them to adopt. Follow identity-control §First start, steps 8 to 11.

1. **The caller:** from the repository root, with `.env` loaded, `pwsh ./scripts/dev-adopt-caller.ps1` shows the plan (its first run, in step 5.1, also bound the server's TOTP), and `-Apply` adopts it. It converges `token_format` and `audience_scope`. A `redirect_uris` or `client_keys` difference means the declaration is wrong and is fixed there, never in the console.
2. **The drift check:** `GET /v1/registrations:drift` with a provider token answers no findings. A finding is applied with `POST /v1/registrations:reconcile`, with its reason (identity-control §First start, step 10).
3. **End in the production settings.** Put `IDENTITY_UNMANAGED_CLIENTS=disable` and `IDENTITY_TOKEN_TYPE=enforce` in identity-control's `.env`, and recreate the service with `docker compose up -d identity-control`. A restart keeps the environment the container was created with. Done before the caller is adopted, `disable` disables it, and `enforce` refuses tokens typed `JWT`. Then `pwsh ./scripts/dev-production-switches.ps1` checks the result, as `deploy-dev` does on every change.

## 7. organization-control, and the wiring

Follow organization-control §Before you start, §First start, and §Wiring to other services.

1. Copy `.env.example` to `.env`. Fill in `KEYCLOAK_ISSUER` (the value identity-control's `.env` holds) and the six passwords. Copy `compose.override.example.yaml` to `compose.override.yaml` (the subnet pin), and set `GOPROXY=direct` where the proxy is intercepted. Then `BUILD_REVISION=$(git rev-parse HEAD) docker compose up -d --build` and `curl -fsS http://127.0.0.1:8083/readyz`.
2. The wiring is two scripts, the files CI runs (`dev-wire.ps1` is organization-control §Wiring to other services, steps 1 to 6c; `dev-wiring-proof.ps1` is step 7). Export `IDENTITY_CALLER_PASSWORD`, `IDENTITY_CALLER_KEY_FILE` and `KEYCLOAK_ISSUER` alone, never by sourcing identity-control's `.env`; the operator's TOTP file is found in the identity-control checkout (step 5.1). Then run `pwsh ./scripts/dev-wire.ps1 -IdentityRepo <identity-control checkout> -KernelDeployDir <kernel deploy/dev> -Operator "<you>" -State <state file>`. For the proof, also export `KC_BOOTSTRAP_ADMIN_PASSWORD` and `KC_ADMIN_URL`, where the kernel's `/admin` answers: `http://127.0.0.1:8081` on a tunnel-mode server, because the public port 8080 answers `404` on `/admin` there (identity-kernel `deploy/dev/Caddyfile.tunnel`); the script's default, `http://localhost:8080`, is CI's. Then run `pwsh ./scripts/dev-wiring-proof.ps1 -IdentityRepo <identity-control checkout> -KernelDeployDir <kernel deploy/dev> -State <state file>` (organization-control §Wiring to other services). Keep the state file's directory outside every directory a container mounts. It receives private keys.
   - **The development reporters are registered here** (organization-control §Wiring to other services, step 6b; `ADR-ORG-001 §5.11`). Organization Control admits a provisioning or obligation report only from a reporter on record. For each of `provisioning`, `obligation:product`, `obligation:hcm`, `obligation:billing` and `obligation:audit`, `dev-wire.ps1` makes a key pair beside the state file, creates a workload `dev-reporter-<what it reports>` in identity-control, registers it with `POST /v1/reporters`, and writes its client and key file into the state file. The stand-in scripts of steps 9 and 13 report as these reporters. `GET /v1/reporters` lists them.
   - **identity-control's invitation resolve is admitted here too** (step 6c; `ADR-IAM-011 §5.7`). identity-control asks Organization Control, as its own workload, which invitation a token names when a person with no account enrols. That workload, step 2's `identity-control-workload`, is admitted to `POST /v1/invitations/resolve` alone, from its own `invitation:resolve` reporter entry: the consumer registration of step 4 does not cover it, because each route has its own entry. `dev-wire.ps1` registers it and writes it into the state file's `reporters`, with identity-control's key file. Each resolve writes a privileged-access row with the authority `reporter`, reviewed through the workload's owner.
   - **Step 5 of the wiring** also sets `ORGANIZATION_IDENTITY_CONTROL_URL`, where invitation acceptance asks whether the signed-in person holds the invited address. Without it `POST /v1/invitations/accept` answers `503`. Identity-control's own side, `IDENTITY_ORGANIZATION_BASE_URL`, is set in step 6 of the same section; without it an enrolment request is counted and answered `503`.
3. Schedule the daily `maintenance` task in your crontab, with the line organization-control §One-off tasks gives. It exits 3 on a security incident open for more than 24 hours. **Check that it runs** (STD-GLB-009 rule 14), with that section's three checks: `crontab -l` shows the line; `systemctl status cron` reads `active (running)`; and the maintenance log in your home directory is from today, or `journalctl -u cron --since today` shows the run. cron reads a changed crontab by itself, so nothing is restarted after `crontab -e`. Schedule organization-control's `backup.sh` too, with the line its §Backups gives.
4. **The bootstrap ceremony's review is step 10.6.** The reviewer needs a credential and a TOTP (step 10), and their provider grant is made in organization-experience, whose client step 8 registers. Until the review is recorded, the realm serves no one but the first Principal and the reviewer (STD-IAM-001 §3.10), so the reviewer is the first person step 10 creates, and nobody else is created before the review.

**Never run `docker compose down -v` in organization-control after this.** The wiring retires the ceremony's own grant in identity-control. From then on the operator is a provider through organization-control's database alone, and a new database revokes that grant everywhere.

**An `Idempotency-Key` is remembered for 7 days.** Both services purge a completed key, with the answer recorded under it, 7 days after it completed, through foundation-platform v0.5.0's `idempotency.PurgeCompleted` (STD-GLB-001 §Commands Require an `Idempotency-Key`). organization-control purges in its daily `maintenance` (item 3), and identity-control in its scheduled sweep. Within the window, a retry with the same key answers the recorded result. After it, the same key is a new command: a creation creates again, and a command whose own state refuses a repeat, such as a second ceremony, still refuses it. An uncompleted key is never purged. Retry a failed command within the 7 days, and never reuse a key from an earlier run.

## 8. The organization-experience BFF client

Follow organization-experience §Registering it (§The client lists every property).

1. **On the laptop:** `node scripts/new-client-key.mjs`.
2. **The operator** registers `organization-experience-bff` (a second device's client has its own name, item 3) with organization-experience's `scripts/dev-register-bff.ps1`, which sends `POST /v1/registrations` as `privileged` in the `per-sign-in` form, with audience `organization-control-api` and redirect `http://127.0.0.1:8091/auth/callback`. organization-experience's `stack-proof` workflow runs the same script (STD-GLB-009 §A procedure step is a script, and CI runs it).
3. **A second device registers its own client,** for example `organization-experience-bff-<device>`, with the same script, and sets `ORGANIZATION_EXPERIENCE_CLIENT_ID` to it (STD-GLB-009 rule 15).
4. **The BFF's `.env`** names the identity BFF's origin in `ORGANIZATION_EXPERIENCE_IDENTITY_EXPERIENCE_ORIGIN`, `http://127.0.0.1:8090` as `.env.example` sets it. The BFF never calls it. The invitation acceptance page links a person with no account to `<origin>/account/enrol#<token>` (`ADR-IAM-011 §5.1`), and the BFF refuses to start without the variable. The BFF reaches organization-control through the tunnel's owner-only port 8083, on `127.0.0.1:8083` after `devtunnel connect`.
5. **Port 8091,** because the identity BFF has 8090. The two still share one cookie, `__Host-ident_session`. A browser scopes cookies by host and not by port, so signing in to one BFF signs the browser out of the other. Use one BFF at a time, or two browser profiles (organization-experience §Before running both BFFs at once).

## 9. Provisioning a Tenant

A Tenant is created `requested` and becomes `active` only after the provisioning system reports that its boundary exists (SAD-004 §5.1, §7.5). **No provisioning system runs on a development server.** The operator stands in for it with organization-control's `scripts/dev-provisioning.ps1`, which reports the outcome through the same routes the provisioning system calls, as the development provisioning reporter that step 7.2 registered. The decision is recorded in [SAD-004 §7.5](../../04-system/scnehaux-organization/scnehaux-organization-control.sad.md#75-provisioning) (2.4.0), with its sources and the options rejected, and detailed in organization-control's `TDD-organization-control-003` §The Provisioning System on a Development Server. Follow organization-control §Provisioning a Tenant on the development server. In order:

1. **In organization-experience, in provider mode:** request the Tenant (Tenants, Request tenant), then **Start provisioning** on its row. The row shows the request's correlation identifier.
2. **On the server**, from organization-control's checkout, with the wiring's variables exported (step 7.2): `pwsh ./scripts/dev-provisioning.ps1 -IdentityRepo <identity-control checkout> -State <state file> -TenantId <tenant_id> -Realized`. It refuses, sending nothing, a Tenant that is not `provisioning` or a request that already has an outcome. `-Failed -Reason "<why>"` tries the failure path; the row then offers **Retry provisioning**.
3. **In organization-experience:** **Activate** on its row. The Tenant is `active`, and Memberships can be granted into it.

**A request older than 30 minutes reads `unresolved`** ("outcome unknown, do not retry"): organization-control's sweep ages every request with no outcome, including one nobody dispatched. It is resolved by reporting its outcome, never by a retry (organization-control `TDD-organization-control-003` §Resolving an `unresolved` Request). Start provisioning is still allowed on a `requested` Tenant, and the script accepts an `unresolved` request. organization-control's `deploy-dev` runs the script on every change.

## 10. Creating a person who can sign in

A person a provider creates in the Admin Portal has `UPDATE_PASSWORD` outstanding and no credential. They get a first credential by [ADR-IAM-010](../../05-decisions/identity-access-platform/ADR-IAM-010-first-credential-for-an-administrator-created-person.md): a temporary password identity-control generates and shows once (identity-control `docs/runbooks/first-credential-handover.md`). Do not set passwords through the kernel's Admin Console or copy `bootstrap.sh` or organization-experience's `e2e/seed.ps1`: they go around the Identity Control API and leave no evidence.

1. **In the Admin Portal, as a provider at `aal2`:** create the person with a username and an email, then **Issue a temporary password**. The value is shown once, with its lapse (24 hours). Nothing stores it; leaving the panel clears it.
2. **Give the value to the person** on a channel other than the one that carries the username. On a development server, the owner reads it and gives it to the person directly.
3. **The person signs in** with the username and the temporary password. The kernel requires a new password and refuses the temporary value as the new one (identity-kernel `passwordHistory`). A sign-in at `aal2` then enrolls a TOTP authenticator and shows the recovery codes (ADR-IAM-005 §5.3).
4. **A lost or lapsed value:** the person's page offers **Issue a new temporary password** while the person has set no password of their own. An unused value is deleted when it lapses.
5. **The email is not proven yet.** To be invited (step 12), the person proves it in the Account application: **Send a code**, then enter the code. On a development server the code reaches the development mail catcher (ADR-IAM-007 §5.3), whose UI identity-control publishes on `127.0.0.1:8025` (identity-control §Reading a code in the mail catcher). From a laptop, add port 8025 to the tunnel as owner-only (step 1). Never relay a code in a ticket or a chat.
6. **On a server from zero, the first person is the bootstrap ceremony's reviewer,** and the review is recorded before anyone else is created (STD-IAM-001 §3.10, identity-control `docs/runbooks/bootstrap-ceremony.md` §Review). The reviewer is neither the operator, the witness nor the first Principal's holder.
   1. **Create the reviewer** with items 1 to 3. Their first sign-in at `aal2` enrolls their TOTP.
   2. **In organization-experience, in provider mode:** grant `provider:identity-control` to the reviewer's `principal_id`, `eligible`, with a reason. An eligible grant confers nothing until the reviewer activates it and another provider, the owner, approves the activation in **Approvals** ([ADR-ORG-002 §5.1](../../05-decisions/organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md), organization-control `TDD-organization-control-001` §Provider Activation).
   3. **The reviewer, in the Admin Portal:** Governance, **Bootstrap ceremony**. Check the record against the change ticket as the ceremony runbook's §Review lists, then **Record review**, `satisfactory` or `findings`, with the finding as the reason. The route and the database refuse a review by the operator, the witness or the first Principal, and the review is insert-only.
   4. `findings` starts an incident, and nobody else is created until the owner decides.

## 11. The first Tenant administrator

A Tenant is `active` after step 9, and nobody can sign in for it until a provider grants its first administrator (ADR-ORG-003 §5.2). The grant also gives that person a Tenant-wide Membership, in the same transaction.

1. **The person can sign in:** step 10.
2. **In organization-experience, in provider mode:** Tenants, **Administrators** on the Tenant's row, **Grant administrator**, with the person's `principal_id` from the Admin Portal and a reason.
3. **The person signs in for the Tenant** in organization-experience. A Tenant administrator's token is `aal2` (ADR-ORG-003 §5.3), so the first sign-in enrolls their TOTP if they have none.

## 12. Inviting a member

An invitation is accepted by the invited person, signed in as themselves, with an email they have proven ([ADR-ORG-007](../../05-decisions/organization-tenancy-platform/ADR-ORG-007-the-invited-person-accepts-signed-in.md)). Granting a Membership directly (the Tenant's Memberships, **Grant membership**) remains available for a person who exists.

1. **The person exists, can sign in, and has proven the invited email** (step 10, items 1 to 5). An address counts only once its holder has returned the code sent to it (ADR-ORG-007 §5.3).
   - _A person with no account_ enrols from the invitation instead ([ADR-IAM-011](../../05-decisions/identity-access-platform/ADR-IAM-011-an-invitee-without-an-account-enrols-at-redemption.md)): the acceptance page links to the identity BFF's enrolment page, `http://127.0.0.1:8090/account/enrol#<token>`. It needs the enrolment workload (step 4.4) and organization-control's `invitation:resolve` entry (step 7.2), and the code reaches the mail catcher. Otherwise create the person first (step 10).
2. **In organization-experience, in the Tenant, as its administrator:** invite the email. The page shows the acceptance link once; the token travels only in its fragment. On a development server nothing delivers it, so give it to the person yourself.
3. **The person opens the link** and signs in without choosing a Tenant. The page accepts the invitation for the signed-in person only, then offers to sign in to the new Tenant. Any refusal (unknown or expired link, an address not proven, a link meant for someone else) reads the same.
4. **A lost link** is revoked and issued again.

## 13. Offboarding a Tenant on the development server

An offboarding waits on two parties that do not run on a development server: the domains that own its obligations, which resolve them, and the provisioning system, which reports the outcome of the deprovisioning that release sends. You stand in for both with two organization-control scripts, through the routes those parties call, as the development reporters that step 7.2 registered (SAD-004 §7.5, 2.5.0; STD-GLB-009 rule 13). Follow organization-control §Offboarding a Tenant on the development server:

1. **In organization-experience, in provider mode:** **Begin offboarding** on the Tenant's row, complete the freeze, and **Raise obligation** for each one the Tenant owes.
2. **On the server**, from organization-control's checkout, with the wiring's variables exported (step 7.2): `pwsh ./scripts/dev-obligation.ps1` resolves one obligation as the domain it was raised against (`-Completed`, or `-Waived` or `-Failed` with `-Reason`). The console offers no such control, on purpose.
3. **In organization-experience:** **Release**, once no obligation is open or failed and no legal hold is set. It is irreversible.
4. **On the server:** `pwsh ./scripts/dev-deprovisioning.ps1 -OffboardingId <id> -Realized` reports the outcome (or `-Failed -Reason "<why>"`, then the console's **Send deprovisioning again**). It never retires and never resends.
5. **In organization-experience:** **Retire**.

Each script reads first and refuses, sending nothing, a transition the service would refuse, and says what to do instead. organization-control's `deploy-dev` runs both on every change.

## 14. Updating

Always in dependency order: **identity-kernel, then identity-control, then organization-control**. Each is updated with the same two commands, in its `deploy/dev`:

```sh
git pull && BUILD_REVISION=$(git rev-parse HEAD) docker compose up -d --build
```

Then check each one before the next:

| Stack                | Check                                                                                                                                    |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| identity-kernel      | `docker compose logs realm-apply` ends in `applied revision ...`. A refusal (exit 2) lists drift (identity-kernel [§Changing the realm]) |
| identity-control     | `docker compose logs migrate` succeeded, and `curl -fsS http://127.0.0.1:8082/readyz`                                                    |
| organization-control | `docker compose logs migrate` succeeded, and `curl -fsS http://127.0.0.1:8083/readyz`                                                    |

A release that needs more than this is taken by standing the server up again from zero (step 15), which every environment is: identity-control's README keeps no in-place upgrade procedure either. The realm signing key is the one thing rotated in place, every 30 days, by identity-kernel `docs/runbooks/signing-key-rotation.md`, with an operator and an approver.

## 15. Reset from zero

A reset destroys the three databases. It is the one procedure that runs `docker compose down -v`, and only when the owner has decided on it.

1. **Back up first** (step 16's forms): each database, the roles, `.env` and `keys/` of every stack, except the kernel's signing keystore and its vault files, which are never copied (STD-GLB-009 rule 9).
2. **Take the stacks down in reverse dependency order**, because each one joins the networks of the stacks before it: `docker compose down -v` in organization-control, then identity-control, then identity-kernel.
3. **Remove `.env` and `keys/`** from each stack. The private keys belong to container users (65532, 65534, and 1000 for the kernel's keystore) and are mode 0600 or 0400, so removing them needs root. The kernel's `keys/` holds the signing keystore, so step 2 runs the signing-key ceremony again.
4. **Keep the local overrides** (`compose.override.yaml`, and the kernel's local file) **and keep the tunnel.** The issuer URL then stays the same, and nothing configured with it changes.
5. Run steps 2 to 8 again.

What the owner redoes afterwards:

- **Both ceremonies, with their reviews:** the signing-key ceremony (step 2.2) gives the realm a new `kid`, so every token signed before the reset fails; the bootstrap ceremony (step 3.4) and its review (step 10.6) run on the new Control Database.
- **The owner's TOTP:** the user is new, so the authenticator entry for it is stale. Delete it from the app. The server's `operator-totp.json` went with `keys/`, so step 5 runs again in its order: the server's TOTP first (5.1), then the owner's (5.3).
- **The BFFs' public JWKs:** the laptops keep their private keys. Each sends its public JWK again for steps 4 and 8.
- **The laptop's session store:** the BFF's sessions name users, clients and tokens of the old realm. Clear the session store in the database `IDENTITY_EXPERIENCE_DEV_DATABASE_URL` names (identity-experience's `.env`), and the organization BFF's likewise.

## 16. Restore from a backup

STD-GLB-009 rule 9 says what a backup holds, and each repository's §Backups gives its exact commands. The order is the same for every stack:

1. Put `.env` and `keys/` back first. The migrate job sets the login roles' passwords from `.env`, so it and the restored roles must agree. The kernel's signing keystore is not in the backup and stays where it is, in `keys/signing` and `keys/vault`: the restored realm loads it under the same `kid`. A server whose keystore is lost is not restored. It is built from zero (step 15), with a new ceremony and a new `kid` (`ADR-IAM-002 §5.3`).
2. Start the database alone: `docker compose up -d postgres`.
3. Restore the roles from the `pg_dumpall --globals-only` file with `psql`, then each database from its `pg_dump -Fc` file with `pg_restore`. The roles come first, because the objects' owners must already exist.
4. `docker compose up -d --build`. The migrate job applies anything newer than the backup, and the service starts once it has succeeded.

Each of the three stacks does steps 2 and 3 with one script, `./restore.sh <roles file> <dump>`, which refuses a stack that already holds the database. Their `deploy-dev` jobs run it in a restore drill against a stack whose volume they have deleted (STD-GLB-002 §Restore Evidence). The kernel's drill also checks that the backup holds no keystore file, password or private key, and that the restored realm signs under the same `kid`.

Restore the stacks in dependency order, kernel first. A restored organization-control database brings its provider grants back, and with them the provider authority that identity-control projects from them. organization-control's `restore.sh` also runs its `restore-bump` stage before the service serves: every Tenant `version`, Tenant security version and provider grant version gains 10^9, the withdrawn ones are published, and every consumer is asked to reconcile (`ADR-ORG-003 §5.5`).

## Known pitfalls

Each of these was hit on the real server.

1. **Compose passes a container only the variables it lists.** A variable set in `.env` that `compose.yaml` does not list is ignored, and nothing says so. Check `compose.yaml` before trusting a setting (STD-GLB-009 rule 8).
2. **A profiled one-off image is not rebuilt by `up --build` unless it reuses the migrate image.** Profiled services are not enabled by `up`, so a task with its own build kept an old image. An old ceremony image demanded `IDENTITY_KEYCLOAK_CLIENT_SECRET` long after client secrets were gone. Every task now runs the migrate image by name (STD-GLB-009 §Development Server Deployment, Compose).
3. **`--origin-header unchanged` is a per-port setting**, made with `devtunnel port create` or `devtunnel port update`, not a flag of `devtunnel host`. Without it, the tunnel rewrites the browser's `Origin`, and Keycloak answers `403` "Invalid origin" to a single-page application's token request.
4. **`devtunnel access create --port` is refused** by the CLI on the server. The flag is `-p`, or `--port-number`. Microsoft's own command reference shows `--port`.
5. **`devtunnel host` can lose the relay and fail its token refresh while staying alive.** systemd sees the service active, so `Restart=` never fires. The watchdog timer of step 1 catches it from outside.
6. **Tunnel mode needs the master realm's `frontendUrl` set to `KEYCLOAK_ADMIN_URL`** (`tunnel-admin.sh`). Otherwise the Admin Console's login form posts to the public port, which answers `404`.
7. **Keycloak's hostname is fixed.** Log in on the public origin, never on `127.0.0.1:8081`, or Keycloak answers "Restart login cookie not found" (identity-control [§Calling the API]). For laptop callbacks, use `127.0.0.1`, not `localhost`.
8. **A non-ASCII `X-Administrative-Reason`** used to reach PostgreSQL as invalid UTF-8 and fail as an unexplained `503`. It is now refused with `400` (STD-GLB-001 §Request Header Values). Write reasons in plain ASCII.
9. **realm-apply has to parse the recorded baseline by its structure, not by today's policy.** The realm on the server was applied at `6beb86d`, before a later policy rule existed. Its own baseline then no longer parsed ("scnehaux.json must set eventsEnabled true"), and every later apply was refused. Fixed in identity-kernel#58.
10. **Account lockout.**
    - _What was seen:_ the server locked an account permanently after 10 failed logins.
    - _Why:_ that realm was last applied at identity-kernel `6beb86d`, whose definition declared no brute-force settings at all. The behaviour came from settings the definition did not declare, made in the console or left from earlier.
    - _What applies on a current definition_ (identity-kernel `realm/scnehaux.json`, TDD-identity-kernel-001 §Guessing Limits): the 10th consecutive failure brings the first **temporary** lockout (`failureFactor` 10). The wait grows by `waitIncrementSeconds` 60 up to `maxFailureWaitSeconds` 900 (strategy `MULTIPLE`). After `maxTemporaryLockouts` 90 temporary lockouts, the 100th consecutive failure brings a **permanent** lockout.
    - _To release a lock:_ a permanent lockout disables the user. Enable the user again, in the Admin Console or through identity-control's assisted recovery (suspend, revoke any lost factor, restore). A temporary lockout ends when its wait runs out. Keycloak keeps the failure counts in memory, so a restart also clears them.
11. **realm-apply refuses console drift** (exit 2, changing nothing). A change made in the Admin Console is either reverted or committed to `realm/` and adopted once (identity-kernel [§Changing the realm]).
12. **Run the kernel with plain `docker compose` when `.env` sets `COMPOSE_FILE`.** `-f` flags replace that list, so a command run with them leaves out the local file, along with the subnet pins it holds.
