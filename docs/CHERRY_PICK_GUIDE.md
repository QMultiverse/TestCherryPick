# Cherry-Pick Guide — Promoting `65-5-Future` changes to `65-5-Current`

This guide walks through promoting selected commits from **`65-5-Future`**
into **`65-5-Current`** using a **cherry-pick** workflow, performed almost
entirely from the **PyCharm UI**. Equivalent Git commands are given at each
step for reference.

> **Goal:** Take the release-65.5 feature commits that currently live only on
> `65-5-Future`, apply the chosen ones onto a new feature branch cut from
> `65-5-Current`, review, push, raise a Pull Request on GitHub, and merge it
> back into `65-5-Current`.

---

## 0. Branch model & starting point

| Branch          | Role                                                        |
| --------------- | ----------------------------------------------------------- |
| `develop`       | Integration branch — base for both release branches         |
| `65-5-Future`   | Next-release work: new tests, libraries, config, test data  |
| `65-5-Current`  | Current-release stabilisation line (target of the promotion) |

Both release branches were cut from `develop`. `65-5-Future` currently
contains **8 feature commits** that `65-5-Current` does **not** have.

### Candidate commits on `65-5-Future`

These are the commits available to promote (oldest first). The short SHAs
below are illustrative — always confirm the live SHAs in the **Git** tool
window, because they change if history is rewritten.

| # | Commit (illustrative SHA) | Summary |
| - | ------------------------- | ------- |
| 1 | `31903bd` | `[CHP-00101]` Add TransactionValidator library |
| 2 | `8336c23` | `[CHP-00102]` Add transactions API regression suite |
| 3 | `08b3913` | `[CHP-00103]` Add refunds test-data fixtures (nested JSON) |
| 4 | `61563a9` | `[CHP-00104]` Add refunds endpoint + `transactions_v2` flags to env config |
| 5 | `f68c37d` | `[CHP-00105]` Add transactions suite + refunds settings (YAML) |
| 6 | `8b1f905` | `[CHP-00106]` Extend DataLoader with refund lookups |
| 7 | `a1d8b9e` | `[CHP-00107]` Add transactions dashboard UI regression suite |
| 8 | `e7a92c2` | `[CHP-00108]` Add transaction keyword resource |

You may cherry-pick **all** of them or a **subset** — this guide picks the
whole set, but the mechanics are identical for one commit.

> ⚠️ **Order matters.** Some commits depend on earlier ones (e.g. the
> transactions suite `CHP-00102` uses the validator library from `CHP-00101`;
> the keyword resource `CHP-00108` also uses it). Cherry-pick in the **same
> chronological order** they were committed to avoid avoidable conflicts.

---

## 1. Fetch the latest from the remote

Bring your local repository up to date so you can see all remote branches and
their newest commits.

**PyCharm UI**
1. **Git** menu → **Fetch** (or the ⟳ *Fetch* button at the top-right of the
   **Git** tool window, `Alt+9`).
2. Open the **Git** tool window → **Log** tab. Confirm you can see
   `origin/65-5-Future` and `origin/65-5-Current` with their latest commits.
   Use the **Branch filter** to show *All branches* if they are hidden.

**Command-line equivalent**
```bash
git fetch --all --prune
```

---

## 2. Check out `65-5-Current` and update it

You want your new work to sit on top of the newest `65-5-Current`.

**PyCharm UI**
1. Bottom-right **Git branch widget** (or **Git → Branches**, `Ctrl+Shift+`` `).
2. Under **Remote Branches**, find `origin/65-5-Current` →
   **Checkout** (this creates/updates a local `65-5-Current` tracking branch).
   - If a local `65-5-Current` already exists, select it → **Update** (pull)
     so it matches the remote.

**Command-line equivalent**
```bash
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
```

---

## 3. Create a feature branch from `65-5-Current`

Never cherry-pick directly onto the shared `65-5-Current` branch. Cut a
dedicated feature branch so the promotion can be reviewed via a PR.

**PyCharm UI**
1. **Git branch widget** → **New Branch** (make sure the popup says
   *“Create branch from 65-5-Current”*).
2. Name it, e.g. **`feature/65-5-cherry-pick-transactions`**.
3. Tick **Checkout branch** → **Create**.

**Command-line equivalent**
```bash
# while on 65-5-Current
git checkout -b feature/65-5-cherry-pick-transactions
```

---

