# Development Server Runbook

This page takes a development server from an empty host to the three Scnehaux stacks running and wired, with both BFFs signing in from a laptop. It also covers updating the server, resetting it, and restoring it.

It says what to do in which order, across repositories. Each repository's `deploy/dev/README.md` owns the details: the exact commands, the variables, and what each script checks. Each step names the README section to follow. The rules every `deploy/dev` follows, and their sources, are [STD-GLB-009 §Development Server Deployment](../../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment). One server's own facts, such as its addresses, ports, subnets and tunnel, are on its environment page, for example [imam-station](imam-station.md).

The repositories:

| Repository              | Kind            | `deploy/dev`                                                                                     |
| :---------------------- | :-------------- | :----------------------------------------------------------------------------------------------- |
| identity-kernel         | server-deployed | [README](https://github.com/anshacerbia2/identity-kernel/blob/main/deploy/dev/README.md)         |
| identity-control        | server-deployed | [README](https://github.com/anshacerbia2/identity-control/blob/main/deploy/dev/README.md)        |
| organization-control    | server-deployed | [README](https://github.com/anshacerbia2/organization-control/blob/main/deploy/dev/README.md)    |
| identity-experience     | laptop-run      | [deploy/dev](https://github.com/anshacerbia2/identity-experience/tree/main/deploy/dev)           |
| organization-experience | laptop-run      | [README](https://github.com/anshacerbia2/organization-experience/blob/main/deploy/dev/README.md) |

A section name below in the form "identity-control §First start" means that heading in that repository's `deploy/dev/README.md`. A repository whose README does not yet have the skeleton's headings has the same content under its older heading, named in brackets.

## 0. Prerequisites

On the server:

- **Docker with Compose v2** (`docker compose`, not `docker-compose`), and your user in the `docker` group.
- **PowerShell 7 (`pwsh`).** The procedure scripts are PowerShell, because CI runs the same files: identity-control's `scripts/dev-token.ps1`, `dev-smoke.ps1` and `dev-adopt-bff.ps1`, and organization-control's `scripts/dev-wire.ps1` and `dev-wiring-proof.ps1`. A server without `pwsh` cannot run steps 5 to 7 as written.
- **The devtunnel CLI**, logged in with the account that will own the tunnel: `devtunnel user login -g -d` (GitHub, device code).
- **Git checkouts** of identity-kernel, identity-control and organization-control.
- **Somewhere outside Docker for backups**, such as a second disk (STD-GLB-009 rule 9).

On each laptop that runs a BFF: Node.js, `pwsh`, a local PostgreSQL for the BFF's sessions, and the devtunnel CLI, logged in with the same account when the laptop needs an owner-only port.

## 1. The dev tunnel

The tunnel is how anything off the server reaches it. Every stack publishes on `127.0.0.1` only (STD-GLB-009 rule 6). Follow identity-kernel [§Behind a dev tunnel instead of a DNS name]: it has the commands and the five mistakes to avoid.

| Port | Serves                                    | Access                                | `--origin-header unchanged` |
| :--- | :---------------------------------------- | :------------------------------------ | :-------------------------- |
| 8080 | Caddy, then Keycloak: the public issuer   | anonymous                             | yes                         |
| 8081 | Keycloak directly, with the Admin Console | owner only                            | yes                         |
| 8082 | the Identity Control API                  | owner only                            | no                          |
| 8083 | the Organization Control API              | owner only                            | no                          |
| 5433 | identity-control's Postgres               | owner only, only for a laptop replica | no                          |

- **Persistent, never temporary.** `devtunnel create` once. The tunnel's host is the issuer, so a new tunnel means a new issuer for every token and every application's configuration.
- **Anonymous access on port 8080 alone:** `devtunnel access create <tunnel> -p 8080 --anonymous`.
- **Ports 8082, 8083 and 5433** are added without `--anonymous`, for example `devtunnel port create <tunnel> -p 8082`. Step 3 needs 8082 only to call identity-control from off the server, and 5433 only for a laptop replica (identity-control [§Running the code from a laptop]).
- **Host it as a systemd user service, with lingering enabled** (`loginctl enable-linger <user>`), so it starts at boot and survives logouts. Add a **watchdog timer** that requests the issuer's public discovery URL and restarts the service when it stops answering, because the host can lose its relay while its process stays alive (STD-GLB-009 rule 10). The unit files are on the server and in no repository. Their names are on the environment page.

## 2. identity-kernel

Follow identity-kernel §First start, in tunnel mode as [§Behind a dev tunnel instead of a DNS name] describes:

1. Copy `.env.example` to `.env`. `KEYCLOAK_HOSTNAME` is the tunnel's host for port 8080, without `https://`.
2. Start the stack. When `.env` sets `COMPOSE_FILE` to list the tunnel file and a local file, run plain `docker compose up -d --wait`, with no `-f` (pitfall 12). Otherwise run `docker compose -f compose.yaml -f compose.tunnel.yaml up -d --wait`.
3. `docker compose logs realm-apply`. It ends in `applied revision ...`.
4. `./new-client-key.sh realm-apply`, then `./create-apply-client.sh`. Put the line it prints in `.env`, then start the stack again.
5. `./tunnel-admin.sh`, so the Admin Console's login stays on port 8081 (pitfall 6).

The issuer is now `https://<KEYCLOAK_HOSTNAME>/realms/scnehaux`.

## 3. identity-control, and the ceremony once

Follow identity-control §Before you start and §First start. In order:

1. Copy `.env.example` to `.env`, and fill in `KEYCLOAK_ISSUER` (the issuer of step 2, exactly), the passwords, `KC_BOOTSTRAP_ADMIN_PASSWORD` copied from the kernel's `.env`, and `KERNEL_DEPLOY_DIR`.
2. Run `./create-kernel-clients.sh >> .env`, then `./create-registration-client.sh`, then `./create-security-ref-key.sh`.
3. `docker compose up -d --build`, then `curl -fsS http://127.0.0.1:8082/readyz`.
4. `./bootstrap.sh "<you>" "<reason>"`. **The ceremony succeeds once per Control Database.** A second run is refused by design.

A network that intercepts TLS to the Go module proxy breaks the build at `go mod download`. Set `GOPROXY=direct` (STD-GLB-009 rule 7). Until the repository's compose passes `GOPROXY` from `.env`, it goes in a local `compose.override.yaml` (identity-control §First start).

## 4. The identity-experience BFF client

The BFF runs on a laptop and signs in as its own confidential client, `identity-experience-bff`, with a key the laptop makes. Its README is identity-experience's `deploy/dev` (the script's header until the README exists).

1. **On the laptop:** `node scripts/new-client-key.mjs`. The private key stays there, and only the public JWK leaves.
2. **On the server:** a new server registers the client through identity-control's `POST /v1/registrations` as `privileged`, in the `provider-scope` form. `create-bff-client.sh` is superseded, and it refuses a client that exists. A server whose client the script already made adopts it in step 6.
3. **More than one device.** The kernel's `set-client-key.sh` sets a client's whole key set at once, and takes one or two JWKs: `./set-client-key.sh scnehaux identity-experience-bff laptop-a.jwk.json laptop-b.jwk.json`. A third device replaces one of the two. Once the client is adopted, its keys belong to its registration. A key is then added through identity-control (`POST /v1/registrations/{registration_id}/keys`, as organization-experience §Rotating the key shows), not by `set-client-key.sh`. identity-control treats a key that its registration does not declare as a wrong declaration.

The redirect URI is `http://127.0.0.1:8090/auth/callback`, on `127.0.0.1` and not `localhost:8080` (pitfall 7).

## 5. The operator's TOTP

Every provider route requires `acr` `aal2`: a password and a TOTP code. Follow identity-control [§Two factors for providers, on a server that ran before them].

1. **The owner enrolls first, in a browser.** Sign in to the Admin Portal. It asks for `aal2`, and the kernel shows the enrollment page. Scan the QR code with an authenticator app.
2. **Then the server gets its own TOTP** for the bootstrap operator, because nobody can relay a 30-second code to an agent. Follow identity-control [§The server's own TOTP for the bootstrap operator]. `Get-ScnehauxToken` from `scripts/dev-token.ps1`, with `-EnrollTotpFile deploy/dev/keys/operator-totp.json` and `-Otp <the owner's current code>`, signs in at `aal2` and enrolls a second TOTP labelled `dev-server`. It writes the secret to that file, mode 0600, never prints it, and refuses when the file exists. Later tokens use `-TotpSecretFile` with the same path.

## 6. Adopt the caller and the BFF, then disable unmanaged clients

Two clients were made by scripts before identity-control could register clients: `identity-control-caller` (by `create-kernel-clients.sh`) and, on an older server, `identity-experience-bff` (by `create-bff-client.sh`). Both are adopted, as `privileged` in the `provider-scope` form, never `internal`. Follow identity-control [§Adopting the BFF].

1. **The BFF:** `pwsh ./scripts/dev-adopt-bff.ps1 -BffJwkFile <the BFF's public JWK>` shows the plan. Add `-Apply` to adopt.
2. **The caller:** today its declaration is only in identity-control's `scripts/dev-smoke.ps1`, step 9b (`application_ref` `identity-control-dev`, redirect `http://127.0.0.1:8099/callback`, audience `identity-control-api`, converging `token_format` and `audience_scope`). Send that declaration to `POST /v1/registrations:adopt`, first with `dry_run`, then for real. The identity-control README is gaining a step of its own for it.
3. **Then** set `IDENTITY_UNMANAGED_CLIENTS=disable` in identity-control's `.env`, and recreate the service with `docker compose up -d identity-control`. A restart keeps the environment the container was created with. Done before both adoptions, this disables the BFF and every open session, or the caller.

## 7. organization-control, and the wiring

Follow organization-control §Before you start, §First start, and §Wiring to other services.

1. Copy `.env.example` to `.env`. Fill in `KEYCLOAK_ISSUER` (the value identity-control's `.env` holds) and the six passwords. Then `docker compose up -d --build` and `curl -fsS http://127.0.0.1:8083/readyz`.
2. The wiring is two scripts, the files CI runs. Export `IDENTITY_CALLER_PASSWORD`, `IDENTITY_CALLER_KEY_FILE` and `IDENTITY_OPERATOR_TOTP_FILE` alone, never by sourcing identity-control's `.env`. Then run `pwsh ./scripts/dev-wire.ps1 -IdentityRepo <identity-control checkout> -KernelDeployDir <kernel deploy/dev> -Operator "<you>" -State <state file>` and `pwsh ./scripts/dev-wiring-proof.ps1 -IdentityRepo <identity-control checkout> -State <state file>`. Keep the state file's directory outside every directory a container mounts. It receives a private key.
3. Schedule the daily `maintenance` task (organization-control §One-off tasks). It exits 3 on a security incident open for more than 24 hours.

**Never run `docker compose down -v` in organization-control after this.** The wiring retires the ceremony's own grant in identity-control. From then on the operator is a provider through organization-control's database alone, and a new database revokes that grant everywhere.

## 8. The organization-experience BFF client

Follow organization-experience §Registering it (§The client lists every property).

1. **On the laptop:** `node scripts/new-client-key.mjs`.
2. **The operator** registers `organization-experience-bff` with `POST /v1/registrations`, as `privileged` in the `per-sign-in` form, with audience `organization-control-api` and redirect `http://127.0.0.1:8091/auth/callback`.
3. **Port 8091,** because the identity BFF has 8090. The two still share one cookie, `__Host-ident_session`. A browser scopes cookies by host and not by port, so signing in to one BFF signs the browser out of the other. Use one BFF at a time, or two browser profiles (organization-experience §Before running both BFFs at once).

## 9. Updating

Always in dependency order: **identity-kernel, then identity-control, then organization-control**. Each is updated with the same two commands, in its `deploy/dev`:

```sh
git pull && docker compose up -d --build
```

Then check each one before the next:

| Stack                | Check                                                                                                                                    |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| identity-kernel      | `docker compose logs realm-apply` ends in `applied revision ...`. A refusal (exit 2) lists drift (identity-kernel [§Changing the realm]) |
| identity-control     | `docker compose logs migrate` succeeded, and `curl -fsS http://127.0.0.1:8082/readyz`                                                    |
| organization-control | `docker compose logs migrate` succeeded, and `curl -fsS http://127.0.0.1:8083/readyz`                                                    |

A release that needs more than this says so in its README, in a section between the skeleton's own sections (for example identity-control [§Moving a server to `identity-control-api`]).

## 10. Reset from zero

A reset destroys the three databases. It is the one procedure that runs `docker compose down -v`, and only when the owner has decided on it.

1. **Back up first** (step 11's forms): each database, the roles, `.env` and `keys/` of every stack.
2. **Take the stacks down in reverse dependency order**, because each one joins the networks of the stacks before it: `docker compose down -v` in organization-control, then identity-control, then identity-kernel.
3. **Remove `.env` and `keys/`** from each stack. The private keys belong to container users (65532, 65534) and are mode 0600, so removing them needs root.
4. **Keep the local overrides** (`compose.override.yaml`, and the kernel's local file) **and keep the tunnel.** The issuer URL then stays the same, and nothing configured with it changes.
5. Run steps 2 to 8 again.

What the owner redoes afterwards:

- **The owner's TOTP:** the user is new, so the authenticator entry for it is stale. Delete it from the app and enroll again (step 5.1). The server's `operator-totp.json` went with `keys/`, so step 5.2 runs again too.
- **The BFFs' public JWKs:** the laptops keep their private keys. Each sends its public JWK again for steps 4 and 8.
- **The laptop's session store:** the BFF's sessions name users, clients and tokens of the old realm. Clear the session store in the database `IDENTITY_EXPERIENCE_DEV_DATABASE_URL` names (identity-experience's `.env`), and the organization BFF's likewise.

## 11. Restore from a backup

STD-GLB-009 rule 9 says what a backup holds, and each repository's §Backups gives its exact commands. The order is the same for every stack:

1. Put `.env` and `keys/` back first. The migrate job sets the login roles' passwords from `.env`, so it and the restored roles must agree.
2. Start the database alone: `docker compose up -d postgres`.
3. Restore the roles from the `pg_dumpall --globals-only` file with `psql`, then each database from its `pg_dump -Fc` file with `pg_restore`. The roles come first, because the objects' owners must already exist.
4. `docker compose up -d --build`. The migrate job applies anything newer than the backup, and the service starts once it has succeeded.

Restore the stacks in dependency order, kernel first. A restored organization-control database brings its provider grants back, and with them the provider authority that identity-control projects from them.

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
