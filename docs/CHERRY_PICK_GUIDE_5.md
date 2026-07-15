# Cherry-Pick Guide 5 — Surgical Hotfix Extraction & Code Conflicts (Round 5)

Fifth exercise (see guides
[1](CHERRY_PICK_GUIDE.md) ·
[2](CHERRY_PICK_GUIDE_2.md) ·
[3](CHERRY_PICK_GUIDE_3.md) ·
[4](CHERRY_PICK_GUIDE_4.md)).

**New skills this round:**
1. **Surgical extraction** — `65-5-Future` is mid-way through a *report-exporter*
   feature, but a **single urgent bugfix** (plus its test) needs to reach the
   current release **now**. You promote **only those 2 commits**, leaving the
   unfinished feature behind.
2. **A real Python *code* conflict** — the bugfix and a hotfix both rewrote the
   same function, `DataLoader.find_user`. You merge *logic*, not just a value.

> **Goal:** Cherry-pick just the urgent `find_user` fix and its test from
> `65-5-Future` onto a feature branch cut from `65-5-Current`, resolve the code
> conflict, review, PR, and merge — without dragging in the exporter feature.

---

## 0. The scenario

### Commits on `65-5-Future`

| # | Commit (illustrative SHA) | Change | Promote now? |
| - | ------------------------- | ------ | ------------ |
| 1 | `113daaf` `CHP-00501` | Add `ReportExporter` library | 🚫 no — feature WIP |
| 2 | `28819b1` `CHP-00502` | Add export config block (settings.yaml) | 🚫 no — feature WIP |
| 3 | `aafd8a3` `CHP-00503` | **URGENT:** `find_user` case-insensitive + trim (data_loader.py) | ✅ **YES** |
| 4 | `695fdc1` `CHP-00504` | Regression test for the lookup fix | ✅ **YES** |
| 5 | `8cf4671` `CHP-00505` | Add export CLI entry point | 🚫 no — feature WIP |

You want **only #3 and #4**. The exporter commits (#1, #2, #5) are unfinished
next-release work — promoting them would ship half a feature to the current
release line.

### Hotfix already on `65-5-Current`

| Commit (illustrative SHA) | Change | Effect |
| ------------------------- | ------ | ------ |
| `4d32a8b` `HOTFIX-541` | `find_user` now **raises `KeyError`** on a missing user (was returning `None`) | conflicts with `CHP-00503` |

> ⚠️ **SHAs are illustrative** — read live ones from the **Log** tab or
> `git log --oneline 65-5-Current..65-5-Future` (ignore older already-promoted
> commits that reappear with new SHAs).

---

## 1–3. Fetch, target branch, feature branch

```bash
git fetch --all --prune
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10005
```

**PyCharm UI:** Fetch → check out/Update `65-5-Current` → **New Branch from
65-5-Current** named `feature/CHP-10005` → Checkout.

---

## 4. Cherry-pick ONLY the two urgent commits

The two commits you want (`CHP-00503`, `CHP-00504`) are adjacent, but they sit
*between* feature commits you must not take. Select **precisely those two**.

**PyCharm UI**
1. **Git** tool window → **Log** tab (`Alt+9`); filter to **`65-5-Future`**.
2. **`Ctrl+Click`** `CHP-00503`, then **`Ctrl+Click`** `CHP-00504` — leave
   `CHP-00501`, `CHP-00502`, `CHP-00505` **unselected**.
3. **Right-click → Cherry-Pick**. It applies `CHP-00503` first (the fix), hits
   the conflict, then — after you resolve — applies `CHP-00504` (the test).

**Command-line** — name the two SHAs, fix before test (chronological order):
```bash
git cherry-pick -x aafd8a3 695fdc1
#                 503⚠    504
```

> 💡 **Order matters:** apply the **fix (`CHP-00503`) before the test
> (`CHP-00504`)** — otherwise the test lands on code that hasn't been fixed yet.

---

## 5. Resolve the code conflict — `libraries/data_loader.py` (CHP-00503)

Open **Merge…** (3-pane; **Left = Yours / 65-5-Current**, **Right = Theirs /
incoming CHP-00503**). The two sides changed the *same function* differently:

