# Sample data

Six CSVs that populate a Net Zero Cloud **Base** trial org — the unconfigured one, which
ships licences and permissions but no records. Without data every report in this package
deploys cleanly and returns nothing, which looks like a failed install and isn't.

All files are **UTF-8, no BOM**, and deliberately contain accented and non-Latin-1 site
names (`Zürich Süd Rechenzentrum`, `São Paulo Fábrica`, `Kraków Magazyn`, `Peña Verde
Oficina`, `Malmö Kontor`, `Ōsaka Seizōsho`). That is not decoration — it is a live test of
your loading path. If names arrive in the org with question marks or mojibake, your
spreadsheet or loader wrote the wrong encoding. See [`../docs/encoding-evidence/`](../docs/encoding-evidence/).

## Load them in order

The order matters: children reference parents by name, so a parent that doesn't exist yet
produces a row that fails to relate.

| # | File | Object | Depends on |
|---|---|---|---|
| 1 | `1_StnryAssetEnvrSrc.csv` | Stationary Asset Environmental Source | — |
| 2 | `2_StnryAssetCrbnFtprnt.csv` | Stationary Asset Carbon Footprint | 1 |
| 3 | `3_StnryAssetEnrgyUse.csv` | Stationary Asset Energy Use | 1, 2 |
| 4 | `4_VehicleAssetEmssnSrc.csv` | Vehicle Asset Emission Source | — |
| 5 | `5_VehicleAssetCrbnFtprnt.csv` | Vehicle Asset Carbon Footprint | 4 |
| 6 | `6_VehicleAssetEnrgyUse.csv` | Vehicle Asset Energy Use | 4, 5 |

## About the `Parent.Name` columns

Files 2, 3, 5 and 6 reference their parents by **name**, e.g. `StnryAssetEnvrSrc.Name`.
Whether that works depends on your loader:

- **Data Loader / Data Import Wizard** generally want the parent **record Id**, not the
  name. Load the parent file, export the Ids, and substitute them.
- Some loaders resolve a parent by an **External Id** field, which `Name` is not by default.

If your loader rejects the name columns, load file 1 (and 4), grab the Ids, and map them
into the child files. The name column is there so the relationships are readable and so
you can see what should link to what — treat it as documentation of intent as much as
loadable data.

## Deliberate gaps

The data is not uniformly complete, on purpose. Some assets have a footprint and no energy
use; some have neither; some footprints have no parent asset at all. That is what makes
the **Missing** and **Orphaned** reports return rows instead of empty results — you can see
them working rather than taking their word for it.
