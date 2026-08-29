# london-safety-analysis — methodology audit

Audited against the live repo on 29 August 2026. Every number below was recomputed from
your own data files or from a primary source. Where I could not verify something, I say so.

---

## State of the repo

Two fixes from the earlier review are in: the record count now reads 753,904 consistently,
and the author block reads "Senior Vehicle Engineer based in Sutton, London."

The scoring fix was never applied. `src/scoring.py` is unchanged and
`data/processed/borough_safety_summary.csv` still shows 32 of 33 boroughs compressed
between 93.1 and 100.0, all labelled "Excellent" — Westminster included.

That is no longer the main problem.

---

## 1. The collection method samples circles, not boroughs

`src/collect_data.py` calls `crimes-street/all-crime` with a single `lat`/`lng` per borough.
The data.police.uk documentation is explicit: that endpoint returns crimes
**within a 1-mile radius of a single point**.

So every row labelled "Barnet" in your dataset is not Barnet. It is *a 25.5 km² circle
centred on Barnet's geographic centroid* — 8.14 km² of it, to be exact, against Barnet's
86.7 km². You then divide those crimes by Barnet's entire 395,000 residents.

Coverage of each borough's actual area by the sampling circle:

| Borough | Area (km²) | Sampled | Coverage |
|---|---|---|---|
| Bromley | 150.1 | 8.1 | **5.4%** |
| Hillingdon | 115.7 | 8.1 | 7.0% |
| Havering | 112.3 | 8.1 | 7.2% |
| Barnet | 86.7 | 8.1 | 9.4% |
| … | | | |
| Islington | 14.9 | 8.1 | 54.6% |
| Kensington and Chelsea | 12.1 | 8.1 | **67.2%** |
| City of London | 2.9 | 2.9 | 100% |

Mean coverage: **15.5% for outer boroughs, 42.5% for inner boroughs.**

Total captured: 376,952 crimes per year. The MPS recorded 951,803 in 2024/25.
You have roughly 40% of London's crime, and the missing 60% is not missing at random —
it is concentrated in exactly the large outer boroughs your analysis recommends.

Four pairs of sampling circles also overlap, so some crimes are counted twice under two
different borough labels. `drop_duplicates(subset=["crime_id", "borough", "month"])`
deduplicates *within* a borough only, so it does not catch this.

---

## 2. I tested whether this invalidates your headline finding. It does not.

This is the part I got wrong on first inspection, and you should know it.

I pulled the Metropolitan Police's own borough-level recorded crime counts
(MPS Recorded Crime: Geographic Breakdown, London Datastore — complete counts, no sampling)
and compared them with yours over the same 18-month window.

| | Your data | MPS actual |
|---|---|---|
| Inner London mean rate per 10k/yr | 828 | 2,086 |
| Outer London mean rate per 10k/yr | 511 | 1,266 |
| Outer London is lower by | **38%** | **39%** |

Your absolute rates are less than half of reality, but the inner/outer *ratio* is almost
exactly right. The sampling bias largely cancels when you aggregate.

Rank correlation between your borough ordering and the MPS ordering: **Spearman ρ = 0.83**.
That is a strong relationship. The analysis is not noise.

**Keep the "outer London is around 40% safer" claim.** It survives independent verification.
Change "40–60%" to "around 40%" — the 60% has no support in either dataset.

---

## 3. What the sampling bias *does* break: the borough ranking

ρ = 0.83 leaves real room for individual boroughs to be badly misplaced, and several are.

| Borough | Your rank | True rank | Why |
|---|---|---|---|
| Hillingdon | 7th safest | **21st** | Circle centred on Uxbridge misses Heathrow entirely |
| Merton | 19th | **4th** | 21.6% coverage, but of a busier-than-average slice |
| Richmond upon Thames | 11th | **1st** | Genuinely the safest borough in London; you rank it 11th |
| Kingston upon Thames | 13th | 5th | |
| Barking and Dagenham | 22nd | 15th | |

Of your published top five — Barnet, Bromley, Redbridge, Bexley, Havering — only **Bexley**
is actually in the real top five. Barnet is 7th, Bromley 8th, Havering 9th, Redbridge 10th.
They are all genuinely good boroughs, so the recommendation isn't dangerous. But
"Safest borough: Barnet (100/100)" is not a defensible claim.

**The true top five for safety: Richmond upon Thames, Sutton, Bexley, Merton, Kingston upon Thames.**

---

## 4. The City of London row is not City of London

City of London is policed by the City of London Police, not the MPS, and its 2.9 km²
sits entirely inside a 1-mile circle that also swallows large parts of Southwark,
Tower Hamlets and Westminster. Your 21,537 "City of London" crimes are mostly other
boroughs' crimes, divided by 9,000 residents.

