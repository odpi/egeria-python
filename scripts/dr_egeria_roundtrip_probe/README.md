# Dr.Egeria round-trip probe and release gate

Writes a recognisable value into every property-style attribute of every Dr.Egeria Create command,
runs the documents through `dr_egeria --process`, reads each element back (and reads what Egeria
actually stored), and reports what didn't come back. Before every pyegeria release it runs as a
**gate**: no regression against a committed baseline, and every known gap listed with its reason.

| File | What it does |
|---|---|
| `scratch.py` | `up` / `down` / `status` for the scratch Egeria (scripted; no hand steps) |
| `probe.py` | the round trip: `--smoke`, `--run`, `--gate`, `--rebaseline` |
| `gate.py` | the release gate: scratch up → probe → compare → report → scratch down |
| `report.py` | renders a `RESULTS-<UTC>.json` as markdown |
| `baseline/<digest>.json` | the committed baseline: one verdict per (command, attribute), per Egeria image digest |
| `known-gaps.json` | rows accepted as not fixable in pyegeria, each with a reason and a reference |

## Hard rules: scratch only

- **Never a real Egeria** (laz or any shared platform). `probe.py` refuses to start, before any request,
  unless the URL is exactly `https://localhost:19443` (or `127.0.0.1`), Docker shows the container
  publishing host port 19443 is `egeria-scratch-roundtrip` labelled `purpose=roundtrip-probe`, and that
  platform's origin answers "Egeria OMAG Server Platform". Ports 9443, 8443 and 7443 are refused on any host.
- **The scratch platform never reaches the host.** `host.docker.internal` is the standard container-to-host
  address and normal elsewhere; the probe refuses it only for its own scratch platform, whose point is
  isolation from the host's shared services. The base image's configuration points its Kafka and
  Egeria endpoints at `host.docker.internal`. `scratch.py up` rewrites them to non-host values, removes
  the view-server's Kafka audit-log destination, and **refuses to start if any copied file still names
  `host.docker.internal`**. As a second guard the container runs with
  `--add-host host.docker.internal:127.0.0.1`, so that name resolves to the container itself.
- **HOME isolation.** The probe's environment inherits no `EGERIA_*` or `PYEGERIA_*` variable, reads no
  `.env` or `config.json`, and sets `HOME` (with `PYEGERIA_DASHBOARD_SHEETS_STORE` and
  `PYEGERIA_USER_REPORT_SPECS_DIR`) inside the run folder, so Dr.Egeria's local stores never touch the
  real `~/.pyegeria`.
- **History (why the rules are this strict).** On 2026-11-12, before the Kafka edits existed, the first
  two hand-built scratch starts tried about ten times to reach `host.docker.internal:9192`, which on that
  host was a shared Kafka. The attempts failed and a read-only check found no trace there (no scratch
  topic or consumer group), but the default image configuration would have connected a scratch server
  to a shared event bus. The same day the first full run wrote one test Dashboard Sheet into the real
  `~/.pyegeria/dashboard_sheets.json` (removed). Hence the refusal and the HOME isolation above.

## Scratch platform

```bash
python scripts/dr_egeria_roundtrip_probe/scratch.py up [--digest sha256:<64 hex>] [--repository postgres|memory]
python scripts/dr_egeria_roundtrip_probe/scratch.py status      # also laz's StartedAt, read-only
python scripts/dr_egeria_roundtrip_probe/scratch.py down
```

`up` refuses unless the Docker VM has at least 15 GB free (the 2026-11-04 disk-full took a shared
PostgreSQL down), pulls `odpi/egeria-platform` by digest (a tag is refused), copies the image's
`/deployments/data` and `application.properties` into `~/.re-gate/roundtrip-probe/scratch-<UTC>/`, and
applies the edits:

1. `view-server.config`: every `"omagserverName":"active-metadata-store"` → `"simple-metadata-store"`, and the
   Kafka audit-log destination removed.
2. `simple-metadata-store.config`: the archives are `CONTENT_PACKS` in `scratch.py`: the **Core Content Pack**
   plus only the packs defining technology types Dr.Egeria's create-from-template commands use (Unity
   Catalog, Apache Kafka, PostgreSQL, Files). The image's SimpleCatalog sample is replaced; no Coco archives.
   The repository and the pack list are recorded in each results header and baseline.
3. `application.properties`: the startup list (both servers for `memory`; none for `postgres`, which are
   configured first, then started), the image's placeholder JSON typo fixed
   (`YAMLSecretsStoreProvider".\` → `",\`; without it no server starts), `kafkaEndpoint` →
   `kafka-disabled.invalid:9092`, `egeriaEndpoint` → `https://localhost:7443`, and `repositoryDatabaseURL` →
   the scratch PostgreSQL container.

Then the refusal check, and:

- **`--repository postgres` (default):** the same PostgreSQL OMRS connector a real platform uses, against a
  throwaway `pgvector/pgvector:pg17` container (`egeria-scratch-roundtrip-pg`) on a **private Docker network**
  (`roundtrip-net`) with **no host port**, and its own volume (`roundtrip-pg-data`). Its credentials are the
  image's own `PostgreSQLRepository` secret (passed through a 0600 env file, deleted at once). The metadata
  store is pointed at it with the image's own sample request (`data/servers/AddPostgreSQLRepository.http`),
  then both servers are started. **Never a shared PostgreSQL.**
- **`--repository memory`:** the in-memory repository, as the first runs used. It returns type-prefixed GUIDs
  (`Glossary-<uuid>`) a PostgreSQL store doesn't, so its results can differ from a real platform's.

The platform runs on `127.0.0.1:19443` with the label, and `up` waits until both servers have started, then
creates the probe user's personal profile (`my-profile/new`) so the commands that need one (Create ToDo,
Meeting, Review, ...) can run. The user is the image's demo `garygeeke`; passwords are read from the image's
own secrets and never printed. Never restart the platform mid-run.