**Yours (HOTFIX-541)** — fail loudly on a missing user:
```python
    def find_user(self, username: str) -> Dict[str, Any]:
        for user in self.load_users():
            if user.get("username") == username:
                return user
        raise KeyError(f"User not found: {username!r}")
```

**Theirs (CHP-00503)** — match case-insensitively / trim whitespace:
```python
    def find_user(self, username: str) -> Optional[Dict[str, Any]]:
        target = username.strip().lower()
        for user in self.load_users():
            if user.get("username", "").strip().lower() == target:
                return user
        return None
```

**Recommended resolution — keep BOTH behaviours** (case-insensitive matching
*and* raise-on-missing):
```python
    def find_user(self, username: str) -> Dict[str, Any]:
        target = username.strip().lower()
        for user in self.load_users():
            if user.get("username", "").strip().lower() == target:
                return user
        raise KeyError(f"User not found: {username!r}")
```
*Rationale:* the incoming fix corrects the *matching* logic (the urgent bug);
the hotfix improved the *not-found* behaviour. They're orthogonal — combine
them. Note the return type stays `Dict[str, Any]` (it raises rather than
returning `None`), matching the hotfix's contract.

Then **Apply** → **Continue Cherry-Pick** (the test `CHP-00504` applies cleanly
after).

**Command-line**
```bash
# after editing data_loader.py to the merged function:
git add libraries/data_loader.py
git cherry-pick --continue
```

---

## 6. Review

You should have **exactly 2** new commits, and **none** of the exporter files.

```bash
git log --oneline 65-5-Current..feature/CHP-10005        # expect 2 commits (503, 504)
ls libraries/report_exporter.py libraries/export_cli.py 2>/dev/null \
  && echo "OOPS: exporter feature leaked" || echo "OK: exporter feature left behind"
python -c "import ast; ast.parse(open('libraries/data_loader.py').read()); print('data_loader.py valid')"
```

**PyCharm UI:** **Git → Log** — confirm 2 commits and that `report_exporter.py`
/ `export_cli.py` are **absent** from the branch.

---

## 7–9. Push, PR, merge

```bash
git push -u origin feature/CHP-10005
gh pr create --base 65-5-Current --head feature/CHP-10005 \
  --title "URGENT: promote find_user case-insensitive fix to 65-5-Current" \
  --body "Cherry-picked CHP-00503 + CHP-00504 from 65-5-Future. Left exporter feature (501/502/505) behind. Resolved data_loader.py conflict by combining case-insensitive matching with HOTFIX-541's raise-on-missing."

# after merge:
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10005
git push origin --delete feature/CHP-10005   # if not auto-deleted
```

> ⚠️ **Create ONE PR, base = `65-5-Current`.** In rounds 3 and 4 the feature
> branch got a *second* PR into `develop` by accident — when the PR form opens,
> change the **base** dropdown from the default (`develop`) to **`65-5-Current`**
> and don't open a second PR.

**PyCharm UI:** **Git → Push** → **GitHub → Create Pull Request** (base
`65-5-Current`) → merge → delete branch → Fetch + Update `65-5-Current`.

---

## Quick reference

```bash
git fetch --all --prune
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10005

git cherry-pick -x aafd8a3 695fdc1     # fix then test; ONLY these two
#   conflict in data_loader.py -> merge both behaviours -> git add libraries/data_loader.py -> git cherry-pick --continue

git log --oneline 65-5-Current..feature/CHP-10005   # 2 commits, no exporter files
git push -u origin feature/CHP-10005
gh pr create --base 65-5-Current --head feature/CHP-10005 --title "..." --body "..."
# merge PR (base 65-5-Current), then sync + delete branch
```

---

## What to double-check this round

- **Exactly 2 commits promoted** — `CHP-00503` + `CHP-00504`. No
  `report_exporter.py`, `export_cli.py`, or the `export:` settings block.
- **Merged function keeps both behaviours** — case-insensitive/trim matching
  **and** `raise KeyError` on missing.
- **Fix applied before test** — the test commit should sit *on top of* the fix.
- **One PR, base `65-5-Current`** — not `develop`.
- **Provenance** — `-x` records `(cherry picked from commit <sha>)`.
