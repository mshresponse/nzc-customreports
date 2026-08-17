# Character encoding: what actually breaks accented site names

If your Net Zero Cloud asset names contain non-English characters — and in any
multinational footprint they will — there is a step in the usual CSV workflow that
destroys them silently. This documents which step, with bytes rather than assertions.

## The short version

Two different things can mangle a name, and only one of them is recoverable.

| Character | UTF-8 | ISO-8859-1 | Recoverable? |
|---|---|---|---|
| `ü` in *Zürich* | `c3 bc` | `fc` | **Yes** — different bytes, same character. Re-read with the right encoding and it's fine. |
| `ö` in *Malmö* | `c3 b6` | `f6` | **Yes** |
| `Ō` in *Ōsaka* | `c5 8c` | *not representable* → `3f` | **No.** It becomes a literal question mark. The original character is gone. |

That last row is the one that matters. `Ō` (U+014C, Latin capital O with macron) has no
ISO-8859-1 code point. Anything that writes Latin-1 replaces it with `?` and there is
nothing left to recover from — no amount of re-reading with the correct encoding brings it
back, because the information is no longer in the file.

## Reproduce it

`names-utf8.csv` and `names-latin1.csv` in this folder are the same six site names written
in each encoding. Compare them:

```bash
python3 - <<'PY'
for path in ['names-utf8.csv', 'names-latin1.csv']:
    for line in open(path, 'rb').read().split(b'\n'):
        if b'saka' in line:
            print(f"{path:20} {' '.join(f'{b:02x}' for b in line)}")
PY
```

```
names-utf8.csv       c5 8c 73 61 6b 61 20 53 65 69 7a c5 8d 73 68 6f
names-latin1.csv     3f 73 61 6b 61 20 53 65 69 7a 3f 73 68 6f
```

`c5 8c` → `3f`. Two bytes carrying a character, replaced by one byte carrying a question
mark.

## Where this bites in practice

**Salesforce report CSV export defaults to ISO-8859-1.** Reports → Export → the format
dropdown offers "Formatted Report" and "Details Only", and the encoding selector below it
defaults to ISO-8859-1, not UTF-8. Anyone exporting a report to check their data will see
mangled names and reasonably conclude the org data is corrupt.

**It usually isn't.** In testing against a live org, names loaded as UTF-8 stored
correctly, exported as garbage under the ISO-8859-1 default, and exported byte-identical
to the source under UTF-8. The org was clean the whole time. The export was lossy.

**But the export is not the only culprit, and often not the real one.** Spreadsheet
applications will happily write Latin-1 or CP1252 on a Save As if you don't choose the
encoding, and that write happens *before* the data reaches Salesforce. A file that leaves
a spreadsheet already mangled loads into the org already mangled, and no amount of correct
export settings will fix it afterwards.

So there are two distinct failure points:

1. **Before the load** — spreadsheet writes the wrong encoding on save. Data enters the
   org already broken. Permanent.
2. **After the load** — report export writes ISO-8859-1. Data in the org is fine; only the
   file you're looking at is broken. Cosmetic, and fixable by changing the dropdown.

Diagnosing which one you have matters, because the fixes are completely different. Open
the record in Salesforce. If the name is right on screen, you have problem 2 and only need
to change the export encoding. If it's wrong on screen, you have problem 1 and need to
reload the data.

## What to do

**Loading data:**

- On a Mac without Excel, **Numbers** exports UTF-8 CSV by default. This is the path of
  least resistance and it works.
- Google Sheets → Download → CSV is UTF-8.
- Excel: use *CSV UTF-8 (Comma delimited)*, not plain *CSV*. The distinction is easy to
  miss in the Save As dropdown and is exactly where this goes wrong.
- Verify before loading: `file -bi yourfile.csv` should say `charset=utf-8`. If it says
  `charset=iso-8859-1`, stop and re-export.

**Exporting reports:**

- Change the encoding selector from ISO-8859-1 to **UTF-8** every time. It does not
  remember.

**Checking what's already in the org:**

The `Asset Names and Locations` report in this package is built for exactly this — every
column inline-editable, so you can fix a mangled name in place rather than round-tripping
a CSV. That is the point of the whole package, and this is its clearest use case.

## Files

| File | Encoding |
|---|---|
| `names-utf8.csv` | UTF-8, no BOM |
| `names-latin1.csv` | ISO-8859-1 — note `Ōsaka` has already become `?saka` |
