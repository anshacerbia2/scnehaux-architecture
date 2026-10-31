# dev-station

The facts of one development server, dev-station, as recorded on 2026-10-07 and updated on 2026-10-16, 2026-10-20 and 2026-10-25. The rules are in [STD-GLB-009 §Development Server Deployment](../../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment). The procedure is the [development server runbook](README.md). This page records only what is specific to this host. It holds no secret: no password, token or key appears here, and none may be added.

## Host

| Fact      | Value                                                     |
| :-------- | :-------------------------------------------------------- |
| Host name | `dev-station`                                             |
| OS        | Ubuntu                                                    |
| Docker    | 28.0, with Compose v2.33                                  |
| Checkouts | `/home/development/apps/<repository>`, one per repository |
| `pwsh`    | 7.6                                                       |

## Network

The corporate Sophos firewall inspects TLS to `proxy.golang.org`, `goproxy.io` and `goproxy.cn`, so module downloads through any of them fail. It does not inspect `github.com`, `go.googlesource.com` or `sum.golang.org`. So **every Go build here uses `GOPROXY=direct`**. Modules come from their origins and are still verified by `go.sum` and the checksum database (STD-GLB-009 rule 7).

## Neighbours on this host

Other workloads share the host. Nothing of ours binds outside `127.0.0.1` (STD-GLB-009 rule 6).

| Neighbour         | Uses                                   |
| :---------------- | :------------------------------------- |
| nginx             | `:443`                                 |
| host PostgreSQL   | `:5432`                                |
| dipanpillow (pm2) | ports 7071 to 7091, and 18071 to 18091 |
| scribe            | ports 3300 to 3500                     |
| microk8s, calico  | the calico subnet below                |

## Subnets

In use by others. **Never reuse them:**

| Subnet            | Used by   |
| :---------------- | :-------- |
| `10.1.173.0/26`   | calico    |
| `10.90.30.0/24`   | the LAN   |
| `172.17.0.0/16`   | `docker0` |
| `172.20.200.0/24` | VPN pool  |

Ours, pinned in the local override files below so Docker's address pools never land on a range in use:

