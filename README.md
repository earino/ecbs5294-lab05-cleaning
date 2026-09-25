# Lab 5 — The clean table that is not clean

**ECBS5294 — Working with Data · Session 3, Block 5**

## Start here

| | |
|---|---|
| **The question** | How much municipal waste did each country generate per person in 2024, and how has that changed since 2010? |
| **The file** | `data/raw/env_wasmun.tsv` — Eurostat, municipal waste, as Eurostat publishes it. What silver must contain: `docs/dictionary.md`. |
| **What is wrong** | The pipeline runs without an error, and its report disagrees with the raw file. |
| **What you hand in** | `DIAGNOSIS.md` on Moodle, before you leave. |
| **First thing to do** | `uv run python pipeline.py`, and read the report. **No AI for the first 20 minutes.** |

## Where things are

| | Where | What you do there |
|---|---|---|
| **Run** | the terminal, in the project folder | `uv run python pipeline.py`: it runs `clean.py`, then `report.py`, and prints the report |
| **Inspect** | `notebooks/diagnose.ipynb` (kernel: `.venv`), and `grep` in the terminal | look at the raw cells; nothing here changes a file |
| **Edit** | `scripts/clean.py`, sections **C**, **E** and **F** only | A, B and D are supplied; `report.py` is not yours |
| **Record** | `DIAGNOSIS.md` | paste each query and what it returned, **before** you change `clean.py` |

**Your first three actions:** (1) run the pipeline and read the report; (2) run the `grep` under *What is broken*;
(3) open `notebooks/diagnose.ipynb`, pick the `.venv` kernel, and run it from the top.

## Get the project

If you cloned it during the stretch, you already have it. Otherwise, in your terminal (Git Bash on Windows,
Terminal on macOS), in the folder where you keep course work:

```bash
git clone https://github.com/earino/ecbs5294-lab05-cleaning.git
cd ecbs5294-lab05-cleaning
uv sync
```

Open **this folder** in VS Code (*File → Open Folder…*). This lab is a **pipeline**, not a notebook. From the project
folder, in the terminal:

```bash
uv run python pipeline.py
```

`pipeline.py` runs two scripts, in order:

- `scripts/clean.py` — raw to **silver**: reads `data/raw/env_wasmun.tsv` (never edits it) and writes
  `data/silver/waste.parquet`, and every observation that is not in silver to `data/silver/rejects.csv`, with its
  reason. A colleague wrote it, reusing the steps from another Eurostat file.
- `scripts/report.py` — silver to **gold**: writes `data/gold/waste_per_inhabitant.csv` and prints it. It is correct
  if silver is right. Do not change it.

`notebooks/diagnose.ipynb` is where you look at the data (pick the `.venv` kernel). The pipeline never reads it.

`data/raw/` has two data files. `env_air_gge_ghg.tsv` is the one the lecture used. This lab is about `env_wasmun.tsv`.

## What is broken

The report says **15 countries** have a 2024 value. Germany, France and Spain are among the blanks.

Eurostat's file has a 2024 value for Germany. See for yourself, in the terminal:

```bash
grep 'A,GEN,KG_HAB,DE' data/raw/env_wasmun.tsv
```

The last column is 2024, and it is not empty. Nothing errors. Find out why, before you change anything.

## What you must produce

`scripts/clean.py` has six sections. **A** (bronze), **B** (long, and Eurostat's flag list) and **D** (write silver
and `rejects.csv`) are supplied: do not change them. **C** is the colleague's parse: you rewrite it. **E** and **F**
are empty: they are yours.

1. **Look** (`notebooks/diagnose.ipynb`). Five questions. Questions 1 and 4 are supplied: run them and read them.
   Questions 2 and 3 are the lecture's queries, on this file. **Question 5 is yours, from the empty cell**: which of
   the report's blanks are right, and which did the cast make? Paste each query and what it returned into
   `DIAGNOSIS.md`, part 3, **before** you change `scripts/clean.py`.
2. **The parse — rewrite section C.** It must still end with two views. `parsed`: every observation of `long`, with
   the number in `value`, Eurostat's flag in `flag`, `NULL` where Eurostat wrote `:`, and a `reason` that is `NULL`
   when the observation goes into silver and says why when it does not. `silver`: the dictionary's columns
   (`docs/dictionary.md`), one unit (`KG_HAB`). An observation whose cell **cannot be read** — it is empty, its number
   does not parse, or its flag is not in Eurostat's list (the `flags` view, from `data/raw/codelist_obs_flag.tsv`) —
   gets a reason that starts `cannot be read`, and does not reach silver. Run the pipeline again and read the report.
