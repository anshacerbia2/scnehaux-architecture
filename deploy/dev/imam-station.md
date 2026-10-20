# imam-station

The facts of one development server, imam-station, as recorded on 2026-10-07 and updated on 2026-10-16 and 2026-10-20. The rules are in [STD-GLB-009 §Development Server Deployment](../../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment). The procedure is the [development server runbook](README.md). This page records only what is specific to this host. It holds no secret: no password, token or key appears here, and none may be added.

## Host

| Fact      | Value                                                     |
| :-------- | :-------------------------------------------------------- |
| Host name | `imam-station`                                            |
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
| 8083 | organization-control                 |

## Dev tunnel

| Fact     | Value                                                      |
| :------- | :--------------------------------------------------------- |
| Tunnel   | `imam-keycloak.asse`                                       |
| Host     | systemd user service `devtunnel-keycloak.service`          |
| Watchdog | `devtunnel-keycloak-watchdog.timer`, every 5 minutes       |
| Issuer   | `https://gqr8l4jz-8080.asse.devtunnels.ms/realms/scnehaux` |
| Admin    | `https://gqr8l4jz-8081.asse.devtunnels.ms`                 |
| Expiry   | 30 days, as `devtunnel show` reports it                    |

| Port | Access                                               |
| :--- | :--------------------------------------------------- |
| 8080 | anonymous: the issuer, which browsers and BFFs reach |
| 8081 | owner only                                           |
| 8082 | owner only                                           |
| 5433 | owner only                                           |
| 8083 | owner only: organization-control, for a laptop's BFF |

The Admin Console is at `/admin/master/console/` on the admin host. It loads only after the kernel's `tunnel-admin.sh` has set the master realm's frontend URL to that host.

The unit files exist on this server only, in the user's systemd directory. They are in no repository.

## What is registered here

Recorded 2026-10-20, as the server's operator reported it. People are not named on this page: the repository is public, and a username is personal data.

| Fact                               | Value                                                                                                                                     |
| :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| organization-experience BFF client | `organization-experience-bff`, registered through identity-control in the `per-sign-in` form, for a laptop BFF at `http://127.0.0.1:8091` |
| First Tenant                       | `Scnehaux Dev`, `01a15393-acef-7000-9a70-24d78a5351d5`, `active` (provisioned through runbook step 9)                                     |
| Its first administrator            | a named development account, granted through runbook step 11; who it is is recorded on the server, not here                               |

## Local, uncommitted files

Each is a server's own override (STD-GLB-009 rule 4). They survive `git pull`, and a reset from zero keeps them (runbook step 15).

| File                                                    | Holds                                                                                                                                            |
| :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `identity-kernel/deploy/dev/compose.local.yaml`         | The subnet pins for the kernel's networks. The kernel's `.env` sets `COMPOSE_FILE` to include it, so the kernel runs with plain `docker compose` |
| `identity-control/deploy/dev/compose.override.yaml`     | `GOPROXY=direct` as a build argument, Postgres on `127.0.0.1:5433`, and the subnet pins                                                          |
| `organization-control/deploy/dev/compose.override.yaml` | The subnet pin for organization-control's `internal` network, copied from its example                                                            |

## Backups

The spare disk `/mnt/imam-storage` (1.8 TB) is the backup target: outside every Docker volume, as STD-GLB-009 rule 9 requires. Other projects share the disk, and its root is mode `777`, so ours live under one directory of their own, mode `700` and owned by `development`:

| Directory                                                 | Holds                                                       |
| :-------------------------------------------------------- | :---------------------------------------------------------- |
| `/mnt/imam-storage/scnehaux-backups/identity-kernel`      | `keycloak-<date>.dump`                                      |
| `/mnt/imam-storage/scnehaux-backups/identity-control`     | `globals-<date>.sql` and `identity_control-<date>.dump`     |
| `/mnt/imam-storage/scnehaux-backups/organization-control` | `globals-<date>.sql` and `organization_control-<date>.dump` |

`development`'s crontab, from each repository's §Backups and organization-control's §One-off tasks. The kernel's dump moves to 02:45, so it does not start with organization-control's. Every `<date>` is the UTC date, as both `backup.sh` scripts write it (`date -u +%F`), so one night's dumps share a name: run at 02:15 to 02:45 WIB, that is the previous day's date.

```text
15 2 * * * /home/development/apps/identity-control/deploy/dev/backup.sh /mnt/imam-storage/scnehaux-backups/identity-control >/dev/null
30 2 * * * /home/development/apps/organization-control/deploy/dev/backup.sh /mnt/imam-storage/scnehaux-backups/organization-control >/dev/null
45 2 * * * umask 077 && cd /home/development/apps/identity-kernel/deploy/dev && docker compose exec -T postgres pg_dump -U keycloak -d keycloak -Fc > /mnt/imam-storage/scnehaux-backups/identity-kernel/keycloak-$(date -u +\%F).dump
15 3 * * * cd /home/development/apps/organization-control/deploy/dev && docker compose run --rm maintenance >> "$HOME/organization-control-maintenance.log" 2>&1
```

These copy the databases alone. Each stack's `.env` and `keys/` are copied by hand when they change, with `sudo` for `keys/`, which belongs to the containers' users. Nothing rotates old dumps yet.
