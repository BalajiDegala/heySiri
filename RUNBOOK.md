# heySiri Runbook

This runbook documents the current deployment approach only:

- the app runs on one Docker host
- other machines on the same LAN open it as `http://heysiri.d2-india.com:8090`
- client machines resolve that name through their `hosts` file
- plain HTTP is used for now

## Quick Start

On the Docker host:

```tcsh
cd /dd/ayon/git/heySiri
mkdir -p data/media
touch data/db.sqlite3
chmod 666 data/db.sqlite3
chmod 777 data data/media
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
docker build -t heysiri:prod .
docker compose up -d
docker compose ps
```

On each client machine, add this `hosts` entry:

```text
<docker-host-lan-ip> heysiri.d2-india.com
```

Then open:

```text
http://heysiri.d2-india.com:8090
```

## Current Topology

- Docker host runs the app and Caddy
- Caddy listens on host port `8090`
- Caddy reverse proxies `http://heysiri.d2-india.com:8090` to the Django app
- client machines map `heysiri.d2-india.com` to the Docker host LAN IP

## Shell Notes

You are using `tcsh`, so use `setenv`.

Example:

```tcsh
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
```

Unset a variable with:

```tcsh
unsetenv DJANGO_SECRET_KEY
```

## Files Used

- [compose.yaml](/dd/ayon/git/heySiri/compose.yaml)
- [Caddyfile.local](/dd/ayon/git/heySiri/Caddyfile.local)
- [Dockerfile](/dd/ayon/git/heySiri/Dockerfile)
- [docker-entrypoint.sh](/dd/ayon/git/heySiri/docker-entrypoint.sh)

## Prerequisites

- Docker daemon access on the machine that will host the app
- `docker compose` available
- All commands run from the repo root

## Persistent Data

Prepare persistent storage on the Docker host:

```bash
mkdir -p data/media
touch data/db.sqlite3
chmod 666 data/db.sqlite3
chmod 777 data data/media
```

Why:

- SQLite needs write access to the database file
- SQLite also needs write access to the parent directory for journal and lock files
- this repo's current LAN deployment runs the app container as `root` in Compose to avoid host bind-mount permission issues

## Build Image

Build the app image on the Docker host from the repo root.

Using Docker directly:

```bash
docker build -t heysiri:prod .
```

Using Compose:

```bash
docker compose build app
```

Either option produces the `heysiri:prod` image used by the stack.

## Deploy Stack

After the image is built, start the stack on the Docker host.

In `tcsh`:

```tcsh
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
docker compose up -d
```

If you want Compose to build and deploy in one command:

```tcsh
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
docker compose up -d --build
```

This starts:

- `heysiri-app`
- `heysiri-caddy`

## Step 1: Find The Docker Host LAN IP

On the machine running Docker, get its LAN IP.

Examples:

```bash
ip addr
```

or:

```bash
hostname -I
```

Example result:

```text
192.168.1.25
```

This is the IP other client machines must use in their `hosts` file.

## Step 2: Confirm The Stack Is Running On The Docker Host

On the Docker host, in `tcsh`:

```tcsh
docker compose ps
```

If not already deployed, use the `Build Image` and `Deploy Stack` steps above.

## Step 3: Open Port 8090 On The Docker Host

Other machines cannot connect unless inbound `8090/tcp` is allowed on the Docker host.

Make sure the OS firewall or network firewall allows:

- `8090/tcp`

## Step 4: Add Hosts Entry On Each Client Machine

On every machine that should access the app, add a `hosts` file entry pointing the name to the Docker host LAN IP.

Example:

```text
192.168.1.25 heysiri.d2-india.com
```

Replace `192.168.1.25` with the real Docker host LAN IP.

### Linux/macOS

Edit `/etc/hosts` and add:

```text
192.168.1.25 heysiri.d2-india.com
```

### Windows

Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator and add:

```text
192.168.1.25 heysiri.d2-india.com
```

## Step 5: Open The App

From any client machine with the correct `hosts` entry:

```text
http://heysiri.d2-india.com:8090
```

## Validation

### On the Docker host

Check containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View app logs only:

```bash
docker compose logs -f app
```

View proxy logs only:

```bash
docker compose logs -f caddy
```

