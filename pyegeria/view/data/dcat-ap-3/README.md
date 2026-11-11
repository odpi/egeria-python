# DCAT-AP 3 SHACL shapes (vendored)

These files are the published SHACL shapes of **DCAT-AP 3.0.1**, copied unchanged so that
pyegeria's `dcat-ap-3-shacl` document validator never fetches anything over the network.

| File | What it is |
|---|---|
| `dcat-ap-SHACL.ttl` | The DCAT-AP 3.0.1 constraints (cardinalities, datatypes). Used by `dcat-ap-3-shacl`. |
| `ranges.ttl` | The DCAT-AP 3.0.1 range (class) constraints. Vendored for completeness; not used by `dcat-ap-3-shacl`, which validates documents that link to external vocabularies by IRI without typing them. |
| `LICENSE` | The licence the shapes are published under (CC BY 4.0), copied from the source repository. |

- **Source:** https://github.com/SEMICeu/DCAT-AP, `releases/3.0.1/shacl/`, at commit
  `4470b8ea907b7eb9ec55ab22befd1ecd2210ff32` (master, fetched 2026-11-11). The shapes are
  byte-identical to the 3.0.1 release commit `729eddfc176d0afee5850ade6528f96f72579412`.
- **Publisher:** SEMIC, Interoperable Europe (European Commission).
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), which permits
  redistribution with attribution. Attribution: "DCAT-AP 3.0.1 SHACL shapes, © SEMIC /
  European Commission, CC BY 4.0, https://github.com/SEMICeu/DCAT-AP".
- **SHA-256:**
  - `dcat-ap-SHACL.ttl` 990d3e42721de6a4be8cc338a7171559f195e62dea89c0b56531356b78cc026f
  - `ranges.ttl` a6eed0fae8d0f5ca977fe2098ca12081ac60b0efe1ddce802d5c08e49505ebcc
  - `LICENSE` 9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94

To update: download the new release's `shacl/` files from the same repository, replace these
files, update the commit, hashes and version above, and rerun `tests/micro-tests/test_sd2_export_dcat.py`.