3. **The accounting — section E**, from the empty space: no query on screen does it for you. The lecture's four
   destinations, in their order, **counted from the two files section D wrote**:
   - **rejected** (cannot be read) and **excluded** (not `KG_HAB`): the rows of `data/silver/rejects.csv`, by reason;
   - **aggregate** (`EU27_2020`, in silver with `is_aggregate` true) and **retained** (everything else in silver; a
     `:` is retained, as `NULL`): the rows of `data/silver/waste.parquet`.

   Print them as one line that adds up to the observations in `long`, on every run. Stop the run if it does not.
4. **The key check — section F.** Stop the run, with the number in the message, if silver's key is not unique.
   The dictionary says what one row of silver is.
5. `DIAGNOSIS.md`, all five parts, short. **Keep five minutes for it.** Then the last ten minutes, below, and the
   Moodle checkpoint.

## Rules

- **Never edit `data/raw/`.** The raw data is the evidence. Fix the script that reads it.
- **Do not change `scripts/report.py`.** It is correct if silver is right, so the fix belongs in `scripts/clean.py`.
- **No AI for the first 20 minutes** of the lab. Look at the values with your own eyes first.
- After that, you may use AI to explain an error or a function. You must be able to explain every line you hand in:
  your neighbour will ask, at the end, without notes.

## Hints, if stuck

Staff will say these over the room at minutes 5, 10, and 15. Read them earlier if you want.

1. Question 1 shows you the cell for a country the report left blank. Now look at the cell for a country the report
   did fill, in the same year. What is different about the two cells?
2. Put the two cells through the colleague's cast, `TRY_CAST(cell AS DOUBLE)`. What does each one return? Question 3
   counts every cell that behaves like the first one.
3. The cast returns `NULL`, with no error, for any text that is not just a number. Eurostat writes a flag after some
   numbers: `628 e` is 628, estimated. Silver needs the number and the flag as two columns — and `:` is not a number
   either.

## Diagnosis note

In `DIAGNOSIS.md`: the template is there. Part 3 is the notebook's five queries and their output; question 5's
split is the heart of it. Part 4 is your section C. Part 5 is the accounting line your pipeline prints, the key check,
and one reconciliation: the number of countries with a 2024 value in gold, against question 5's cells that hold a
number.

## Stretch task

None. This is the heaviest lab of the course. If you finish early, run the pipeline twice and compare what it wrote:
`cksum data/silver/* data/gold/*` after each run prints a checksum per file. The two runs must make the same files.

## Git thread

`data/raw/` is committed on purpose. `data/silver/` and `data/gold/` are not: the pipeline makes them, so `.gitignore`
leaves them out. After a run, `git status` shows your script as changed, and never a silver file.

Commit after the accounting works. The message says what the cause was, and carries the accounting line, e.g.
"Keep Eurostat's flag in its own column; in = rejected + excluded + aggregate + retained, with the four numbers" — not
"fix".

## The last ten minutes

When staff call it — minute 33 of a lab that starts on time, later if the lab started early — finished or not, turn to
the person next to you (three if the row is odd). One of you explains, about a minute: what was wrong, why, the query
that proved it, what you changed, how you know it is right. Point at the screen; do not read the note. The other asks:

1. **Show me the query that proves it.**
2. **Why was it wrong, not just where?**
3. **The what-if question on the slide.**

Then swap. If either of you is unsure, or you disagree, put a hand up: staff come to you first. Then the answer to
the what-if, for everyone. An unfinished repair is explained the same way: what you found so far.

Before you leave: the lab's **checkpoint on Moodle**. Upload `DIAGNOSIS.md` with its first line filled in. That is
what "complete" means; nobody signs you off.

## If you got lost: how to reset

Both of these **destroy work**. Read before running.

**Discard uncommitted changes (destructive)** — throw away edits and new files; keep your commits:

```bash
git restore --staged --worktree .    # every tracked file back to the last commit, staged or not
git clean -fd                        # and remove new, untracked files
```

> ⚠️ Permanently deletes uncommitted changes, staged or not, and any new untracked files.

**Full reset to the starter state (destructive)** — back to exactly what you cloned; throws away your commits too:

```bash
git reset --hard origin/main
git clean -fdx
```

> ⚠️ Discards your local commits and uncommitted changes. The `-x` also removes ignored files — `data/silver/`,
> `data/gold/`, the `.venv/` environment — so the folder matches a fresh clone. `uv sync` rebuilds the environment in
> a minute.
