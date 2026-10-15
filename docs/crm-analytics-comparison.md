# Comparing with the CRM Analytics Net Zero app

How to stand up Salesforce's own **Net Zero Analytics** app (CRM Analytics) next to this
package in one scratch org, loaded with the same data, and what the comparison shows. Built
and checked on 2026-10-15 against template version 4.8.

## Set it up

1. **A scratch org with all three features.** `config/analytics-scratch-def.json` adds
   `DevelopmentWave` (CRM Analytics) and `TCRMforSustainability` (the Net Zero Analytics
   licence and permission sets) to the usual `SustainabilityApp`:

   ```bash
   sf org create scratch --definition-file config/analytics-scratch-def.json --alias nzc-crma --duration-days 14
   ```

2. **Permission sets for yourself:** `NetZeroAdmin`, `NetZeroManager` and
   `TCRMforSustainabilityAdmin` (`EinsteinAnalyticsPlusAdmin` comes pre-assigned).
3. **This package and the showcase data,** exactly as in `sample-data/README.md`.
4. **Give the CRM Analytics Integration User read access.** The template refuses to create
   the app until the Integration User (profile *Analytics Cloud Integration User*) can read
   every object and field it loads — 33 Net Zero Cloud objects, about 800 fields. A permission
   set with read and View All on those objects, read on every permissionable field, plus read
   on `Account` and `AnnualEmssnInventory` (dependencies the deploy insists on), assigned to
   that user, is enough. The template's error names the fields it is missing.
5. **Create the app from the template** — `sfdc_internal__Net_Zero_Analytics` — with
   `POST /services/data/v67.0/wave/folders`:

   ```json
   {
     "label": "Net Zero Analytics",
     "name": "Net_Zero_Analytics",
     "templateSourceId": "sfdc_internal__Net_Zero_Analytics",
     "templateValues": {
       "Can_Continue": true,
       "IsProgrammatic": true,
       "autoconfig": "true",
       "ApplySecurityPredicates": "None",
       "includePrograms": "No"
     }
   }
   ```

   `includePrograms` is off because the Program objects aren't in a Net Zero Cloud scratch
   org. `ApplySecurityPredicates: None` makes every row visible to anyone who can open the
   app, which suits a demo org; a real one would use the role hierarchy. The build takes
   about eight minutes and creates six dashboards, including **Audit Dashboard**.

## What the comparison shows

Both read the same 300 showcase records in the same org.

| | Net Zero Analytics (CRM Analytics) | This package (Lightning reports) |
|---|---|---|
| Licence | CRM Analytics for Net Zero Cloud add-on | None beyond Net Zero Cloud |
| Setup | Template app, Integration User access to 33 objects, ~8 minute build | One deploy |
| Freshness | As of the last data sync ("Data updated: Today at 10:43 AM") | Live: every run queries the records |
| Audit view | Four tabs (Overview, Emission Factors, Data Quality, Renewable Energy), five filters including a comparison year | One dashboard, one Reporting Year filter |
| What "data quality" means | Usage intensity per m², monthly variance, outliers | Missing footprints and energy use, orphaned records, footprint stages |
| Fixing what it finds | Open the record | Edit in the report |

Two things only show up when both run on the same data:

- **Neither showed Scope 1 or 2 totals at first — and that was the data, not either
  product.** The showcase data then had no emission factors on its energy use and no scope
  allocation on its sites, and without them Net Zero Cloud leaves every scope field at zero.
  The CRM Analytics app showed 313 for vehicles because it also reads per-gas CO2, which Net
  Zero Cloud fills in whenever a vehicle energy use has a factor. The showcase data now
  carries factors and allocations, so both show real Scope 1 and 2.
- **Most of the CRM Analytics Data Quality tab needs data this demo doesn't have** — floor
  area for intensity, start and end dates on energy use for the monthly views — so it reads
  zero or "No results found". The two products answer different questions: theirs is "is
  this consumption plausible?", this package's is "is this inventory complete?".

## Scope 3

The showcase data includes Scope 3 (spend-based procurement and business travel), which
this package doesn't report on. Loaded into the comparison org, it fills two of the CRM
Analytics app's dashboards:

- **Scope 3 Procurement Dashboard**: 4.8K tCO2e from $14.1M of spend across eight
  suppliers, by year, by GHG category and by supplier, with emissions per million spent.
- **Business Travel Impact**: 76 tCO2e from flights, hotels and ground travel, by cost
  centre, month, traveller location and supplier.

Three things that weren't obvious:

- **Net Zero Cloud calculates Scope 3 on each record as it saves it** — spend times the
  procurement factor (deflated to the factor's year, hence the inflation rate the summary
  needs), distance times the haul-band factor for a flight, nights times the hotel factor.
  The Scope 3 footprints filled in a few minutes after the load; the procurement summaries'
  totals stayed empty. The CRM Analytics dashboards read the record-level figures either way.
- **After loading data, CRM Analytics needs a data sync and a recipe run** before the
  dashboards see it (`POST /wave/dataConnectors/{id}/ingest`, then start the recipe's
  dataflow with `POST /wave/dataflowjobs`). About ten minutes in a scratch org.
- **Both dashboards default to the current year.** With data for 2022–2024 they open empty;
  set Duration (procurement) or Travel Start Date (travel) to All Time.
