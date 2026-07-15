# Cherry-Pick Guide 2 — Resolving Conflicts (Round 2)

This is the **advanced** companion to
[`CHERRY_PICK_GUIDE.md`](CHERRY_PICK_GUIDE.md). Round 1 cherry-picked cleanly.
**Round 2 is deliberately harder:** `65-5-Current` has received independent
*hotfixes* that touch the **same lines** as the new `65-5-Future` work, so some
commits **will conflict** when cherry-picked. The focus here is **resolving
those conflicts inside PyCharm's merge tool**.

> **Goal:** Promote the 6 round-2 feature commits from `65-5-Future` onto a new
> feature branch cut from `65-5-Current`, resolve the 3 expected conflicts,
> review, push, raise a PR against `65-5-Current`, and merge.

---

## 0. The scenario

Since the round-1 merge, the two branches diverged **on the same files**:

### New work on `65-5-Future` (to be promoted)

| # | Commit (illustrative SHA) | Change | Cherry-pick result |
| - | ------------------------- | ------ | ------------------ |
| 1 | `cd7cf7c` `CHP-00201` | Raise API timeouts/retries + add `rate_limit` (qa.json, dev.json) | ⚠️ **CONFLICT** (qa.json) |
| 2 | `fe46d7b` `CHP-00202` | Add `RetryPolicy` library (new file) | ✅ clean |
| 3 | `0d71ad6` `CHP-00203` | Enable parallel execution (settings.yaml) | ⚠️ **CONFLICT** |
| 4 | `654cc4c` `CHP-00204` | Add retry logic to `ApiClient` (api_client.py) | ⚠️ **CONFLICT** |
| 5 | `7f4e6f4` `CHP-00205` | Add retry test suite (new file) | ✅ clean |
| 6 | `b0a9a36` `CHP-00206` | Register retry suite (test_config.yaml) | ✅ clean |

### Independent hotfixes already on `65-5-Current` (cause the conflicts)

| Commit (illustrative SHA) | Change | Collides with |
| ------------------------- | ------ | ------------- |
| `3be4f7e` `HOTFIX-511` | QA timeout → 60s, retries → 2 (qa.json) | `CHP-00201` |
| `69e4a1f` `HOTFIX-512` | max_workers → 2, timeout → 120s, retry_failed → 0 (settings.yaml) | `CHP-00203` |
| `83c4eb6` `HOTFIX-513` | Add `verify_ssl` + JSON `Accept` header (api_client.py) | `CHP-00204` |

> ⚠️ **SHAs are illustrative** — always read the live ones from the **Log** tab
> or `git log --oneline 65-5-Current..65-5-Future`.

> 🔎 **Heads-up — that range shows *14* commits, not 6.** Round 1 promoted the
> `CHP-001xx` commits by **cherry-pick**, which creates **new SHAs** on
> `65-5-Current`. Git therefore still counts the 8 round-1 originals on
> `65-5-Future` as "missing" from Current, even though their *content* is
> already there. **Ignore those** — for round 2 you cherry-pick **only the 6
> `CHP-002xx` commits** listed above. (If you did accidentally include a
> round-1 commit, Git would report it as *empty / already applied* — harmless,
> but skip it with `git cherry-pick --skip` / *Skip* in PyCharm.)

> 💡 **Note on `CHP-00201`:** it edits *two* files but only **qa.json**
> conflicts — **dev.json** applies cleanly (Current never touched it). Git
> pauses on the whole commit until you resolve qa.json, even though dev.json is
> already staged.

---

## 1–3. Fetch, target branch, feature branch

Same as Guide 1 — condensed here.

**PyCharm UI**
1. **Git → Fetch**.
2. **Git branch widget** → check out **`origin/65-5-Current`** → **Update**.
3. **Git branch widget** → **New Branch from 65-5-Current** →
   name it **`feature/CHP-10002`** → **Checkout**.

**Command-line equivalent**
```bash
git fetch --all --prune
git checkout 65-5-Current
git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10002
```

---

## 4. Start the cherry-pick

**PyCharm UI**
1. **Git** tool window → **Log** tab (`Alt+9`).
2. Filter to **`65-5-Future`**; select the six `CHP-002xx` commits
   (`Shift+Click` the contiguous range).
3. **Right-click → Cherry-Pick**.

PyCharm applies them **oldest-first**. It will apply `CHP-00201`, immediately
hit the qa.json conflict, and **pause with a *Conflicts* dialog**. The clean
commits before/after apply automatically around the pauses.

