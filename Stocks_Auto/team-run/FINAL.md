# FINAL DELIVERY

## What You Got

- **`Stocks_Auto/03_Pipeline.py`** — the end-to-end entry point: fetch (6 sources) → rules.md filter → dedup → group by company → summarize (rule-based, zero LLM) → write JSON.
- **`Stocks_Auto/config.py`** — central config (source list, output path, dedup threshold, etc.), replaces the hardcoded other-machine path from the original draft.
- **`Stocks_Auto/fetch_common.py` + `fetch_cnyes.py` / `fetch_udn.py` / `fetch_ctee.py` / `fetch_ptt.py` / `fetch_youtube.py`** — the five HTML/RSS fetchers (Yahoo's fetcher, `02_Fetch_Yahoo.py`, was pre-existing and untouched).
- **`Stocks_Auto/rules.py` + `rules.md`** — filter rules (600-char minimum, same-day-only, YouTube financial-keyword filter).
- **`Stocks_Auto/dedup.py`** — title-similarity + body-Jaccard + distinguishing-term dedup (fixed in Revision Round 1 after a real over-merge was caught).
- **`Stocks_Auto/grouping.py`** — groups articles by TWSE/TPEx-listed company, using a 1,980-company lookup table cached at `Stocks_Auto/cache/company_map.json` (fixed in Revision Round 1 after 6/7 audited groups were found to be false positives).
- **`Stocks_Auto/summarize.py` + `12_Martix_DataSheet.py`** — rule-based summary (title + first ~150 chars) plus TF-IDF keyword tags per group; no LLM/AI model calls anywhere in the codebase (independently grep-verified twice, by both reviewers).
- **`Stocks_Auto/websites/Stocks/backend/data/2026-07-14.json`** — the actual, real (non-sample) output of a live run: 53 articles, 20 groups. **This is the file to look at as proof the pipeline works.**
- **`Stocks_Auto/01_Data_Search.py`** — kept (not deleted), header-annotated as SUPERSEDED; no longer called by the pipeline. `10_LangChain.py` and `11_LamaIndex.py` are confirmed gone from disk.
- `team-run/PLAN.md`, `RESEARCH.md`, `BUILD_LOG.md`, `REVIEW.md`, `REVIEW_ROUND2.md` — the full paper trail behind this delivery.

## How It Was Verified

- **This integration pass**: re-listed `Stocks_Auto/` and `websites/Stocks/backend/data/` on disk — every file BUILD_LOG.md claims to have produced genuinely exists, sizes/timestamps are consistent with a real run. Loaded `2026-07-14.json` with `json.load` via the project's own `.venv` — parses cleanly, correct schema (`date`/`generated_at`/`group_count`/`total_articles`/`groups[].{group,keywords,article_count,articles}`), Chinese text is correct UTF-8 (a garbled first read was a Windows-console codepage display issue, not a data problem — confirmed by re-reading the raw file, which shows correct characters). Confirmed `10_LangChain.py`/`11_LamaIndex.py` are absent from disk.
- **Round 1 review (REVISE)**: independently caught 3 real defects the Builder's own tests missed — grouping false positives (6/7 audited groups wrong), silent mid-word summary truncation on non-Yahoo sources, and a dedup over-merge that silently deleted a distinct article's content.
- **Round 2 review (PASS)**: independently re-ran the full pipeline itself (not just re-reading the Builder's output), re-fetched live source pages to cross-check grouping decisions, wrote its own coverage script over all non-Yahoo summaries, and confirmed genuine duplicates still merge correctly (fix didn't just disable dedup). Two MINOR, non-blocking observations were logged, not fixed (see below).
- **Zero-LLM constraint**: `grep -riE "openai|anthropic|generativeai|import.*gpt|api_key"` run independently by both the Builder and both reviewers across all project `.py` files — zero hits in project code (the only hits, before excluding `.venv`, were inside the third-party `youtube_transcript_api` library's own internal YouTube player-API key handling, unrelated to any LLM).

No verification work was redone in this pass beyond the smoke checks above — the review gate already did the substantive work, twice.

## Confidence & Assumptions (carried from the whole pipeline)

**High confidence, verified directly:**
- Pipeline runs end-to-end without crashing and produces a valid, correctly-schemed JSON file at the right path. [High]
- Zero LLM API calls anywhere in project code. [High]
- Grouping false-positive, summary-truncation, and dedup over-merge bugs found in Round 1 are genuinely fixed, not just claimed fixed. [High — independently re-verified on live data in Round 2]

**Known Limitations carried forward honestly (not solved, not hidden):**
- **(a) YouTube currently contributes zero content.** The fetcher is fully wired up (RSS discovery of the day's videos from 57東森財經新聞, financial-keyword filtering, transcript fetch with graceful fallback) and does not crash the pipeline — but as of every run performed during this build (including the reviewer's independent re-run), 0/15 candidate videos had usable transcripts (`TranscriptsDisabled` / `VideoUnplayable`). This is a YouTube-side limitation (anti-bot/PoToken measures still evolving per RESEARCH.md), not a bug in the code, but it means the YouTube source is currently decorative — it may start working on a future day, or may not.
- **(b) cnyes / udn / ctee are HTML-scraping based**, not official RSS (none could be found for these three despite a real search — see RESEARCH.md finding #2). They are meaningfully more fragile than the Yahoo RSS source: any front-end redesign (class names, JSON-LD structure) can silently break them. `fetch_ctee.py` already broke once during the build (JSON-LD-as-array vs. object) and was fixed, which is itself evidence this class of breakage is real and will likely recur. Each fetcher fails soft (returns an empty list, doesn't crash the pipeline) but "doesn't crash" is not the same as "still works."
- **(c) PTT scraping is a ToS/legal gray area.** No robots.txt exists for ptt.cc (confirmed by direct request), and there's no public ToS explicitly permitting automated scraping. The `over18` cookie bypass is a well-established community technique, not a novel risk, and you (the user) already knowingly accepted this trade-off at the Q2 planning stage. It is not further mitigated in this build — it's a known, accepted risk, not a solved one.
- **(d) `COMMON_WORD_COLLISION_KEYWORDS` in `grouping.py` is an inherently unbounded list**, per the Round 2 reviewer's own explicit judgment. During the build, each additional pipeline run surfaced at least one *new* short-company-name-collides-with-a-common-word case (世界, 新建, 中華, 大田, 三星, 力士) that hadn't been anticipated. All cases found so far are fixed and regression-tested, and the Round 2 reviewer judged the residual risk acceptable for v1 — but this is explicitly a "living list," not a closed, permanently-solved problem. Expect future days' news to surface new collisions that will need to be added by hand.
- **(e) You still need to manually move/sync `Stocks_Auto/websites/Stocks/backend/data/` into your actual separate Websites repo.** This was your own stated plan at the Q4 planning stage ("先預設為websites/Stocks/backend/data/我會搬移過去到那個repo當中") — the pipeline deliberately does not automate this cross-repo sync.
- Two additional MINOR items from Round 2 (non-blocking, informational): grouping's first-match-wins design can occasionally attach a broad market-wrap article to one of several companies it happens to name in passing (not a wrong-entity false positive, just a "which of several valid entities" ambiguity); and dedup's `BODY_SIMILARITY_MIN=0.15` threshold and `_code_near()` 20-character window are experience-based defaults, not exhaustively tuned.

## Suggested Next Steps

**How to run it yourself:**
1. Open a terminal in `Stocks_Auto/`.
2. Activate the existing virtual environment: `.venv\Scripts\activate` (or call `.venv\Scripts\python.exe` directly without activating).
3. Run `python 03_Pipeline.py` (or `.venv\Scripts\python.exe 03_Pipeline.py`).
4. Output lands at `Stocks_Auto/websites/Stocks/backend/data/yyyy-mm-dd.json` for today's date.

**No scheduling is set up.** This was a deliberate v1 stop-condition exclusion (see PLAN.md Q5/M8) — the pipeline only runs when you run it manually. It does **not** run automatically every day at 15:00 as your original draft assumed. If you want that, RESEARCH.md already has a ready-to-use recipe (finding #5): wrap the venv's `python.exe`/`pythonw.exe` call in a `.bat` file that `cd`s into the project directory first, then register it with `schtasks /Create /SC DAILY /TN "StocksAutoDaily" /TR "C:\path\to\run.bat" /ST 15:00 /RL HIGHEST /F`. Nobody has done this yet — it's a real gap, not an oversight to be quietly assumed away.

Optional, non-blocking polish for a future iteration (none of this is required for v1 to be usable):
- Add new entries to `COMMON_WORD_COLLISION_KEYWORDS` as they're discovered on future days (see Limitation (d)).
- Periodically spot-check cnyes/udn/ctee fetchers still work, since they depend on unstable HTML structure rather than a stable RSS contract.
- If YouTube transcripts remain permanently unavailable for this channel, consider swapping to a different channel known to caption its uploads, or accepting the source as currently non-contributing.
- If you want daily automation, wire up Windows Task Scheduler per the recipe above.
