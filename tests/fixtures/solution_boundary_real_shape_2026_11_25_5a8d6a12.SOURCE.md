# Source of the solution_*_real_shape_2026_11_25_5a8d6a12.json fixtures

REAL SHAPE, unmodified (copies of the raw files of "window P", 2026-11-25).

- Platform: a scratch Egeria (memory repository) running `odpi/egeria-platform@sha256:5a8d6a128e011db5d9eda698f8d46d3c389f59100d69eab31428a0390000309f`
  (6.4-SNAPSHOT, the first build with odpi/egeria#9465), started by `scripts/dr_egeria_roundtrip_probe/scratch.py up`; the user is the image's demo user.
- `solution_blueprint_nested_boundaries_...json`: `SolutionArchitect.get_solution_blueprint_by_guid(guid, graph_query_depth=10, output_format="JSON")` of a blueprint
  that has a boundary as a member, which has a nested boundary, which has a role (blueprint > boundary > boundary > role).
- `solution_boundary_retrieve_...json`: `get_solution_boundary_by_guid(guid, graph_query_depth=10, output_format="JSON")` of that outer boundary. The default-depth read
  returned the same bytes.
- Every element is a `probe-*` element, created and deleted in that window; no password, token or host name is in the files (checked by grep).