**Command-line equivalent**
```bash
git cherry-pick -x cd7cf7c fe46d7b 0d71ad6 654cc4c 7f4e6f4 b0a9a36
# ... stops at the first conflict; you resolve, then `git cherry-pick --continue`
```

---

## 5. Resolving each conflict in PyCharm

When the **Conflicts** dialog appears, click **Merge…** on the listed file to
open the **3-pane merge editor**:

```
┌───────────────┬──────────────────┬───────────────┐
│  Left = YOURS │  Result (edit    │ Right = THEIRS │
│  (65-5-Current│   this centre    │ (incoming      │
│   HEAD)       │   pane)          │  CHP-002xx)    │
└───────────────┴──────────────────┴───────────────┘
```

- **Left / “Yours”** = the hotfix already on `65-5-Current`.
- **Right / “Theirs”** = the incoming `65-5-Future` change being cherry-picked.
- Use the **`>>` / `<<` (Accept)** gutter arrows, the **`X` (ignore)**, or just
  **type directly in the centre pane**. The goal is usually to **combine both
  intents**, not blindly pick one side.
- Buttons: **Apply** (save the resolution), **Abort** (cancel the merge).

### Conflict A — `config/environments/qa.json` (CHP-00201)

| Side | timeout_seconds | retries | rate_limit block |
| ---- | --------------- | ------- | ---------------- |
| **Yours** (HOTFIX-511) | `60` | `2` | — |
| **Theirs** (CHP-00201) | `90` | `5` | added |

**Recommended resolution — keep the incident-driven hotfix values, adopt the
new rate_limit block:**
```json
    "version": "v1",
    "timeout_seconds": 60,
    "retries": 2,
    "rate_limit": {
      "requests_per_minute": 600,
      "burst": 50
    },
    "endpoints": {
```
*Rationale:* `60s`/`2` were set deliberately after a CI incident, so they win;
but `rate_limit` is new, non-conflicting intent, so keep it.

### Conflict B — `config/settings.yaml` (CHP-00203)

| Key | Yours (HOTFIX-512) | Theirs (CHP-00203) |
| --- | ------------------ | ------------------ |
| `parallel` | `false` | `true` |
| `max_workers` | `2` | `4` |
| `default_timeout_seconds` | `120` | `90` |
| `retry_failed` | `0` | `2` |
| `fail_fast` | — | `false` (new) |

**Recommended resolution — enable parallelism (their intent) but respect the
CI worker cap and timeout from the hotfix:**
```yaml
execution:
  parallel: true
  max_workers: 2
  default_timeout_seconds: 120
  retry_failed: 2
  fail_fast: false
```
*Rationale:* turning on `parallel` is the feature being promoted; `max_workers:
2` and `120s` are infra limits the hotfix imposed and must stay; `retry_failed:
2` and `fail_fast` are the new behaviour.

### Conflict C — `libraries/api_client.py` (CHP-00204)

This is the trickiest: **Yours** added an SSL-verify toggle + JSON `Accept`
header; **Theirs** added retry logic (a new `_send` wrapper + `max_retries`).
Both changed `__init__`, `get`, and `post`. **Keep both features.**

**Recommended merged result:**
```python
    def __init__(self, base_url: str, timeout_seconds: int = 30,
                 max_retries: int = 3, verify_ssl: bool = True) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._session = requests.Session()
        self._session.headers["Accept"] = "application/json"
        self._token: Optional[str] = None

    # ... set_auth_token / _url unchanged ...

    def _send(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send a request, retrying on transient 5xx/429 responses."""
        last: Optional[requests.Response] = None
        for attempt in range(1, self.max_retries + 1):
            last = self._session.request(
                method, self._url(path), timeout=self.timeout,
                verify=self.verify_ssl, **kwargs
            )
            if last.status_code not in (429, 500, 502, 503, 504):
                return last
        return last

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._send("GET", path, params=params)

    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._send("POST", path, json=payload)
```
*Rationale:* the retry `_send` wrapper is the promoted feature; `verify_ssl` and
the `Accept` header from the hotfix are folded in — note `verify=self.verify_ssl`
is threaded through `_send` so both survive.

---

## 6. Apply, then continue the sequence

For **each** conflict:

**PyCharm UI**
1. Edit the centre pane to the merged result → **Apply**.
2. Back in the **Git** tool window, click **Continue Cherry-Pick** to move to
   the next commit. PyCharm re-uses the original commit message.
3. If things go wrong: **Abort Cherry-Pick** rolls the whole sequence back.

