# Cherry-Pick Guide 4 — Ranges, Empty Commits & Value Conflicts (Round 4)

Fourth exercise (see guides
[1](CHERRY_PICK_GUIDE.md) ·
[2](CHERRY_PICK_GUIDE_2.md) ·
[3](CHERRY_PICK_GUIDE_3.md)).

**New skills this round:**
1. **Range cherry-pick** — promote a *contiguous* block of commits in one go.
2. **An "already applied / empty" commit** — one Future fix was *also* applied
   directly on `65-5-Current` as a hotfix, so cherry-picking it produces **no
   changes**. You'll learn to **skip** it.
3. **A value conflict with no obviously-right answer** — two teams picked
   different numbers for the same setting; you resolve to a deliberate value.

> **Goal:** Promote the round-4 *logging/observability* commits from
> `65-5-Future` onto a feature branch cut from `65-5-Current`, skip the empty
> commit, resolve the one conflict, review, PR, and merge.

---

## 0. The scenario

### New work on `65-5-Future`

| # | Commit (illustrative SHA) | Change | Cherry-pick result |
| - | ------------------------- | ------ | ------------------ |
| 1 | `4ded330` `CHP-00401` | Add structured `logging:` block (settings.yaml) | clean |
| 2 | `0c111e5` `CHP-00402` | Add `LogFormatter` library (new file) | clean |
| 3 | `c78034e` `CHP-00403` | Harden `mask_secret` → reveal last **2** chars (utils.py) | 🟡 **EMPTY** (already on Current) |
| 4 | `cc0d361` `CHP-00404` | Add structured-logging test suite (new file) | clean |
| 5 | `755a8ce` `CHP-00405` | Raise `retain_days` 14 → **30** (settings.yaml) | ⚠️ **CONFLICT** |

### Hotfixes already on `65-5-Current`

| Commit (illustrative SHA) | Change | Effect on cherry-pick |
| ------------------------- | ------ | --------------------- |
| `637c25a` `HOTFIX-531` | Same `mask_secret` hardening (last **2** chars) | makes `CHP-00403` **empty** |
| `46f8fe1` `HOTFIX-532` | Cut `retain_days` 14 → **7** (storage cost) | conflicts with `CHP-00405` |

> 🟡 **Why is `CHP-00403` empty?** `HOTFIX-531` made the *identical* change on
> `65-5-Current` already. Git tries to apply the patch, finds the result is
> already present, and pauses with *"The previous cherry-pick is now empty."*
> That's expected — you **skip** it (below), you don't force an empty commit.

> ⚠️ **SHAs are illustrative** — read live ones from the **Log** tab or
> `git log --oneline 65-5-Current..65-5-Future` (that range also lists older
> already-promoted commits with new SHAs — ignore those; promote only the
> `CHP-004xx` block).

---

## 1–3. Fetch, target branch, feature branch

**Command-line**
```bash
git fetch --all --prune
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10004
```

**PyCharm UI:** Fetch → check out/Update `65-5-Current` → **New Branch from
65-5-Current** named `feature/CHP-10004` → Checkout.

---

## 4. Cherry-pick the whole RANGE at once