## 4. Locate the commits to cherry-pick

**PyCharm UI**
1. Open **Git** tool window → **Log** tab (`Alt+9`).
2. In the branch filter, select **`65-5-Future`** (or *All branches*).
3. You will see the `CHP-00101 … CHP-00108` commits that are on
   `65-5-Future` but not on your feature branch.
4. (Optional) Click each commit to inspect its **Changed files** and diff in
   the right-hand pane before deciding to promote it.

**Command-line equivalent — preview what is unique to Future**
```bash
git log --oneline 65-5-Current..65-5-Future
```

---

## 5. Cherry-pick from the Log

**PyCharm UI**
1. Still in the **Log** tab, with your feature branch checked out
   (the current branch is shown in **bold**).
2. Select the commits to promote:
   - **Single commit:** click it.
   - **Multiple commits:** `Ctrl+Click` individual commits, or `Shift+Click`
     a contiguous range.
3. **Right-click** the selection → **Cherry-Pick**
   (the toolbar also has a 🍒 *Cherry-Pick* button).
4. PyCharm applies the commits **oldest-first** and, by default, commits each
   one onto your feature branch immediately, preserving the original messages.

> **Tip — keep a breadcrumb to the source commit.** If you want each new
> commit message to record the original SHA (`(cherry picked from commit …)`),
> use the command line with `-x` (below), or edit the message when PyCharm
> pauses. This makes later auditing much easier.

**Command-line equivalent**
```bash
# all eight, in order, recording the source SHA in each message
git cherry-pick -x 31903bd 8336c23 08b3913 61563a9 f68c37d 8b1f905 a1d8b9e e7a92c2

# a contiguous range (exclusive lower bound) also works:
# git cherry-pick -x 65-5-Current..65-5-Future
```

---

## 6. Resolve conflicts (only if they occur)

Because the feature branch is cut from `65-5-Current`, which shares the same
base as `65-5-Future`, these particular commits should apply cleanly. If a
conflict does arise (e.g. the same JSON/YAML block was changed on both lines):

**PyCharm UI**
1. A **Conflicts** dialog appears → click **Merge…** for each file.
2. In the 3-pane merge editor, resolve each change:
   **Left = your branch**, **Right = incoming (cherry-picked)**,
   **Centre = result**. Use *Accept Left / Accept Right* or edit the centre
   pane directly.
3. Click **Apply**.
4. In the **Git** tool window, click **Continue Cherry-Pick** to resume with
   the remaining commits.
5. To back out entirely: **Abort Cherry-Pick**.

**Command-line equivalents**
```bash
# after editing the conflicted files and staging them:
git add <resolved-files>
git cherry-pick --continue

# or skip / abort:
git cherry-pick --skip
git cherry-pick --abort
```

---

## 7. Review the promoted changes

**PyCharm UI**
1. **Git** tool window → **Log** tab: confirm the new commits now sit on
   **`feature/65-5-cherry-pick-transactions`**, above the `65-5-Current` tip.
2. Select the range and review the combined diff, or open the **Commit** tool
   window (`Ctrl+K` area) to inspect file-by-file.
3. Optionally run the suites locally before pushing:
   ```bash
   robot --variable ENV:qa --outputdir results tests/
   ```

**Command-line equivalent**
```bash
git log --oneline 65-5-Current..feature/65-5-cherry-pick-transactions
git diff 65-5-Current...feature/65-5-cherry-pick-transactions
```

---

## 8. Commit any follow-up edits (if needed)

Cherry-pick auto-commits, so normally there is nothing extra to commit. If you
amended a message or made a small fix during conflict resolution:

**PyCharm UI**
- **Commit** tool window (`Ctrl+K`) → stage → enter a message → **Commit**.
- To adjust the last message: **Git → Uncommit / Amend**, or right-click the
  commit in the **Log** → **Edit Commit Message** (`F2`) — only safe because
  the branch has not been pushed/shared yet.

**Command-line equivalent**
```bash
git commit --amend        # edit the most recent commit
```

---

## 9. Push the feature branch

**PyCharm UI**
1. **Git → Push** (`Ctrl+Shift+K`).
2. The dialog shows the outgoing commits. The push target should read
   `origin : feature/65-5-cherry-pick-transactions`. Because the branch is new,
   PyCharm sets the upstream automatically.
3. Click **Push**.

**Command-line equivalent**
```bash
git push -u origin feature/65-5-cherry-pick-transactions
```