Test locally on the Docker host:

```bash
curl -I http://heysiri.d2-india.com:8090
```

### On a client machine

Test name resolution and HTTP access:

```bash
curl -I http://heysiri.d2-india.com:8090
```

## Restart / Rebuild

Restart:

```bash
docker compose restart
```

Stop:

```bash
docker compose down
```

Rebuild after code changes:

```bash
docker build -t heysiri:prod .
docker compose up -d
```

Or in one step:

```bash
docker compose up -d --build
```

## Update / Redeploy Flow

When code changes are ready on the Docker host:

1. Pull or copy the latest code into the repo.
2. Rebuild the image.
3. Restart the stack with the new image.
4. Verify from both the Docker host and a client machine.

Commands:

```tcsh
cd /dd/ayon/git/heySiri
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
docker build -t heysiri:prod .
docker compose up -d
docker compose ps
docker compose logs --tail=100
```

## Django Host Settings

Current local HTTP defaults from [compose.yaml](/dd/ayon/git/heySiri/compose.yaml:1):

- `DJANGO_ALLOWED_HOSTS=heysiri.d2-india.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=http://heysiri.d2-india.com:8090`
- `DJANGO_SECURE_SSL_REDIRECT=false`
- `DJANGO_SESSION_COOKIE_SECURE=false`
- `DJANGO_CSRF_COOKIE_SECURE=false`
- `DJANGO_SECURE_HSTS_SECONDS=0`

## Optional Direct IP Access

If you want to access the app directly by IP instead of domain, for example:

```text
http://192.168.1.25:8090
```

then start the stack with Django configured to allow both the domain and the IP.

In `tcsh`:

```tcsh
setenv DJANGO_SECRET_KEY 'replace-this-with-a-real-secret'
setenv DJANGO_ALLOWED_HOSTS 'heysiri.d2-india.com,192.168.1.25'
setenv DJANGO_CSRF_TRUSTED_ORIGINS 'http://heysiri.d2-india.com:8090,http://192.168.1.25:8090'
docker compose up -d --build
```

Using the domain name is still the cleaner option.

## Common Issues

### Other machines cannot open the site

Cause:

- wrong LAN IP in the client `hosts` file
- no `hosts` entry on the client
- Docker host firewall blocks `8090/tcp`
- client and Docker host are not on the same reachable network

Fix:

- verify the Docker host LAN IP
- verify the client `hosts` file entry
- open inbound `8090/tcp`
- retry `curl -I http://heysiri.d2-india.com:8090` from the client

### Domain does not resolve

Cause:

- `hosts` file entry missing or incorrect

Fix:

- add:

```text
192.168.1.25 heysiri.d2-india.com
```

with the correct Docker host LAN IP

### Docker daemon permission denied

Cause:

- the current user cannot access Docker

Fix:

- run as a user with Docker access
- or fix access to `/var/run/docker.sock`

### DisallowedHost

Cause:

- request hostname is missing from `DJANGO_ALLOWED_HOSTS`

Fix:

- use the domain access pattern from this runbook
- or include the direct IP in `DJANGO_ALLOWED_HOSTS` if you are opening by IP

### CSRF failures

Cause:

- origin is missing from `DJANGO_CSRF_TRUSTED_ORIGINS`

Fix:

- ensure:

```text
DJANGO_CSRF_TRUSTED_ORIGINS=http://heysiri.d2-india.com:8090
```

- if using direct IP access, include that IP origin too

### HTTP 502 from Caddy

Cause:

- `heysiri-caddy` is up but `heysiri-app` is crashing or restarting

Check:

```bash
docker compose ps
docker compose logs --tail=100 app
docker compose logs --tail=100 caddy
```

Common fix for this repo:

```bash
mkdir -p data/media
touch data/db.sqlite3
chmod 666 data/db.sqlite3
chmod 777 data data/media
docker compose down
docker compose up -d --build
```

### SQLite readonly database

Cause:

- the bind-mounted `data/db.sqlite3` file is not writable by the container
- or the `data/` directory is not writable for SQLite journal files

Fix:

```bash
chmod 666 data/db.sqlite3
chmod 777 data data/media
docker compose down
docker compose up -d --build
```