This round the 5 commits are contiguous and you want *all* of them, so use the
**range** form (contrast with round 3's `Ctrl+Click` subset).

**PyCharm UI**
1. **Git** tool window → **Log** tab (`Alt+9`); filter to **`65-5-Future`**.
2. Click `CHP-00401`, then **`Shift+Click`** `CHP-00405` to select the whole
   block of five.
3. **Right-click → Cherry-Pick**. PyCharm applies oldest-first and will pause
   **twice**: once on the empty `CHP-00403`, once on the `CHP-00405` conflict.

**Command-line** — the `A..B` range expands to those commits (oldest-first):
```bash
git cherry-pick -x 65-5-Future~4..65-5-Future
#   == CHP-00401 CHP-00402 CHP-00403 CHP-00404 CHP-00405
# (or list them explicitly: git cherry-pick -x 4ded330 0c111e5 c78034e cc0d361 755a8ce)
```

> 💡 `A..B` is **exclusive of A**. `65-5-Future~4..65-5-Future` means "the last
> 5 commits of Future" — double-check the count in the Log before running it.

---

## 5. Handle the EMPTY commit — `CHP-00403`

When the sequence reaches `CHP-00403`, it stops because the change is already
present on `65-5-Current`.

**PyCharm UI**
- PyCharm shows a dialog noting the commit is empty / already applied. Choose
  **Skip commit** (do **not** "Commit anyway" — that would create a pointless
  empty commit in the history).

**Command-line**
```bash
git cherry-pick --skip     # drop the empty commit, continue the sequence
```

> ✅ Skipping is correct here: the security fix is *already* on the branch via
> `HOTFIX-531`. An empty commit would just be noise.

---

## 6. Resolve the value conflict — `config/settings.yaml` (CHP-00405)

The sequence next stops on `retain_days`. Open **Merge…** (3-pane editor;
**Left = Yours / 65-5-Current**, **Right = Theirs / incoming CHP-00405**).

| Setting | Yours (HOTFIX-532) | Theirs (CHP-00405) |
| ------- | ------------------ | ------------------ |
| `retain_days` | `7` (storage cost) | `30` (observability) |

Neither number is automatically "right" — it's a genuine trade-off. **Decide,
and type the chosen value into the centre pane.** A common resolution is a
**deliberate compromise**:
```yaml
  screenshots_on_failure: true
  retain_days: 14
```
*Rationale:* `30` risks the storage budget the hotfix was defending; `7` may be
too short to investigate flaky failures. `14` honours both intents. (If your
team has provisioned storage, `30` is equally valid — the point is that you
**chose**, rather than blindly accepting a side.)

Then **Apply** → **Continue Cherry-Pick**.

**Command-line**
```bash
# after setting retain_days to your chosen value:
git add config/settings.yaml
git cherry-pick --continue
```

---

## 7. Review

You should end with **4** new commits on `feature/CHP-10004` (401, 402, 404,
405 — **not** 403, which was skipped).

```bash
git log --oneline 65-5-Current..feature/CHP-10004     # expect 4 commits, no CHP-00403
grep retain_days config/settings.yaml                 # your chosen value
python -c "import yaml; yaml.safe_load(open('config/settings.yaml')); print('settings.yaml valid')"
```

**PyCharm UI:** **Git → Log** — confirm 4 commits and that `CHP-00403` is absent.

---

## 8–10. Push, PR, merge

```bash
git push -u origin feature/CHP-10004
gh pr create --base 65-5-Current --head feature/CHP-10004 \
  --title "Promote logging/observability to 65-5-Current" \
  --body "Cherry-picked CHP-00401,402,404,405 from 65-5-Future. Skipped CHP-00403 (already on Current via HOTFIX-531). Resolved retain_days conflict to 14 (compromise between 7 and 30)."

# after merge:
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10004
git push origin --delete feature/CHP-10004   # if not auto-deleted
```

**PyCharm UI:** **Git → Push** → **GitHub → Create Pull Request** (base
`65-5-Current`) → merge → delete branch → Fetch + Update `65-5-Current`.

> ⚠️ **PR base = `65-5-Current`.** (In an earlier round the feature branch was
> accidentally also merged into `develop` — double-check the **base** dropdown
> reads `65-5-Current`, not `develop`, before you create the PR.)

---

## Quick reference

```bash
git fetch --all --prune
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10004

git cherry-pick -x 65-5-Future~4..65-5-Future
#   empty at CHP-00403     -> git cherry-pick --skip
#   conflict at CHP-00405  -> edit settings.yaml -> git add config/settings.yaml -> git cherry-pick --continue

git log --oneline 65-5-Current..feature/CHP-10004   # 4 commits, no CHP-00403
git push -u origin feature/CHP-10004
gh pr create --base 65-5-Current --head feature/CHP-10004 --title "..." --body "..."
# merge PR, then sync + delete branch
```

---

## What to double-check this round

- **Only 4 commits promoted** — `CHP-00403` must **not** appear on your feature
  branch (it was empty/skipped). If you see it, you clicked *Commit anyway*
  instead of *Skip*.
- **`retain_days` is your chosen value**, applied intentionally — not silently
  clobbered to one side.
- **Result isn't identical to `65-5-Future`** — expected: you skipped a commit
  and may have chosen a compromise value.
- **Base branch of the PR is `65-5-Current`** — not `develop`.
- **Provenance** — `-x` records `(cherry picked from commit <sha>)` on each
  promoted commit.