---

## 10. Create a Pull Request on GitHub

**Target the PR at `65-5-Current`, not `develop` or `main`.**

**Option A — GitHub web UI**
1. GitHub usually shows a **“Compare & pull request”** banner after the push.
2. Otherwise: repo → **Pull requests** → **New pull request**.
3. Set **base = `65-5-Current`**,
   **compare = `feature/65-5-cherry-pick-transactions`**.
4. Title e.g. *“Promote release-65.5 transactions changes to 65-5-Current
   (cherry-pick CHP-00101…CHP-00108)”*. In the description, list the promoted
   `CHP-` tickets and note they were cherry-picked from `65-5-Future`.
5. Add reviewers → **Create pull request**.

**Option B — PyCharm GitHub integration**
1. Ensure GitHub is connected: **Settings → Version Control → GitHub**
   (add your account / token if prompted).
2. Open the **Pull Requests** tool window
   (**Git → GitHub → View Pull Requests**, or the Pull Requests tab in the Git
   tool window).
3. Click **+ (New Pull Request)**, choose
   **base = `65-5-Current`**, fill in title/description → **Create**.

**Command-line equivalent (GitHub CLI)**
```bash
gh pr create \
  --base 65-5-Current \
  --head feature/65-5-cherry-pick-transactions \
  --title "Promote release-65.5 transactions changes to 65-5-Current" \
  --body "Cherry-picked CHP-00101..CHP-00108 from 65-5-Future."
```

---

## 11. Merge the PR into `65-5-Current`

1. Wait for CI checks and reviewer approval on the PR.
2. Choose a merge strategy:
   - **Create a merge commit** — keeps each cherry-picked commit visible.
   - **Squash and merge** — collapses the promotion into one commit on
     `65-5-Current` (tidy history; individual `CHP-` commits are lost).
   - **Rebase and merge** — replays the commits with no merge commit.
   *Recommended:* a **merge commit** (or squash) so the promotion is auditable.
3. Click **Merge pull request** → **Confirm merge**.
4. **Delete the feature branch** when prompted (it has served its purpose).

**Bring the merge back locally (PyCharm)**
1. **Git → Fetch**.
2. Check out `65-5-Current` → **Update** (pull) so your local branch matches
   the merged remote.

**Command-line equivalent**
```bash
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git branch -d feature/65-5-cherry-pick-transactions          # local cleanup
git push origin --delete feature/65-5-cherry-pick-transactions  # if not auto-deleted
```

---

## Quick reference — command-line summary

```bash
# 1. Fetch
git fetch --all --prune

# 2. Update target branch
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current

# 3. Feature branch from 65-5-Current
git checkout -b feature/65-5-cherry-pick-transactions

# 4-5. Cherry-pick (record source SHA with -x)
git cherry-pick -x 31903bd 8336c23 08b3913 61563a9 f68c37d 8b1f905 a1d8b9e e7a92c2
#   conflicts? -> resolve, git add <files>, git cherry-pick --continue
#   give up?   -> git cherry-pick --abort

# 6-7. Review
git log --oneline 65-5-Current..feature/65-5-cherry-pick-transactions

# 8. Push
git push -u origin feature/65-5-cherry-pick-transactions

# 9. PR
gh pr create --base 65-5-Current --head feature/65-5-cherry-pick-transactions \
  --title "Promote release-65.5 transactions changes to 65-5-Current" \
  --body "Cherry-picked CHP-00101..CHP-00108 from 65-5-Future."

# 10. After merge, sync
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
```

---

## Troubleshooting & tips

- **Wrong SHAs?** SHAs in this doc are illustrative. Read the live ones from
  the **Log** tab or `git log --oneline 65-5-Current..65-5-Future`.
- **“Nothing to cherry-pick / already applied.”** The change is already on the
  target branch. Cherry-pick is idempotent for identical content.
- **Empty commit after conflict resolution.** If resolving a conflict makes the
  change a no-op, run `git cherry-pick --skip` (CLI) or *Skip* in PyCharm.
- **Cherry-picking a merge commit** requires a mainline: `git cherry-pick -m 1 <sha>`.
- **Preserve provenance.** The `-x` flag appends
  `(cherry picked from commit <sha>)` to each message — invaluable for audits.
- **Keep the feature branch small.** One promotion = one PR keeps review and
  rollback simple.