That single row is what pins your min-max scale and flattens the other 32 boroughs into
6.7 points. Drop it, or source it separately from City of London Police.

---

## 5. Smaller items

- **House prices have no cited source.** `house_price_k` drives 30% of the Family Score
  and appears nowhere in the pipeline. Cite it (ONS/HM Land Registry UK HPI, borough
  median paid price) or the Family Score isn't reproducible.
- **`config.py` comment is wrong:** "Metropolitan Police Service covers all 32 London
  boroughs" — it covers 32 of the 33 local authorities, excluding the City of London.
- **Git LFS trap.** `crime_data_raw.csv` and `crime_data_clean.csv` are LFS pointers.
  The README says "the data files are already included so you can run the analysis
  immediately." Anyone who clones without `git lfs install` gets 133-byte stub files and
  a crash on the first notebook. Add the LFS step to Getting Started.
- **Anti-social behaviour** is in police.uk data but is not a notifiable offence and is
  absent from MPS recorded crime. If you switch source, that 3% weight has to be dropped
  and the rest renormalised (I did this in the rebuilt scores).
- **Westminster's denominator.** Even with correct data, Westminster's 2,334 per 10k is
  measured against 211,000 residents serving over a million daily workers and visitors.
  Document this as a limitation rather than fixing it silently — a resident-denominated
  rate overstates the risk to someone who actually lives there.

---

## The fix

Swap the data source for the borough analysis. Keep police.uk for what it's good at.

**MPS Recorded Crime: Geographic Breakdown**
https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m

Complete monthly counts per borough per crime type. No sampling, no radius, no
double-counting, no 33 × 24 = 792 API calls. It is the correct dataset for comparing
boroughs, and swapping it in is a smaller job than the collection script you already wrote.

Keep the police.uk API work. Street-level point data within a radius is exactly what that
endpoint is for, and your Folium map is a legitimate use of it. Reframe it in the README
as "street-level crime mapping" rather than the basis of the borough scores.

`borough_safety_summary_REBUILT.csv` is what your scoring algorithm produces on MPS data,
with City of London removed and the ASB weight renormalised away. Scores now span 0 to 92.5
instead of 93.1 to 100.0, and the tiers actually discriminate: 2 Excellent, 9 Good,
10 Moderate, 10 Elevated, 1 High Risk.

---

## Do this before anything goes on LinkedIn

Right now the repo's headline table says Barnet is the safest borough in London at 100/100
and labels Westminster "Excellent." Both are wrong and both are checkable in minutes by
anyone who knows London. Driving recruiter traffic to that page is worse than not posting.

**Same-day mitigation** — paste this at the top of the README while you do the rebuild:

```markdown
> **⚠️ Methodology revision in progress (August 2026)**
>
> Crime data in this repository was collected using the data.police.uk
> `crimes-street/all-crime` endpoint with a single lat/lng per borough. That endpoint
> returns crimes within a **1-mile radius of a point**, not within borough boundaries,
> so each borough is sampled at between 5% and 100% of its actual area while rates are
> divided by its full resident population.
>
> The inner/outer London finding has been independently verified against MPS
> borough-level recorded crime and holds (~40%). **Individual borough rankings below
> should not be relied on** and are being rebuilt from the MPS Recorded Crime:
> Geographic Breakdown dataset.
```

Then the four line edits:

1. Project Summary — "Safest borough | Barnet (100 / 100)" → remove until rebuilt.
2. Key Findings — "Outer London boroughs are 40–60% safer" → "around 40% safer
   (verified against MPS borough-level recorded crime)".
3. Project Summary — "Highest risk | City of London, Westminster, Kensington and Chelsea"
   → "Westminster, Camden, Kensington and Chelsea".
4. Getting Started — add `git lfs install` before `git clone`.

---

## What I could not check

- Your notebooks. `.ipynb` outputs were not fetched, so the ANOVA p-value, the r > 0.85
  violence/robbery correlation, and the 4-cluster K-means result are unverified. All three
  were computed on the biased sample and should be re-run after the source swap.
- The Streamlit app and Power BI dashboard read `borough_safety_summary.csv`. I have not
  confirmed they won't break when City of London disappears and a `safety_rank` column
  appears. Check before deploying.
- The rebuilt family score uses your documented 50/30/20 formula. I could not reproduce
  your original from the published columns, so treat these numbers as a reconstruction
  and reconcile against notebook 04.
- I benchmarked against a GitHub mirror of the London Datastore MPS files rather than the
  Datastore directly (network restrictions). Its 12-month total of 931,179 offences is
  consistent with the published 951,803 for 2024/25, so I trust it for this comparison —
  but pull from data.london.gov.uk for the actual rebuild.
