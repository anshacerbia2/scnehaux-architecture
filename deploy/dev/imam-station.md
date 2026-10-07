# imam-station

The facts of one development server, imam-station, as recorded on 2026-10-07. The rules are in [STD-GLB-009 §Development Server Deployment](../../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment). The procedure is the [development server runbook](README.md). This page records only what is specific to this host. It holds no secret: no password, token or key appears here, and none may be added.

## Host

| Fact      | Value                                                     |
| :-------- | :-------------------------------------------------------- |
| Host name | `imam-station`                                            |
| OS        | Ubuntu                                                    |
| Docker    | 28, with Compose v2.33                                    |
| Checkouts | `/home/development/apps/<repository>`, one per repository |
| `pwsh`    | **not installed yet.** Runbook steps 5 to 7 need it       |

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
| `172.28.244.0/24` | reserved for organization-control `internal`       |

## Host ports

All on `127.0.0.1`:

| Port | Serves                                                                               |
| :--- | :----------------------------------------------------------------------------------- |
| 8080 | Caddy: the public issuer                                                             |
| 8081 | Keycloak directly: the Admin Console                                                 |
| 8082 | identity-control                                                                     |
| 5433 | identity-control's Postgres                                                          |
| 8083 | organization-control, planned: not deployed yet, and the tunnel has no port 8083 yet |

## Dev tunnel

| Fact     | Value                                                      |
| :------- | :--------------------------------------------------------- |
| Tunnel   | `imam-keycloak.asse`                                       |
| Host     | systemd user service `devtunnel-keycloak.service`          |
| Watchdog | `devtunnel-keycloak-watchdog.timer`, every 5 minutes       |
| Issuer   | `https://gqr8l4jz-8080.asse.devtunnels.ms/realms/scnehaux` |
| Admin    | `https://gqr8l4jz-8081.asse.devtunnels.ms`                 |

The unit files exist on this server only, in the user's systemd directory. They are in no repository.

## Local, uncommitted files

Each is a server's own override (STD-GLB-009 rule 4). They survive `git pull`, and a reset from zero keeps them (runbook step 10).

| File                                                | Holds                                                                                                                                            |
| :-------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `identity-kernel/deploy/dev/compose.local.yaml`     | The subnet pins for the kernel's networks. The kernel's `.env` sets `COMPOSE_FILE` to include it, so the kernel runs with plain `docker compose` |
| `identity-control/deploy/dev/compose.override.yaml` | `GOPROXY=direct` as a build argument, Postgres on `127.0.0.1:5433`, and the subnet pins                                                          |

## Backups

The spare disk `/mnt/imam-storage` (1.8 TB) is the intended backup target: outside every Docker volume, as STD-GLB-009 rule 9 requires.