**Command-line equivalent (per conflict)**
```bash
# after editing the file to the merged result:
git add config/environments/qa.json      # (or settings.yaml / api_client.py)
git cherry-pick --continue

# escape hatches:
git cherry-pick --skip     # drop just this commit
git cherry-pick --abort    # roll back the entire cherry-pick sequence
```

Repeat until all six commits are applied. Expect to resolve **3 conflicts**
(qa.json, settings.yaml, api_client.py); the other three commits apply silently.

---

## 7. Review

**PyCharm UI** — **Git → Log**: confirm 6 new commits sit on
`feature/CHP-10002` above the `65-5-Current` tip. Open each conflicted file's
diff and re-read your merged result.

**Command-line**
```bash
git log --oneline 65-5-Current..feature/CHP-10002        # expect 6 commits
git diff 65-5-Current...feature/CHP-10002                # review the net change
python -c "import ast; ast.parse(open('libraries/api_client.py').read())"  # sanity: valid Python
```

> ✅ **Sanity check after conflict resolution:** unlike round 1, the branches
> will **not** be identical to `65-5-Future` — that's expected and correct,
> because you intentionally kept some hotfix values (e.g. `timeout_seconds: 60`,
> `max_workers: 2`). Verify the *merged intent*, not byte-equality.

---

## 8. Push

**PyCharm UI** — **Git → Push** (`Ctrl+Shift+K`) → **Push**.

**Command-line**
```bash
git push -u origin feature/CHP-10002
```

---

## 9. Create the PR (base = `65-5-Current`)

**PyCharm UI** — **Git → GitHub → Create Pull Request** →
base **`65-5-Current`**, compare **`feature/CHP-10002`**.

**GitHub CLI**
```bash
gh pr create --base 65-5-Current --head feature/CHP-10002 \
  --title "Promote round-2 retry/config changes to 65-5-Current" \
  --body "Cherry-picked CHP-00201..CHP-00206 from 65-5-Future. Resolved 3 conflicts (qa.json, settings.yaml, api_client.py) by combining hotfix + feature intent."
```

In the PR description, **call out the conflict resolutions** so reviewers know
which hotfix values you deliberately preserved.

---

## 10. Merge into `65-5-Current`, then sync & clean up

1. After review/CI, **Merge pull request** (a merge commit keeps the promotion
   auditable; squash also fine).
2. **Delete** `feature/CHP-10002` on merge.
3. Locally: **Git → Fetch**, check out `65-5-Current`, **Update**.

**Command-line**
```bash
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10002
git push origin --delete feature/CHP-10002   # if not auto-deleted
```

---

## Quick reference

```bash
git fetch --all --prune
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git checkout -b feature/CHP-10002

git cherry-pick -x cd7cf7c fe46d7b 0d71ad6 654cc4c 7f4e6f4 b0a9a36
#   conflict on qa.json      -> merge -> git add config/environments/qa.json   -> git cherry-pick --continue
#   conflict on settings.yaml-> merge -> git add config/settings.yaml          -> git cherry-pick --continue
#   conflict on api_client.py-> merge -> git add libraries/api_client.py       -> git cherry-pick --continue

git log --oneline 65-5-Current..feature/CHP-10002   # 6 commits
git push -u origin feature/CHP-10002
gh pr create --base 65-5-Current --head feature/CHP-10002 --title "..." --body "..."
# merge PR, then:
git checkout 65-5-Current && git pull --ff-only origin 65-5-Current
git branch -d feature/CHP-10002
```

---

## Conflict-resolution tips

- **Left = Yours (target/HEAD), Right = Theirs (incoming).** In *cherry-pick*
  (and *rebase*) this can feel reversed vs a normal merge — read the pane
  headers, don't assume.
- **Combine, don't just pick a side.** A conflict means two intentional
  changes overlapped; the right answer is usually to preserve *both* intents,
  as in Conflict C above.
- **Resolve one commit fully before continuing.** Cherry-pick is sequential —
  finish qa.json before `--continue` moves you to the next commit.
- **`--abort` is safe** and non-destructive: it returns you to the pre-cherry-pick
  state on your feature branch. Use it if a resolution goes sideways.
- **Empty result?** If your resolution makes a commit a no-op, use
  `git cherry-pick --skip` (or *Skip* in PyCharm).
- **Validate code after merging conflicts** — a syntactically broken merge in a
  `.py`/`.json`/`.yaml` file is easy to introduce; run a quick parse/lint before
  you push.
- **Record provenance** with `-x` so each promoted commit notes
  `(cherry picked from commit <sha>)` for later audits.
