# Cherry-Pick Guide 6 — The Modify/Delete Conflict (Round 6)

Sixth exercise (see guides
[1](CHERRY_PICK_GUIDE.md) ·
[2](CHERRY_PICK_GUIDE_2.md) ·
[3](CHERRY_PICK_GUIDE_3.md) ·
[4](CHERRY_PICK_GUIDE_4.md) ·
[5](CHERRY_PICK_GUIDE_5.md)).

**New skill this round:** the **modify/delete conflict** — the trickiest common
kind. `65-5-Future` **deletes** `libraries/utils.py` (it was consolidated into a
new `helpers.py`), but `65-5-Current` has a hotfix that **modified** that same
file. Git can't auto-merge "deleted here, changed there" — *you* must decide
whether the file lives or dies, and make sure the hotfix isn't silently lost.

> **Goal:** Promote the helper-consolidation commits from `65-5-Future` onto a
> branch cut from `65-5-Current`, resolve the modify/delete conflict correctly
> (without losing the hotfix's improvement), review, PR, and merge.

---

## 0. The scenario

### Commits on `65-5-Future`

| # | Commit (illustrative SHA) | Change | Cherry-pick |
| - | ------------------------- | ------ | ----------- |
| 1 | `d5c8c01` `CHP-00601` | Add `libraries/helpers.py` (consolidated helpers **with input validation**) | clean |
| 2 | `92a5e56` `CHP-00602` | **Delete** `libraries/utils.py` (superseded by helpers.py) | ⚠️ **MODIFY/DELETE** |
| 3 | `7819040` `CHP-00603` | Add `tests/api/test_helpers.robot` | clean |

### Hotfix already on `65-5-Current`

| Commit (illustrative SHA) | Change | Effect |
| ------------------------- | ------ | ------ |
| `aa73fbf` `HOTFIX-551` | Add input-type validation to `utils.py`'s `mask_secret` | conflicts with the **deletion** of `utils.py` |

> 🧩 **Why this conflicts:** `CHP-00602` says "delete `utils.py`". `HOTFIX-551`
> says "here's an important change *inside* `utils.py`". Git has no way to apply
> a patch to a file the other side removed, so it stops and asks you.

> ⚠️ **SHAs are illustrative** — read live ones from the **Log** tab or
> `git log --oneline 65-5-Current..65-5-Future`.

---

## 1–3. Fetch, target branch, feature branch

```bash
git fetch --all --prune
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10006
```

**PyCharm UI:** Fetch → check out/Update `65-5-Current` → **New Branch from
65-5-Current** named `feature/CHP-10006` → Checkout.

---

## 4. Cherry-pick the three commits

**PyCharm UI**
1. **Git** tool window → **Log** tab (`Alt+9`); filter to **`65-5-Future`**.
2. `Shift`-select `CHP-00601` … `CHP-00603` → **Right-click → Cherry-Pick**.
3. `CHP-00601` applies; `CHP-00602` stops with a **modify/delete** conflict.

**Command-line**
```bash
git cherry-pick -x d5c8c01 92a5e56 7819040
#                 601     602⚠    603
```

---

## 5. Resolve the modify/delete conflict — `libraries/utils.py`

Git prints something like:
```
CONFLICT (modify/delete): libraries/utils.py deleted in 92a5e56 (CHP-00602)
and modified in HEAD. Version HEAD of libraries/utils.py left in tree.
```
The file is **left on disk** (the HEAD/modified version) and marked unmerged.
You must choose one of two outcomes:

### ✅ Decide FIRST: is the hotfix preserved elsewhere?

Before deleting anything, confirm `HOTFIX-551`'s change isn't lost. Open the new
`libraries/helpers.py` — its `mask_secret` **already validates input type**
(`raise TypeError(...)`), which is exactly what the hotfix added to `utils.py`.
So the improvement survives the deletion. **That makes "accept the deletion"
the correct resolution here.**

> ⚠️ If `helpers.py` did **not** already contain the hotfix's behaviour, you
> would instead **port the hotfix into `helpers.py` first**, then delete
> `utils.py`. Never accept a deletion that silently drops a live fix.

### Option A — accept the deletion (recommended here)

**PyCharm UI**
- In the **Conflicts** dialog / **Local Changes**, right-click
  `libraries/utils.py` → **Resolve** → choose **Accept Theirs** (the incoming
  *deletion*). PyCharm removes the file.
- Alternatively use the merge dialog's *"Accept the deletion / remove file"*
  prompt shown for modify/delete conflicts.

**Command-line**
```bash
git rm libraries/utils.py        # honour the deletion
git cherry-pick --continue
```

### Option B — keep the modified file (only if utils.py is still needed)

**PyCharm UI:** right-click `utils.py` → **Resolve** → **Accept Yours** (keep
the HEAD/modified version).
**Command-line:** `git add libraries/utils.py && git cherry-pick --continue`

> For this exercise use **Option A** — `helpers.py` supersedes `utils.py` and
> keeps the hotfix behaviour, so keeping the old file would leave dead,
> duplicated code.

After resolving, `CHP-00603` (the test) applies cleanly.

---

## 6. Review

```bash
git log --oneline 65-5-Current..feature/CHP-10006     # expect 3 commits
test -f libraries/utils.py && echo "utils.py STILL present (Option B)" || echo "utils.py removed (Option A) ✓"
test -f libraries/helpers.py && echo "helpers.py present ✓"
python -c "import ast; ast.parse(open('libraries/helpers.py').read()); print('helpers.py valid')"
```

**PyCharm UI:** **Git → Log** — confirm 3 commits; in the Project view confirm
`utils.py` is gone and `helpers.py` + `test_helpers.robot` are present.

> 🔎 **Grep for stragglers:** make sure nothing on `65-5-Current` still imports
> `utils` (`grep -rn "import utils\|from .*utils" libraries tests resources`).
> In this repo nothing does — but on a real codebase, a modify/delete resolution
> that removes a file must be paired with updating its importers.

---

## 7–9. Push, PR, merge

```bash
git push -u origin feature/CHP-10006
gh pr create --base 65-5-Current --head feature/CHP-10006 \
  --title "Consolidate helpers into helpers.py on 65-5-Current" \
  --body "Cherry-picked CHP-00601..00603 from 65-5-Future. Resolved modify/delete on utils.py by accepting the deletion (helpers.py supersedes it and already includes HOTFIX-551's input validation)."

# after merge:
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10006
git push origin --delete feature/CHP-10006   # if not auto-deleted
```

> ⚠️ **One PR, base = `65-5-Current`.** Change the base dropdown from the
> default `develop` and don't open a second PR (this bit us in earlier rounds).

**PyCharm UI:** **Git → Push** → **GitHub → Create Pull Request** (base
`65-5-Current`) → merge → delete branch → Fetch + Update `65-5-Current`.

---

## Quick reference

```bash
git fetch --all --prune
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10006

git cherry-pick -x d5c8c01 92a5e56 7819040
#   modify/delete on utils.py:
#     verify helpers.py keeps the hotfix behaviour, then:
#     git rm libraries/utils.py
#     git cherry-pick --continue

git log --oneline 65-5-Current..feature/CHP-10006   # 3 commits; utils.py gone
git push -u origin feature/CHP-10006
gh pr create --base 65-5-Current --head feature/CHP-10006 --title "..." --body "..."
# merge PR (base 65-5-Current), then sync + delete branch
```

---

## What to double-check this round

- **Decided the modify/delete deliberately** — you accepted the deletion
  *because* `helpers.py` preserves the hotfix, not by reflex.
- **`utils.py` is gone, `helpers.py` remains**, and no code imports the old
  module.
- **3 commits promoted**, test applies on top.
- **One PR, base `65-5-Current`.**
- **Provenance** — `-x` records `(cherry picked from commit <sha>)`.
