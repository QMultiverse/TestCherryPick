# Cherry-Pick Guide 3 — Selective Promotion (Round 3)

Third exercise in the series (see
[`CHERRY_PICK_GUIDE.md`](CHERRY_PICK_GUIDE.md) and
[`CHERRY_PICK_GUIDE_2.md`](CHERRY_PICK_GUIDE_2.md)).

**New skills this round:**
1. **Selective cherry-picking** — `65-5-Future` contains a **WIP commit you must
   NOT promote**. You will pick a *subset*, skipping it.
2. **One deliberate conflict** — a Slack-config change collides with a hotfix
   already on `65-5-Current`.

> **Goal:** Promote the notifications feature (5 of 6 commits) from
> `65-5-Future` onto a feature branch cut from `65-5-Current`, **skip the WIP
> commit**, resolve the single conflict, review, PR, and merge.

---

## 0. The scenario

### New work on `65-5-Future`

| # | Commit (illustrative SHA) | Change | Promote? | Cherry-pick |
| - | ------------------------- | ------ | -------- | ----------- |
| 1 | `20fb62e` `CHP-00301` | Add notifications (email/webhook) config to dev + qa | ✅ yes | clean |
| 2 | `30fa23c` `CHP-00302` | Add `NotificationService` library | ✅ yes | clean |
| 3 | `8d7a72e` `CHP-00303` | Add notification templates/recipients test data | ✅ yes | clean |
| 4 | `519e4d5` `CHP-00304` | Enable Slack notifications on failure/flaky (settings.yaml) | ✅ yes | ⚠️ **CONFLICT** |
| 5 | `b974ac1` `CHP-00305` | **[WIP] Experimental SMS spike** | 🚫 **NO — SKIP** | (do not select) |
| 6 | `3560ae0` `CHP-00306` | Add notifications API test suite | ✅ yes | clean |

> 🚫 **Why skip `CHP-00305`?** It is an unfinished proof-of-concept
> (`libraries/sms_spike.py`) — no tests, hard-coded provider, not wired in, and
> its own message says *DO NOT PROMOTE*. Shipping it to the current release line
> would introduce dead, untested code. This is the whole point of *selective*
> cherry-picking: promote finished work, leave WIP behind.

### Hotfix already on `65-5-Current` (causes the conflict)

| Commit (illustrative SHA) | Change | Collides with |
| ------------------------- | ------ | ------------- |
| `2d17540` `HOTFIX-521` | Route Slack to `#release-65-5-alerts` for the release window | `CHP-00304` |

> ⚠️ **SHAs are illustrative** — read live ones from the **Log** tab or
> `git log --oneline 65-5-Current..65-5-Future`. (As in round 2, that range also
> lists older already-promoted commits with *new* SHAs — ignore those; promote
> only the `CHP-003xx` commits above, minus the WIP one.)

---

## 1–3. Fetch, target branch, feature branch

**PyCharm UI**
1. **Git → Fetch**.
2. **Git branch widget** → check out **`origin/65-5-Current`** → **Update**.
3. **Git branch widget** → **New Branch from 65-5-Current** →
   name it **`feature/CHP-10003`** → **Checkout**.

**Command-line**
```bash
git fetch --all --prune
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10003
```

---

## 4. Cherry-pick a SUBSET (skip the WIP commit)

**PyCharm UI**
1. **Git** tool window → **Log** tab (`Alt+9`); filter to **`65-5-Future`**.
2. Select **only the five commits to promote**. The WIP `CHP-00305` sits in the
   middle of the range, so **do NOT `Shift`-select the whole block** — instead
   **`Ctrl+Click`** each of `CHP-00301`, `CHP-00302`, `CHP-00303`, `CHP-00304`,
   `CHP-00306`, leaving `CHP-00305` unselected.
3. **Right-click → Cherry-Pick**. PyCharm applies them oldest-first and pauses
   on the `CHP-00304` conflict.

**Command-line** — list the 5 SHAs explicitly (note: **no `CHP-00305`**):
```bash
git cherry-pick -x 20fb62e 30fa23c 8d7a72e 519e4d5 3560ae0
#                 301     302     303     304⚠    306
```

