# Published sources, included excerpts and external downloads

Use this page with the [setup guide](../setup.md). Tasks 00–05 and both
primers need **only open-source software, the included files and published
inputs**; no licence file or commercial software is required. Task 00 and the paper primers use included invented models. Tasks
01–04 share one published Cu–Ni TDB; Task 05 uses Sun's published Ni–Nb TDB.

## What is included and what stays external

| Item | Repository treatment | Use |
|---|---|---|
| Course-written lessons, scripts, synthetic TDBs and generated plots/JSON | Included | Runnable introductory route |
| [Four Mey chemical-interaction rows](../materials/cuni/mey1992_binary_parameters.csv) | Included, cited and independently formatted | Task 01 reading context; does not replace the TDB |
| [Nine Srikanth–Jacob Ni-activity rows](../materials/cuni/srikanth_jacob1989_ni_activity.csv) | Included, cited and independently formatted | Task 02 fit at 1000 K |
| [Eight Fischer Ni-twin curve readings](../materials/boundaries/ni_twin_curve.csv) | Included, cited and independently digitized | Task 03 curve/area-site exercise |
| [Hallstedt 2025 article PDF](hallstedt2025.pdf) | Included unchanged under CC BY 4.0, with attribution | Cu–Ni collection provenance |
| Complete Cu–Ni and Sun Ni–Nb TDBs | External, learner-fetched | Required computation inputs; exact identities below |
| Mey, Srikanth–Jacob, Fischer and Sun paper PDFs/figures | External links; no redistribution grant established for the inspected copies | Source reading and the named diagram comparisons |
| Restricted third-party course instructions, databases and software | Excluded | Not needed |

Selected facts are independently formatted, without copied table/figure layout.
Their presence does not imply a licence for whole databases, articles or figures.


## Hallstedt: included article under CC BY 4.0