| Subnet            | Network                                            |
| :---------------- | :------------------------------------------------- |
| `172.28.240.0/24` | identity-kernel `internal`                         |
| `172.28.241.0/24` | `scnehaux-identity-api` (the kernel's api network) |
| `172.28.242.0/24` | identity-control `internal`                        |
| `172.28.243.0/24` | `scnehaux-identity-control-api`                    |
| `172.28.244.0/24` | organization-control `internal`                    |

## Host ports

All on `127.0.0.1`:

| Port | Serves                               |
| :--- | :----------------------------------- |
| 8080 | Caddy: the public issuer             |
| 8081 | Keycloak directly: the Admin Console |
| 8082 | identity-control                     |
| 5433 | identity-control's Postgres          |
| 8025 | identity-control's Mailpit interface |
| 8083 | organization-control                 |

## Dev tunnel

| Fact     | Value                                                      |
| :------- | :--------------------------------------------------------- |
| Tunnel   | `dev-keycloak.asse`                                        |
| Host     | systemd user service `devtunnel-keycloak.service`          |
| Watchdog | `devtunnel-keycloak-watchdog.timer`, every 5 minutes       |
| Issuer   | `https://gqr8l4jz-8080.asse.devtunnels.ms/realms/scnehaux` |
| Admin    | `https://gqr8l4jz-8081.asse.devtunnels.ms`                 |
| Expiry   | 30 days, as `devtunnel show` reports it                    |

| Port | Access                                                 |
| :--- | :----------------------------------------------------- |
| 8080 | anonymous: the issuer, which browsers and BFFs reach   |
| 8081 | owner only                                             |
| 8082 | owner only: identity-control, for a laptop's BFF       |
| 5433 | owner only                                             |
| 8025 | owner only: identity-control's Mailpit, to read a code |
| 8083 | owner only: organization-control, for a laptop's BFF   |

The Admin Console is at `/admin/master/console/` on the admin host. It loads only after the kernel's `tunnel-admin.sh` has set the master realm's frontend URL to that host.

The unit files exist on this server only, in the user's systemd directory. They are in no repository.

## What is registered here

Recorded 2026-10-20, as the server's operator reported it. People are not named on this page: the repository is public, and a username is personal data.

| Fact                               | Value                                                                                                                                                                                                                                                                                                                                                             |
| :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| organization-experience BFF client | `organization-experience-bff`, registered through identity-control in the `per-sign-in` form, for a laptop BFF at `http://127.0.0.1:8091`                                                                                                                                                                                                                         |
| Device clients                     | One registration per developer device (STD-GLB-009 rule 15). The client above serves one laptop. A second device gets its own client, added here as a row with its device name. An identity BFF device's clients, `identity-experience-bff-<device>` and the enrolment workload `identity-experience-enrolment-<device>` (runbook step 4), are added the same way |
| First Tenant                       | `Scnehaux Dev`, `01a15393-acef-7000-9a70-24d78a5351d5`, `active` (provisioned through runbook step 9)                                                                                                                                                                                                                                                             |
| Its first administrator            | a named development account, granted through runbook step 11; who it is is recorded on the server, not here                                                                                                                                                                                                                                                       |

## Local, uncommitted files

Each is a server's own override (STD-GLB-009 rule 4). They survive `git pull`, and a reset from zero keeps them (runbook step 15).

| File                                                    | Holds                                                                                                                                            |
| :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `identity-kernel/deploy/dev/compose.local.yaml`         | The subnet pins for the kernel's networks. The kernel's `.env` sets `COMPOSE_FILE` to include it, so the kernel runs with plain `docker compose` |
| `identity-control/deploy/dev/compose.override.yaml`     | `GOPROXY=direct` as a build argument, Postgres on `127.0.0.1:5433`, and the subnet pins                                                          |
| `organization-control/deploy/dev/compose.override.yaml` | The subnet pin for organization-control's `internal` network, copied from its example                                                            |

## Signing keystore

The realm's signing key was made by the signing-key ceremony before the kernel's first start (runbook step 2.2, identity-kernel `docs/runbooks/signing-key-ceremony.md`). On this host it is held as identity-kernel's `deploy/dev/README.md` §Keys describes:

| File, under `identity-kernel/deploy/dev/keys/` | Holds                                                        | Custody                                                                                     |
| :--------------------------------------------- | :----------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| `signing/realm-signing-<kid>.p12`              | the PKCS#12 keystore, one RSA-3072 key pair                  | owned by 1000, the kernel's user, mode 0400, in a directory of mode 0500; mounted read-only |
| `vault/scnehaux_realm-signing-<kid>`           | its password, for Keycloak's file vault                      | the same                                                                                    |
| `realm-signing-<kid>.crt`                      | its certificate, the public half                             | root, mode 0644                                                                             |
| `realm-signing-<kid>.ceremony.json`            | the ceremony record: operator, witness, reason, times, `kid` | root, mode 0644; a copy is attached to the change ticket, never pasted in chat              |

- **One copy, on this host's disk only.** The keystore and its vault file are never copied: not to `/mnt/dev-storage`, not with `.env` and `keys/`, not to the ticket (STD-GLB-009 rule 9, `ADR-IAM-002 §5.3`). NIST SP 800-57 gives the backup of a private signature key as "No (in general)" (`ADR-IAM-002` [R6]).
- **Its protection here is access control.** Only root and the kernel's container user can read it, and the kernel mounts it read-only. The people who hold root on this host can read it; that is accepted for a development server and nowhere else.
- **A lost or damaged keystore is not restored.** The kernel refuses to start without it (identity-kernel `docs/runbooks/custody-outage.md`), and the server is rebuilt from zero (runbook step 15) with a new ceremony and a new `kid`. Every development token signed before then fails.
- Each later key is made by the same ceremony and moved in and out of service by identity-kernel `docs/runbooks/signing-key-rotation.md`, so more than one keystore can be here during a rotation. A key's files are removed only by its retirement, abandonment or revocation.
- The ceremony's operator, witness and reviewer are recorded in the ceremony record and on the change ticket, not on this page.

## Backups

The spare disk `/mnt/dev-storage` (1.8 TB) is the backup target: outside every Docker volume, as STD-GLB-009 rule 9 requires. Other projects share the disk, and its root is mode `777`, so ours live under one directory of their own, mode `700` and owned by the operator's account:

| Directory                                                | Holds                                                       |
| :------------------------------------------------------- | :---------------------------------------------------------- |
| `/mnt/dev-storage/scnehaux-backups/identity-kernel`      | `globals-<date>.sql` and `keycloak-<date>.dump`             |
| `/mnt/dev-storage/scnehaux-backups/identity-control`     | `globals-<date>.sql` and `identity_control-<date>.dump`     |
| `/mnt/dev-storage/scnehaux-backups/organization-control` | `globals-<date>.sql` and `organization_control-<date>.dump` |

The operator's crontab, from each repository's §Backups and organization-control's §One-off tasks. Every stack's line runs its `backup.sh`, never a bare `pg_dump`. The kernel's runs at 02:45, so it does not start with organization-control's. Every `<date>` is the UTC date, as every `backup.sh` writes it (`date -u +%F`), so one night's sets share a name: run at 02:15 to 02:45 WIB, that is the previous day's date.

```text
15 2 * * * /home/development/apps/identity-control/deploy/dev/backup.sh /mnt/dev-storage/scnehaux-backups/identity-control >/dev/null
30 2 * * * /home/development/apps/organization-control/deploy/dev/backup.sh /mnt/dev-storage/scnehaux-backups/organization-control >/dev/null
45 2 * * * /home/development/apps/identity-kernel/deploy/dev/backup.sh /mnt/dev-storage/scnehaux-backups/identity-kernel >/dev/null
15 3 * * * cd /home/development/apps/organization-control/deploy/dev && docker compose run --rm maintenance >> "$HOME/organization-control-maintenance.log" 2>&1
```

- **Each `backup.sh` keeps the newest 14 complete sets, by count,** and deletes older ones only after the new set is in place. A failed or silent backup deletes nothing. Each writes its files as `.partial` and renames them only when complete.
- **The kernel's `backup.sh` never copies the signing keystore or its vault file** (§Signing keystore). Its restore drill checks that no keystore file, password or private key is in the backup.
- These copy the databases alone. Each stack's `.env` and `keys/` are copied by hand when they change, with `sudo` for `keys/`, which belongs to the containers' users. The kernel's copy excludes `keys/signing` and `keys/vault`, as identity-kernel §Backups shows.

Gap on this host, against STD-GLB-009 rule 9 (1.10.0):

- **No copy leaves the host.** `/mnt/dev-storage` is a disk in this machine, so the off-site copy of CISA's 3-2-1 rule is not met. This server is redeployed from zero, so the gap is accepted here; production must meet it.
