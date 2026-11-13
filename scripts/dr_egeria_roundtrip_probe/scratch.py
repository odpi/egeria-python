#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The scratch Egeria the round-trip probe runs against: `up`, `down`, `status`.

    python scripts/dr_egeria_roundtrip_probe/scratch.py up [--digest sha256:...] [--out DIR]
    python scripts/dr_egeria_roundtrip_probe/scratch.py status
    python scripts/dr_egeria_roundtrip_probe/scratch.py down

`up` copies the base image's own server configuration out of the image, applies the option-A edits
(simple-metadata-store + view-server, no Kafka, the Core Content Pack as the only archive), REFUSES to
start if any copied file still names `host.docker.internal`, then runs the platform on 127.0.0.1:19443
with the scratch label, waits for both servers, and creates the probe user's personal profile.

The repository (`--repository`, default `postgres`) is the same PostgreSQL OMRS connector a real
platform uses, against a throwaway `pgvector/pgvector:pg17` container on a private Docker network with
no host port, so the probe sees what a Postgres-backed platform does (the in-memory repository, kept as
`--repository memory`, returns type-prefixed GUIDs a Postgres store doesn't). Never a shared Postgres.

`down` removes the platform and PostgreSQL containers, the private network, the PostgreSQL volume and
the scratch configuration (results are kept), and confirms nothing labelled is left and 19443 is free.

Never a laz or shared platform: the container, port and label are fixed, and the probe's own guard
checks them again before any request.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import ssl
from pathlib import Path

DEFAULT_DIGEST = "sha256:002a3ef17b269775797fd9bf590a503b098141094c83839443b79753c44f4060"
IMAGE_REPO = "odpi/egeria-platform"
CONTAINER = "egeria-scratch-roundtrip"
LABEL = "purpose=roundtrip-probe"
PORT = 19443
SERVERS = ("simple-metadata-store", "view-server")
LAZ_CONTAINER = "quickstart-egeria-main"   # only ever inspected (StartedAt), never touched
FORBIDDEN_HOST = "host.docker.internal"
POINTER = ".current_scratch"

PG_CONTAINER = "egeria-scratch-roundtrip-pg"
PG_IMAGE = "pgvector/pgvector:pg17"
NETWORK = "roundtrip-net"            # private: the PostgreSQL container publishes no host port
PG_VOLUME = "roundtrip-pg-data"
PG_DATABASE = "egeria"
DATABASE_URL = f"jdbc:postgresql://{PG_CONTAINER}:5432/{PG_DATABASE}"
STORE_SCHEMA = "repository_simple_metadata_store"
#: The archives the metadata store loads: the Core Content Pack plus only those packs that define the
#: technology types (and their catalog templates) Dr.Egeria's create-from-template commands use. No Coco.
CONTENT_PACKS = (
    "content-packs/CoreContentPack.omarchive",
    "content-packs/UnityCatalogContentPack.omarchive",   # Create UC Server/Catalog/Schema/Table/Function/Volume
    "content-packs/ApacheKafkaContentPack.omarchive",    # Create Kafka Server Element
    "content-packs/PostgresContentPack.omarchive",       # Create Postgres Server/Database Element
    "content-packs/FilesContentPack.omarchive",          # Create CSV Data File / Folder / CSV File templates
)
MIN_FREE_GB = 15                      # the 2026-11-04 Docker VM disk-full took the shared PostgreSQL down
PROBE_USER = "garygeeke"
REPOSITORIES = ("postgres", "memory")

KAFKA_ENDPOINT = "kafka-disabled.invalid:9092"   # never resolves: no event bus at all
EGERIA_ENDPOINT = "https://localhost:7443"       # the container itself


class Refused(SystemExit):
    pass


DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")


def checked_digest(digest: str) -> str:
    """The pin must be a full image digest, `sha256:<64 hex>`: a tag (`latest`, `6.3`) can move under it."""
    if not DIGEST_RE.fullmatch(digest or ""):
        raise Refused(f"REFUSED: --digest {digest!r} is not a full image digest (sha256:<64 hex>); "
                      "a tag can't stand in for the pin")
    return digest


# ── The edits (pure functions, unit-tested on a copied fixture) ──

def edit_view_server_config(text: str) -> str:
    """Point every view service at simple-metadata-store and drop the Kafka audit-log destination."""
    config = json.loads(text)

    def repoint(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "omagserverName" and value == "active-metadata-store":
                    node[key] = "simple-metadata-store"
                else:
                    repoint(value)
        elif isinstance(node, list):
            for value in node:
                repoint(value)

    repoint(config)
    repo = config.get("repositoryServicesConfig") or {}
    if "auditLogConnections" in repo:
        repo["auditLogConnections"] = [c for c in repo["auditLogConnections"] if "kafka" not in json.dumps(c).lower()]
    return json.dumps(config, indent=2)


def edit_store_config(text: str, packs: tuple = CONTENT_PACKS) -> str:
    """The metadata store loads CONTENT_PACKS (technology types, templates) instead of the image's SimpleCatalog
    sample archive: one archive connection per pack, each a copy of the image's own connection."""
    config = json.loads(text)
    repo = config["repositoryServicesConfig"]
    template = json.dumps(repo["openMetadataArchiveConnections"][0])
    repo["openMetadataArchiveConnections"] = [
        json.loads(template.replace("content-packs/SimpleCatalog.omarchive", pack)) for pack in packs]
    return json.dumps(config, indent=2)


def archive_files(text: str) -> list[str]:
    """The archive files a server config loads (for the results header)."""
    connections = json.loads(text)["repositoryServicesConfig"].get("openMetadataArchiveConnections") or []
    return [c.get("endpoint", {}).get("networkAddress", "") for c in connections]


def edit_application_properties(text: str, repository: str = "memory") -> str:
    """Start only the two scratch servers (memory) or none (postgres: they're configured for PostgreSQL
    first, then started), fix the image's placeholder JSON typo, point the Kafka and Egeria endpoint
    placeholders away from the host, and the repository URL at the scratch PostgreSQL container."""
    out = []
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("startup.server.list="):
            line = "startup.server.list=" + (",".join(SERVERS) if repository == "memory" else "")
        elif stripped.startswith('"repositoryDatabaseURL"'):
            line = '    "repositoryDatabaseURL" : "' + DATABASE_URL + '",\\'
        elif stripped.startswith('"kafkaEndpoint"'):
            line = f'    "kafkaEndpoint" : "{KAFKA_ENDPOINT}",\\'
        elif stripped.startswith('"egeriaEndpoint"'):
            line = f'    "egeriaEndpoint" : "{EGERIA_ENDPOINT}",\\'
        elif stripped.startswith('"secretsStoreProvider"') and line.rstrip().endswith('".\\'):
            # the base image's own typo: `".\` where the JSON needs `",\` -- no server starts without the fix
            line = line.rstrip()[:-3] + '",\\'
        out.append(line)
    return "\n".join(out)


def forbidden_references(folder: Path) -> list[str]:
    """Every copied file that still names the host (`host.docker.internal`): any one refuses the start."""
    hits = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        if FORBIDDEN_HOST.encode() in path.read_bytes():
            hits.append(str(path.relative_to(folder)))
    return hits


def apply_edits(folder: Path, repository: str = "memory") -> None:
    vsc = folder / "data" / "servers" / "view-server" / "config" / "view-server.config"
    vsc.write_text(edit_view_server_config(vsc.read_text(encoding="utf-8")), encoding="utf-8")
    store = folder / "data" / "servers" / "simple-metadata-store" / "config" / "simple-metadata-store.config"
    if store.exists():
        store.write_text(edit_store_config(store.read_text(encoding="utf-8")), encoding="utf-8")
    props = folder / "application.properties"
    props.write_text(edit_application_properties(props.read_text(encoding="utf-8"), repository),
                     encoding="utf-8")
    hits = forbidden_references(folder)
    if hits:
        raise Refused(f"REFUSED: the scratch configuration still names {FORBIDDEN_HOST} in {hits}; "
                      "the scratch platform must never reach the host")


# ── Docker ──

def docker(*args, check=True) -> str:
    proc = subprocess.run(["docker", *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise SystemExit(f"docker {' '.join(args[:2])} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def laz_started_at() -> str | None:
    """StartedAt of laz's Egeria container, if this host has one (read-only inspect)."""
    proc = subprocess.run(["docker", "inspect", "-f", "{{.State.StartedAt}}", LAZ_CONTAINER],
                          capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else None


def port_free(port: int = PORT) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def labelled() -> list[str]:
    return docker("ps", "-a", "--filter", f"label={LABEL}", "--format", "{{.Names}}").split()


def labelled_networks() -> list[str]:
    return docker("network", "ls", "--filter", f"label={LABEL}", "--format", "{{.Name}}").split()


def labelled_volumes() -> list[str]:
    return docker("volume", "ls", "--filter", f"label={LABEL}", "--format", "{{.Name}}").split()


def docker_free_gb(image: str) -> float:
    """Free space on the Docker VM's disk (the image's overlay root), in GB."""
    out = docker("run", "--rm", "--network", "none", "--entrypoint", "df", image, "-k", "/")
    return int(out.splitlines()[-1].split()[3]) / (1024 * 1024)


def image_secret(image: str, file: str, collection: str, field: str) -> str:
    """A value from the image's own secrets file (`<collection>:` ... `<field>: value`); never printed."""
    script = (f"awk '/^ *{collection}:/{{f=1}} f && /^ *{field}:/{{sub(/^ *{field}: */,\"\"); print; exit}}' "
              f"/deployments/secrets/{file}")
    value = docker("run", "--rm", "--network", "none", "--entrypoint", "sh", image, "-c", script)
    if not value:
        raise SystemExit(f"no {field} for {collection} in the image's {file}")
    return value


# ── The platform's REST API (scratch only: always https://localhost:19443) ──

def _call(method: str, path: str, body=None, token: str | None = None, text: bool = False):
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    data = None
    headers = {}
    if body is not None:
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        headers["Content-Type"] = "text/plain" if isinstance(body, str) else "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://localhost:{PORT}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, context=ctx, timeout=120) as response:
        raw = response.read().decode()
    if text:
        return raw
    result = json.loads(raw) if raw.strip() else {}
    if isinstance(result, dict) and result.get("relatedHTTPCode", 200) >= 400:
        raise SystemExit(f"{method} {path}: {result.get('exceptionErrorMessage') or result}")
    return result


def wait_for_platform(timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = docker("inspect", "-f", "{{.State.Status}}", CONTAINER, check=False)
        if state != "running":
            raise SystemExit(f"{CONTAINER} is {state}; see `docker logs {CONTAINER}`")
        try:
            if "Egeria" in _call("GET", "/open-metadata/platform-services/server-platform/origin", text=True):
                return
        except (OSError, ValueError):
            pass
        time.sleep(3)
    raise SystemExit(f"timed out waiting for the platform; see `docker logs {CONTAINER}`")


def wait_for_servers(timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = docker("inspect", "-f", "{{.State.Status}}", CONTAINER, check=False)
        if state != "running":
            raise SystemExit(f"{CONTAINER} is {state}; see `docker logs {CONTAINER}`")
        logs = subprocess.run(["docker", "logs", CONTAINER], capture_output=True, text=True)
        text = logs.stdout + logs.stderr
        started = [s for s in SERVERS if any("SERVER-OPS-0004" in line and s in line for line in text.splitlines())]
        if len(started) == len(SERVERS):
            return
        time.sleep(5)
    raise SystemExit(f"timed out waiting for {SERVERS} to start; see `docker logs {CONTAINER}`")


def user_token(image: str, user: str = PROBE_USER) -> str:
    password = image_secret(image, "coco-user-directory.omsecrets", user, "clearPassword")
    return _call("POST", "/api/token", {"userId": user, "password": password}, text=True).strip()


def configure_postgres_and_start(token: str) -> None:
    """Point simple-metadata-store at the scratch PostgreSQL (the image's own sample request,
    data/servers/AddPostgreSQLRepository.http, with our database), then start both servers."""
    _call("POST", "/open-metadata/admin-services/servers/simple-metadata-store/local-repository/mode/"
                  "postgres-repository",
          {"databaseURL": f"{DATABASE_URL}?currentSchema={STORE_SCHEMA}", "databaseSchema": STORE_SCHEMA,
           "secretsStore": "~{egeriaServersSecretsStore}~",
           "secretsCollectionName": "~{repositorySecretCollectionName}~"}, token=token)
    for server in SERVERS:
        _call("POST", f"/open-metadata/platform-services/server-platform/servers/{server}/instance", token=token)


def ensure_profile(token: str, user: str = PROBE_USER) -> str:
    """The probe user's personal profile (Create ToDo/Meeting/Review/... need one); created if missing."""
    root = "/servers/view-server/api/open-metadata/my-profile"
    found = _call("GET", root, token=token).get("element")
    if isinstance(found, dict):
        return found.get("elementHeader", {}).get("guid", "")
    created = _call("POST", f"{root}/new", {
        "class": "NewElementRequestBody", "isOwnAnchor": True,
        "properties": {"class": "PersonProperties", "qualifiedName": f"Person::{user}::scratch",
                       "displayName": f"{user} (scratch)", "fullName": f"{user} (scratch)",
                       "description": "Personal profile created by scratch.py for the round-trip probe"}},
        token=token)
    return created.get("guid", "")


# ── up / down / status ──

def start_postgres(folder: Path, image: str) -> None:
    """A throwaway PostgreSQL on the private network; credentials are the image's own PostgreSQLRepository
    secret, so the platform's connector finds them where it already looks."""
    if not docker("images", "-q", PG_IMAGE, check=False):
        print(f"pulling {PG_IMAGE}")
        docker("pull", PG_IMAGE)
    docker("network", "create", "--label", LABEL, NETWORK)
    docker("volume", "create", "--label", LABEL, PG_VOLUME)
    env = folder / "pg.env"
    env.write_text(f"POSTGRES_USER={image_secret(image, 'egeria-servers.omsecrets', 'PostgreSQLRepository', 'userId')}\n"
                   f"POSTGRES_PASSWORD={image_secret(image, 'egeria-servers.omsecrets', 'PostgreSQLRepository', 'clearPassword')}\n"
                   f"POSTGRES_DB={PG_DATABASE}\n")
    env.chmod(0o600)
    docker("run", "-d", "--name", PG_CONTAINER, "--label", LABEL, "--network", NETWORK,
           "-v", f"{PG_VOLUME}:/var/lib/postgresql/data", "--env-file", str(env), PG_IMAGE)
    env.unlink()
    for _ in range(60):
        if subprocess.run(["docker", "exec", PG_CONTAINER, "pg_isready", "-d", PG_DATABASE],
                          capture_output=True).returncode == 0:
            return
        time.sleep(2)
    raise SystemExit(f"{PG_CONTAINER} never became ready; see `docker logs {PG_CONTAINER}`")


def up(digest: str, out: Path, repository: str = "postgres", timeout: int = 900) -> Path:
    digest = checked_digest(digest)
    if repository not in REPOSITORIES:
        raise SystemExit(f"--repository must be one of {REPOSITORIES}")
    if labelled() or labelled_networks() or labelled_volumes():
        raise SystemExit(f"scratch resources already exist ({labelled() + labelled_networks() + labelled_volumes()}); "
                         "run `down` first")
    if not port_free():
        raise SystemExit(f"port {PORT} is in use; refusing to start")
    image = f"{IMAGE_REPO}@{digest}"
    if not docker("images", "-q", image, check=False):
        print(f"pulling {image}")
        docker("pull", image)
    free = docker_free_gb(image)
    if free < MIN_FREE_GB:
        raise SystemExit(f"only {free:.1f} GB free on the Docker VM; refusing below {MIN_FREE_GB} GB")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = out / f"scratch-{stamp}"
    folder.mkdir(parents=True)
    cid = docker("create", image)
    try:
        docker("cp", "-q", f"{cid}:/deployments/data", str(folder / "data"))
        docker("cp", "-q", f"{cid}:/deployments/application.properties", str(folder / "application.properties"))
    finally:
        docker("rm", cid)
    apply_edits(folder, repository)  # refuses before anything runs
    (out / POINTER).write_text(str(folder))
    network = []
    if repository == "postgres":
        start_postgres(folder, image)
        network = ["--network", NETWORK]
    docker("run", "-d", "--name", CONTAINER, "--label", LABEL, *network,
           "--add-host", f"{FORBIDDEN_HOST}:127.0.0.1",   # second guard: the host name resolves to the container
           "-p", f"127.0.0.1:{PORT}:7443",
           "-v", f"{folder / 'data'}:/deployments/data",
           "-v", f"{folder / 'application.properties'}:/deployments/application.properties",
           "-e", "JAVA_OPTS_APPEND=-Xmx3g", image)
    wait_for_platform(timeout)
    token = user_token(image)
    if repository == "postgres":
        configure_postgres_and_start(token)
    wait_for_servers(timeout)
    profile = ensure_profile(user_token(image))
    print(f"scratch up: {CONTAINER} on https://localhost:{PORT} ({repository} repository, "
          f"{len(CONTENT_PACKS)} content packs), servers {', '.join(SERVERS)} started, {PROBE_USER} profile "
          f"{profile or 'present'}; {free:.0f} GB free; config {folder}")
    return folder


def down(out: Path) -> None:
    for name in labelled():
        docker("rm", "-f", name)
    for network in labelled_networks():
        docker("network", "rm", network)
    for volume in labelled_volumes():
        docker("volume", "rm", volume)
    pointer = out / POINTER
    if pointer.exists():
        folder = Path(pointer.read_text().strip())
        if folder.name.startswith("scratch-") and folder.parent == out and folder.exists():
            shutil.rmtree(folder)
        pointer.unlink()
    left = labelled() + labelled_networks() + labelled_volumes()
    print(f"scratch down: labelled containers/networks/volumes left {left or 'none'}; port {PORT} "
          f"{'free' if port_free() else 'STILL IN USE'}")
    if left or not port_free():
        raise SystemExit(1)


def status() -> dict:
    info = {"container": docker("inspect", "-f", "{{.State.Status}} {{.State.StartedAt}}", CONTAINER, check=False)
            or "absent", "postgres": docker("inspect", "-f", "{{.State.Status}}", PG_CONTAINER, check=False)
            or "absent", "labelled": labelled(), "networks": labelled_networks(), "volumes": labelled_volumes(),
            "port_free": port_free(), "laz_started_at": laz_started_at()}
    print(json.dumps(info, indent=1))
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("up", "down", "status"))
    ap.add_argument("--digest", default=DEFAULT_DIGEST, help="the platform image digest (default: the laz pin)")
    ap.add_argument("--repository", default="postgres", choices=REPOSITORIES,
                    help="postgres (default: the connector a real platform uses) or memory")
    ap.add_argument("--out", default="~/.re-gate/roundtrip-probe")
    args = ap.parse_args(argv)
    checked_digest(args.digest)
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    if args.action == "up":
        up(args.digest, out, args.repository)
    elif args.action == "down":
        down(out)
    else:
        status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