> 💡 **Tip:** because you are naming exact commits, there is zero risk of the
> WIP commit sneaking in — the range form `A..B` would have included it.

---

## 5. Resolve the one conflict — `config/settings.yaml` (CHP-00304)

PyCharm shows the **Conflicts** dialog → **Merge…** to open the 3-pane editor
(**Left = Yours / 65-5-Current**, **Right = Theirs / incoming CHP-00304**).

| | `enabled` | `channel` | `notify_on` |
| - | --------- | --------- | ----------- |
| **Yours** (HOTFIX-521) | `true` | `#release-65-5-alerts` | — |
| **Theirs** (CHP-00304) | `true` | `#qa-notifications` | `failure`, `flaky` |

**Recommended resolution — keep the release channel, adopt the new triggers:**
```yaml
  slack:
    enabled: true
    channel: "#release-65-5-alerts"
    notify_on:
      - failure
      - flaky
```
*Rationale:* the `#release-65-5-alerts` routing was set deliberately for the
release window (hotfix intent wins), while `notify_on` is the new, non-competing
behaviour the feature adds — keep both.

Then **Apply** → in the Git tool window **Continue Cherry-Pick** to finish the
remaining commit.

**Command-line**
```bash
# after editing settings.yaml to the merged result:
git add config/settings.yaml
git cherry-pick --continue
#   escape hatches: git cherry-pick --skip   |   git cherry-pick --abort
```

---

## 6. Review

**PyCharm UI** — **Git → Log**: confirm **5** new commits on
`feature/CHP-10003`, and that **`sms_spike.py` is NOT present**.

**Command-line**
```bash
git log --oneline 65-5-Current..feature/CHP-10003            # expect 5 commits
test -f libraries/sms_spike.py && echo "OOPS: WIP got promoted" || echo "OK: WIP correctly skipped"
python -c "import yaml,sys; yaml.safe_load(open('config/settings.yaml')); print('settings.yaml valid')"
```

---

## 7–9. Push, PR, merge

**PyCharm UI**
1. **Git → Push** (`Ctrl+Shift+K`).
2. **Git → GitHub → Create Pull Request** → base **`65-5-Current`**,
   compare **`feature/CHP-10003`**.
3. After review/CI → **Merge pull request** → **delete** the feature branch.
4. **Fetch**, check out `65-5-Current`, **Update**.

**Command-line**
```bash
git push -u origin feature/CHP-10003
gh pr create --base 65-5-Current --head feature/CHP-10003 \
  --title "Promote notifications feature to 65-5-Current" \
  --body "Cherry-picked CHP-00301..304,306 from 65-5-Future (skipped WIP CHP-00305). Resolved 1 conflict in settings.yaml (kept release channel + new notify_on triggers)."

# after merge:
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10003
git push origin --delete feature/CHP-10003   # if not auto-deleted
```

---

## Quick reference

```bash
git fetch --all --prune
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10003

# 5 commits, WIP CHP-00305 intentionally omitted:
git cherry-pick -x 20fb62e 30fa23c 8d7a72e 519e4d5 3560ae0
#   conflict on settings.yaml -> merge -> git add config/settings.yaml -> git cherry-pick --continue

git log --oneline 65-5-Current..feature/CHP-10003   # 5 commits, no sms_spike.py
git push -u origin feature/CHP-10003
gh pr create --base 65-5-Current --head feature/CHP-10003 --title "..." --body "..."
# merge PR, then sync + delete branch
```

---

## What to double-check this round

- **Did the WIP stay behind?** `libraries/sms_spike.py` must **not** exist on
  your feature branch. If it does, you accidentally included `CHP-00305` — undo
  with an interactive rebase drop, or `git rebase --onto` to remove it, or just
  redo the cherry-pick with the correct selection.
- **Conflict combined, not clobbered** — the merged `slack:` block should keep
  the release channel *and* the new `notify_on` list.
- **Result is not identical to `65-5-Future`** — expected: you skipped a commit
  and kept a hotfix value. Verify *intent*, not byte-equality.
- **Provenance** — `-x` records `(cherry picked from commit <sha>)` on each
  promoted commit.