`down` removes the platform and PostgreSQL containers, the private network, the volume and the scratch
configuration (results are kept), and confirms no labelled container, network or volume is left and port
19443 is free.

## Running the probe

```bash
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --smoke      # one glossary, read back
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --run        # every Create command
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/report.py ~/.re-gate/roundtrip-probe/RESULTS-<UTC>.json
```

The probe tests the pyegeria installed in the interpreter that runs it (specs included), so to probe
another checkout run it with that checkout's environment, e.g. `uv run --project <checkout> python …/probe.py`.
Outputs, under `~/.re-gate/roundtrip-probe/`: `RESULTS-<UTC>.json` / `.md`, and `run-<UTC>/` with the
generated document per family, each `dr_egeria --process --advanced --debug` log, and the processed output.

### Verdicts

`MATCH`; `DROPPED (not stored)` (sent, absent on read-back and absent in the raw store);
`NOT RETURNED (stored)` (sent, absent on read-back, present in the raw store: an Egeria read gap);
`DROPPED (raw read not applicable)` (absent on read-back; the raw store can't answer: relationships
such as Search Keywords, and header fields);
`CHANGED`; `DEFAULTED`; `NOT FOUND` (stored under another key: a spec metadata gap);
`SKIPPED (relationship – phase 2)`, `SKIPPED (control)`, `SKIPPED (no status property)`, …;
`NOT APPLIED (reported)` (not sent, and Dr.Egeria's output says so: a `not applied: <attribute>: <reason>`
warning, the reason in the note);
`REJECTED (breaks the create)` (an attribute whose probe value makes Egeria reject the whole create,
listed with its cause in `REJECTED` in `probe.py`; the pyegeria-side ones are sent anyway by default, since
F-A, and `--no-send-rejected` skips them; Extended Properties is always skipped); `CREATE-FAILED`; `AUTH`;
`UNRESOLVED`.

- **Stored (raw)** column: for every non-MATCH row the entity is read through repository-services on the
  scratch metadata store (`POST …/simple-metadata-store/open-metadata/repository-services/users/{u}/instances/entity/{guid}`),
  which returns the stored instance properties and effective times, bypassing the bean converters.
- **Side** (DROPPED / NOT RETURNED / CHANGED / DEFAULTED): from the `--debug` request bodies, key-aware —
  Egeria-side (in the body under the expected key), pyegeria-side (in no body), or `pyegeria-side?`
  (sent only under another key).
- **Status** is read from the type's own status field (`contentStatus` / `activityStatus` /
  `deploymentStatus`, from `element_status_fields`), on a second, Status-only element per command (the
  command's own Content/Activity/Deployment Status attribute would otherwise win the field).
- Every run uses `RTP::<UTC>::<Command>` names, so a re-run on the same platform creates, not updates.

## The release gate

```bash
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/gate.py              # up, probe, compare, down
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/gate.py --results RESULTS-<UTC>.json   # compare only
uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --run --gate                  # platform already up
```

The gate **fails** (exit 1) on: a row that was MATCH and now isn't; a new REJECTED, CREATE-FAILED or
UNRESOLVED; a command that has disappeared. **Improvements don't fail**: they print "update the baseline".
Rows in `known-gaps.json` never fail (an entry with a `verdict` covers that verdict only); when one
becomes MATCH the gate prints "remove from known gaps". No baseline for the platform's digest → exit 2.

- **Updating the baseline** (a release that fixes rows): `gate.py --rebaseline` (or `probe.py --run
  --rebaseline`). The rewritten file lists each changed row under `changes` with `"<one-line reason>"`;
  fill in every reason and commit the baseline in the release PR.
- **A new Egeria digest** (the laz pin moves): `gate.py --digest sha256:<new> --rebaseline` writes
  `baseline/<new>.json`; the PR shows the diff between the old and new digest baselines, so Egeria-side
  changes are visible.
- **Where it runs:** GitHub Actions (`.github/workflows/probe-gate.yml`: `workflow_dispatch`, and PRs
  labelled `release` or targeting `release/*`; the results are uploaded as artifacts), or locally with
  `gate.py` when Actions is unavailable (attach the results to the release PR).
- **Release procedure** (`docs/RELEASING.md`): "probe gate green, or its failure explained in the PR"
  comes after the 3.13 micro-tests and before tagging.

Phase 2 (relationship attributes, real zones) is not covered yet.