B. Hallstedt, “The SGTE collection of binary datasets,” *Calphad* 89 (2025),
102833. [DOI](https://doi.org/10.1016/j.calphad.2025.102833).
[Institutional record](https://publications.rwth-aachen.de/record/1011611) ·
[Publisher-version PDF](https://publications.rwth-aachen.de/record/1011611/files/1011611.pdf).
The first PDF page states © 2025 The Author, published by Elsevier, under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). A repository copy must
preserve those notices and credit author/title/year/DOI/source/licence; it retains
CC BY 4.0 separately from the project's Apache licence. Preserve the original
PDF bytes and state any later changes. Attribution does not imply endorsement.

**Included copy:** [hallstedt2025.pdf](hallstedt2025.pdf), 44 pages,
1,646,244 bytes, SHA-256
`cfc791558f42d59bc247fd55d69b4c058e24a4854489a736b4c9584088404de5`.
It is the institutional publisher-version PDF, obtained on 2 October 2026.
Title, DOI and the first-page CC BY 4.0 notice were checked. The repository
copy is **byte-identical** to that PDF; no article content or metadata was
changed. The Hallstedt PDF is background reading,
not a runtime input or a prerequisite to execute the Cu–Ni model.

The [Elsevier supplement policy](https://www.elsevier.support/publishing/answer/which-license-should-i-select-when-posting-my-research-data)
says open-access supplementary data follow the article licence. The
[Cu–Ni source note](../materials/cuni/README.md) separately records uncertainty
about embedded SGTE unary coverage. We keep the **complete TDB** external;
this does not turn the licensed article into a
restricted PDF or establish a prohibition on using the published TDB locally.

## Obtain the exact two databases

From the repository root, after installing the locked environment:

```bash
export CALPHAD_INPUT_DIR="$HOME/calphad-inputs"
mkdir -p "$CALPHAD_INPUT_DIR"
```

| Input | Download | Member/file to keep | Required identity |
|---|---|---|---|
| Cu–Ni | [Direct TDB](https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb) · [collection listing](https://phasediagrams.org/phase-diagram/CuNi-92Mey-LB.tdb) | `CuNi-92Mey-LB.tdb` | 6,789 bytes; SHA-256 `7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1` |
| Cu–Ni alternate route | [Hallstedt original supplementary ZIP](https://ars.els-cdn.com/content/image/1-s2.0-S0364591625000367-mmc3.zip) | ZIP member **`datasets/datasets/CuNi-92Mey-LB.tdb`**; save its contents as `CuNi-92Mey-LB.tdb` | Same identity as direct file (archive member checked) |
| Ni–Nb | [Sun original supplementary ZIP](https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip) | ZIP member **`calpha_102563_Nb-Ni_new_mmc1.tdb`**; keep that filename | 13,087 bytes; SHA-256 `ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a` |

In a browser, save the direct Cu–Ni file. For ZIPs, open the archive and extract
**only the named member** into `$CALPHAD_INPUT_DIR`. If the direct supplement
link fails, open the corresponding article DOI, find its supplementary-material
section and select the matching `mmc3` (Hallstedt) or `mmc1` (Sun) archive.
Do not select the Sun `mmc2.docx` instead of the TDB archive. The Sun filename
says Nb–Ni although our course says Ni–Nb; these refer to the same binary.

The [setup guide](../setup.md#obtain-the-two-external-inputs) supplies Python
commands for the direct downloads and exact byte/hash check. For the alternate
Hallstedt ZIP route, this terminal block needs no unzip program:

```bash
.venv/bin/python - <<'PY'
import hashlib, io, os, urllib.request, zipfile
from pathlib import Path
url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0364591625000367-mmc3.zip'
with urllib.request.urlopen(url, timeout=30) as response:
    archive = response.read()
with zipfile.ZipFile(io.BytesIO(archive)) as supplement:
    data = supplement.read('datasets/datasets/CuNi-92Mey-LB.tdb')
expected = '7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1'
if len(data) != 6789 or hashlib.sha256(data).hexdigest() != expected:
    raise SystemExit('Cu–Ni input mismatch; do not run a material example')
path = Path(os.environ['CALPHAD_INPUT_DIR']) / 'CuNi-92Mey-LB.tdb'
if path.exists() and path.read_bytes() != data:
    raise SystemExit(f'Existing different input left untouched: {path}')
path.write_bytes(data)
print(f'OK: {path}')
PY
```

Keep complete inputs outside Git, unchanged. Both teaching scripts enforce the
TDB identity; a newer or different file is not a drop-in replacement, so do
not relax the hash checks to accept it. Save exact HTTP/error messages if
access fails. Browser access may work where the automated download is blocked,
but this is not guaranteed.

## Obtain the papers and find the relevant material

Use your normal publisher/library access or the named public manuscript route.
Save PDFs outside Git, for example in `$CALPHAD_INPUT_DIR/papers`. A downloaded
HTML login/error page is not a PDF. Do not substitute a scan from other course
material for a publisher PDF, and do not upload a paper PDF to the course merely
because you can read it.

| Paper | Access route | Where to look / why needed |
|---|---|---|
| S. an Mey, “Thermodynamic re-evaluation of the Cu–Ni system,” *Calphad* 16 (1992), 255–260 | [DOI/publisher](https://doi.org/10.1016/0364-5916(92)90022-P); follow full-text/PDF using library access if required | Fig. 1: printed p.256 / inspected PDF p.2, liquidus/solidus. Fig. 7: p.259 / PDF p.5, miscibility gap. Table 2: p.257 / PDF p.3, coefficient excerpt. Task 01 comparison. |
| S. Srikanth and K. T. Jacob, “Thermodynamic properties of Cu–Ni alloys: Measurements and assessment,” *Materials Science and Technology* 5 (1989), 427–434 | [DOI/publisher](https://doi.org/10.1179/mst.1989.5.5.427) · [author-posted PDF](https://www.researchgate.net/profile/Kallarackel-Jacob/publication/233719829_Thermodynamic_properties_of_Cu-Ni_alloys_Measurements_and_assessment/links/592e9ece0f7e9beee73eb889/Thermodynamic-properties-of-Cu-Ni-alloys-Measurements-and-assessment.pdf) | Table 1: p.429 / inspected PDF p.3, reported Ni activities at 1000 K. Task 02's selected CSV is included, so full-paper access is not needed for the computation. |
| F. Fischer, G. Schmitz and S. M. Eich, “A systematic study of grain boundary segregation and grain boundary formation energy using a new copper–nickel embedded-atom potential,” *Acta Materialia* 176 (2019), 220–231 | [DOI/publisher](https://doi.org/10.1016/j.actamat.2019.06.027) · [publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S1359645419303945); use publisher/library PDF access for the actual figure | Fig. 3: p.224 / inspected PDF p.5, blue pure-Ni coherent-twin formation-energy curve; geometry in Section 3 p.222 / PDF p.3. Task 03's independent readings are included. The preview identifies the paper; it is not a substitute for full figure inspection. |
| H. Sun et al., “Thermodynamic modeling of the Nb-Ni system with uncertainty quantification using PyCalphad and ESPEI,” *Calphad* 82 (2023), 102563 | [DOI/publisher](https://doi.org/10.1016/j.calphad.2023.102563) · [public institutional manuscript PDF](https://www.osti.gov/servlets/purl/2205728) · [institutional record](https://www.osti.gov/biblio/2205728) | Fig. 8(a): printed manuscript p.42 / PDF p.44, present assessment for Task 05 comparison. Fig. 8(b) is the previous assessment. The public manuscript is not the publisher-layout version. |

Page counts above refer to the inspected versions. Publisher and accepted
manuscript layouts can differ; use the named figure/table and caption as well
as the page number. Paper PDF hashes below identify our inspected copies only:
the scripts **do not check them**, and you do not need that exact copy.

| Inspected paper | Bytes | SHA-256 |
|---|---:|---|
| Mey 1992 | 408,129 | `ef4ab2a3aaac46baf37cdbec302d36b924a23d89dbb29c5cfdf7ff5cff8b7542` |
| Srikanth–Jacob 1989 | 596,594 | `c8b525de8eb691d04521babf35d24a1bdd87b593019d366f558ca5a00d3f7b1c` |
| Fischer 2019 | 1,453,941 | `eb3fe5b6c92f24ea9ea440132e0ab52e8082f03d14e789679284acaff90aaabd` |
| Sun OSTI manuscript | 1,859,153 | `787622fd834f3270d308f2a9cab22d3f24579c1ccbfaabad50651c9127594f84` |

For a paper with a public direct PDF URL, a terminal download can use the same
standard-library route (example: Sun's manuscript):

```bash
mkdir -p "$CALPHAD_INPUT_DIR/papers"
.venv/bin/python - <<'PY'
import os, urllib.request
from pathlib import Path
url = 'https://www.osti.gov/servlets/purl/2205728'
with urllib.request.urlopen(url, timeout=30) as response:
    data = response.read()
if not data.startswith(b'%PDF-'):
    raise SystemExit('Response is not a PDF; use the institutional browser link')
path = Path(os.environ['CALPHAD_INPUT_DIR']) / 'papers' / 'sun2023_osti.pdf'
if path.exists() and path.read_bytes() != data:
    raise SystemExit(f'Existing different PDF left untouched: {path}')
path.write_bytes(data)
print(path)
PY
```

The Hallstedt and Srikanth direct PDF links can be used with the same pattern
and a corresponding filename. For Mey/Fischer the DOI is a landing-page route;
use its PDF button rather than passing the DOI to a raw-PDF downloader.
Task 04's runnable inputs are the same Cu–Ni bulk plus the explicitly invented
boundary preference; **no extra segregation dataset or optional thesis is required**.
