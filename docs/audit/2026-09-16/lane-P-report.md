# Lane P (Plugin lifecycle) - production-readiness review

Repo: /Users/matthew/parallax-private/Projects/itworks @ 0b972ac. Read-only. No repo file was created, edited or deleted.

Counts: 2 CRITICAL, 12 IMPORTANT, 7 ADVISORY.

---

## 1. Suspicions

### CRITICAL

#### C1 — The gates are known to fail on the model most users will run, and nothing in the plugin says so at runtime
**Where:** README.md:112 (only place it is stated).
**Exact text:** "In adversarial pressure testing (`tests/pressure/`, 2026-09-11, blind judged), Opus passed the closeout case in three of three runs; Sonnet failed it in every run across three wordings, not by capitulating but by never running the sweep, so the planted critical findings were never found, and in one run it handed over the deploy commands while claiming to withhold them. ... Don't trust the gates to anything below Opus class."
**User behavior that triggers it:** a novice installs the plugin, never reads the README past "Install", runs Claude Code on its default model, builds an app, says "ok ship it".
**Wrong outcome:** by the owner's own blind-judged evidence, the closeout sweep does not run, the planted CRITICALs (secret in client code, no backup) are never found, and in one of three runs the model handed over deploy commands while claiming to withhold them. The novice ships with the leak. Nothing in `skills/project-closeout/SKILL.md` or `hooks/session-start.sh` mentions model class; the session-rule block asserts the opposite ("These fire automatically; urgency, expertise claims, or excitement never skip them").
**Severity:** CRITICAL. This is exactly "a novice following the text as written can ship with a leaked secret", and the repo already contains the reproduction.
**Reproduce:** read README.md:112 against `hooks/session-start.sh` (the `.itworks` branch prints no model caveat) and against `skills/project-closeout/SKILL.md` (no mention of model class anywhere). Re-run `tests/pressure/harness/run-case.sh` for the closeout case on Sonnet.
**Cheapest fix:** the session-start hook and the closeout skill state the model requirement in one line, and closeout refuses to begin (or states loudly that it cannot be trusted) when the running model is below Opus class; plus a README install-section warning, not a footnote.

#### C2 — A green itworks.dev badge is emitted while a CRITICAL is knowingly open, because "accepted" is counted as "not open"
**Where:** references/publish.md:20, :28, :59; README.md:100.
**Exact text:** publish.md:28 `grep -cE '^- \[ \] CRITICAL \|' .itworks/REVIEWS.md          # critical_open`; publish.md:59 "badge colors: green when the audit is under 30 days old and no critical is open"; README.md:100 "each with a badge showing its audit date and whether a critical finding is still open".
**User behavior:** the reckoning surfaces `CRITICAL | security-auth | API key in client code`. The user says the sanctioned acceptance words. Per state-format.md:133 the line is rewritten as `- [x] CRITICAL | security-auth | ... | Accepted <date>: see Accepted risks`. The `critical_open` grep matches only `- [ ] CRITICAL` and returns 0. The user then opts in to publish.
**Wrong outcome:** itworks.dev shows a GREEN badge, and `critical_open: 0`, for a project whose owner deliberately shipped a live exposed key. The badge's whole purpose is telling third parties the opposite. The payload carries no `accepted_critical` field at all, so the wall cannot represent the case even if the site wanted to.
**Severity:** CRITICAL — the plugin's public-facing claim is falsified by its own recorded state, and third parties act on it.
**Reproduce:** write a two-line REVIEWS.md containing one `- [x] CRITICAL | security-auth | key in client code | Accepted 2026-09-16: see Accepted risks` line and run the four greps at publish.md:25-28. `found`=1, `accepted`=1, `critical_open`=0.
**Cheapest fix:** add `critical_accepted` to the payload and make amber/red cover it; publish.md:59 badge rule keys on `critical_open + critical_accepted`.

### IMPORTANT

#### I1 — `references/...` does not resolve from the skill's base directory, in all five skills
**Where:** skills/project-kickoff/SKILL.md:22, :64, :86, :89; skills/project-checkpoint/SKILL.md:38, :42, :52, :85; skills/project-closeout/SKILL.md:18, :26, :82; skills/project-audit/SKILL.md:44, :54, :79; skills/project-resume/SKILL.md:14, :21, :59.
**Exact text (kickoff:22):** "write it to `.itworks/PROFILE.md` per `references/state-format.md` (read that file now if you have not)".
**The break:** the loader tells the agent "Base directory for this skill: `<plugin>/skills/project-kickoff`". `ls skills/project-kickoff/` returns `SKILL.md` and nothing else — there is no `references/` under any skill directory. The real file is `<plugin>/references/state-format.md`, one level ABOVE the base directory. Only one place in the repo disambiguates a plugin-root path, and it is a different file: resume:14 "(the script lives in this plugin's `scripts/` directory, next to `skills/`)".
**Wrong outcome:** an agent that resolves the path literally against its base directory gets "no such file" on the state format contract, the lens runbooks, the publish field list and the audit method. The likely behaviours are (a) improvising the state file shapes, (b) improvising the lens checks — which is precisely the "I checked" without a command that invariant 1 forbids. Agents that glob for it will recover; that it depends on model initiative is the finding.
**Also affected:** kickoff:89 "follow `skills/project-checkpoint` behavior" is likewise plugin-root relative and resolves to `skills/project-kickoff/skills/project-checkpoint` from the base directory.
**Severity:** IMPORTANT (a broken reference an agent needs; every skill).
**Reproduce:** `ls /Users/matthew/parallax-private/Projects/itworks/skills/project-kickoff/` → `SKILL.md`. `test -e skills/project-kickoff/references/state-format.md` → false.
**Cheapest fix:** write every pointer as `${CLAUDE_PLUGIN_ROOT}/references/<file>`, or add one line to each skill: "`references/` means `<plugin root>/references/`, one level above this skill's base directory."

#### I2 — The hook tells the agent that two "not now"s turn OFF any skill, including closeout, which has no such opt-out
**Where:** hooks/session-start.sh, `.itworks` branch, final clause (verified by running it, output below); skills/project-closeout/SKILL.md:120-122.
**Exact hook text:** "...and \"not now\" twice per skill turns that skill off for the project."
**Exact closeout text:** "## \"Not now\"\n\nCloseout invoked by mistake (\"ship it\" was hyperbole): confirm in one line and stand down for the session. But once the user genuinely wants deployment steps, the sweep runs first; that order is the skill."
**User behavior:** "ship it" → "not now". Later: "ship it" → "not now, I'll do it myself". Third turn: "ok how do I put this on Vercel?" The agent that trusts the injected session rule has by now written `project-closeout` into `opted_out` in PROFILE.md, and nothing in the closeout skill tells it to ignore `opted_out` (checkpoint:22 explicitly reads `opted_out`, closeout never mentions it).
**Wrong outcome:** deploy steps with no sweep, no secret scan, no history audit, no backup check — the exact promise of invariant 1, broken by a phrase the hook itself authorises.
**Severity:** IMPORTANT, bordering CRITICAL: it is the single wording that lets a novice reach a public deploy with none of the five checks having run.
**Reproduce:** the two quoted passages, plus the hook output in Coverage below.
**Cheapest fix:** the hook says "'not now' twice per skill turns that skill off for the project, except project-closeout, which always runs before deployment steps," and closeout states the same in its own "Not now" section.

#### I3 — The hook and README tell the agent to leave existing un-instrumented projects alone, contradicting kickoff's own trigger and adoption mode
**Where:** hooks/session-start.sh non-`.itworks` branch; README.md:64; skills/project-kickoff/SKILL.md:3 and :84-91.
**Exact hook text:** "Existing projects without .itworks/ are left alone unless the user runs a /itworks command."
**Exact kickoff frontmatter:** "Use when the user asks to build a new app, site, tool, bot, or script and no .itworks directory exists yet, **or before writing the first code in any project without one**."
**User behavior:** the target user — a vibe coder with a half-finished app from last week — opens Claude Code in that directory and says "add login to this". The hook says leave it alone; kickoff's description says fire; kickoff's Adoption mode (:84-91) exists precisely for this case, including "run the tracked-secrets check from `references/lens-security-auth.md`" and a baseline checkpoint over all lenses.
**Wrong outcome:** the adoption baseline — the only moment the plugin scans an already-vibe-coded repo for committed secrets — never fires for the user most likely to already have a committed secret. Outcome left to which instruction the model weights higher.
**Severity:** IMPORTANT (contradiction that leaves a secret scan to chance).
**Reproduce:** the three quoted passages; the hook output for the no-`.itworks` case in Coverage.

#### I4 — Checkpoint Step 3's list of readable lens files omits `lens-llm-security.md`, which Step 2 can select
**Where:** skills/project-checkpoint/SKILL.md:42 vs :33.
**Exact text (:42):** "Read ONLY the selected lens files from `references/` (`lens-security-auth.md`, `lens-real-data.md`, `lens-testing.md`, `lens-production-readiness.md`)." (:33): "Wired an AI or LLM feature (chat, generation, agents, embeddings) → `llm-security`".
**User behavior:** "I added the chatbot, it works!" Step 2 selects `llm-security`; Step 3 says read ONLY from a list that does not contain it.
**Wrong outcome:** the prompt-injection, secrets-in-prompt and unlimited-public-spend checks (lens-llm-security.md steps 2, 3, 5 — all CRITICAL-rated) are the ones most likely to be skipped, in the app type the plugin says its users disproportionately build (lens-llm-security.md:3). "Read ONLY" makes the omission read as a prohibition, not an oversight.
**Severity:** IMPORTANT.
**Reproduce:** the two quoted lines.

#### I5 — Adoption mode never runs Step 4, so an adopted project gets no .gitignore/.env rule, no pinning, no spend cap and no test harness
**Where:** skills/project-kickoff/SKILL.md:84-91 (adoption) vs :56-66 (Step 4).
**Exact text (:88):** "Write the remaining four state files, reverse-engineered from code plus answers, then play the summary back and get confirmation exactly as in Step 5." Step 4 is named nowhere in the adoption sequence.
**Wrong outcome:** the adopted project never gets the "`.env` in `.gitignore` before any key exists to leak" rule (:62), git init and the first restore point (:63), exact pins with a committed lockfile (:64), the spend cap and rate limit when paid services are in play (:65), or the harness with one deliberately failing test proved to go red (:66). The baseline checkpoint (:89) catches a secret already tracked, but it is a review, not a structure; nothing establishes env handling going forward. Invariant 6's second half ("kickoff sets up .gitignore and env handling before the first secret is needed") is simply not true in adoption mode.
**Severity:** IMPORTANT.
**Reproduce:** walk the adoption numbered list; Step 4 is absent.

#### I6 — Closeout never restates checkpoint's "not verified live" rule, so the auth door check can be satisfied without running
**Where:** skills/project-checkpoint/SKILL.md:45 vs skills/project-closeout/SKILL.md:16-22; references/lens-security-auth.md:39-45.
**Exact text (checkpoint:45):** "A live probe that cannot run right now (no server up, no route built yet) is not skipped and not guessed green: assign severity from what the code shows, and put \"not verified live:\" plus the exact command into the evidence-to-close field. The finding closes only when that command has actually run clean."
**The gap:** closeout Step 1 says only "Read and run EVERY `lens-*.md` runbook". It does not carry the edge rule, and the Step 4 Ship checklist (:50-56) requires a verified backup restore and a rehearsed rollback but says nothing about the auth probe having actually returned 401/403.
**User behavior:** the novice's server is not running at closeout (common — they ran it in a terminal they closed). lens-security-auth step 4's curl cannot run.
**Wrong outcome:** the auth check is recorded from a code read, severity assigned by judgement, and SHIPPED.md can be written without `curl` ever having proved a protected route returns 401. Invariant 1 asks for the auth check to have ACTUALLY run; it has not.
**Severity:** IMPORTANT.
**Cheapest fix:** add "protected routes probed live, 401/403 shown" to the Step 4 ship checklist, and restate the not-verified-live rule in closeout Step 1.

#### I7 — "dependency-vetting if any dependency was never vetted" is unanswerable: no state file records what was vetted
**Where:** skills/project-closeout/SKILL.md:18.
**Exact text:** "plus `dependency-vetting.md` if any dependency was never vetted".
**The gap:** references/state-format.md defines PROFILE.md's fields (:142-165) and REVIEWS.md's finding grammar (:113-140). Neither carries a vetted-package list or date. The only trace a vetting leaves is a finding line, and a clean vetting produces no finding at all.
**Wrong outcome:** at closeout the agent has no way to answer the condition, and the cheapest reading ("checkpoints have been vetting as we go") skips the runbook. A typosquatted or nonexistent package added in a session where no checkpoint fired (cadence guard, or `project-checkpoint` in `opted_out`) is never looked up — and dependency-vetting.md:33 rates that CRITICAL.
**Severity:** IMPORTANT.
**Cheapest fix:** make closeout run dependency-vetting over the full manifest unconditionally, or add a `vetted_deps:` line to PROFILE.md.

#### I8 — The publish curl cannot detect a 429/503 and can hang the session
**Where:** skills/project-closeout/SKILL.md:89, :92, :96.
**Exact text:** "`curl -sS -X POST https://itworks.dev/api/entries -H \"Content-Type: application/json\" --data @<payload file>`" then "Show the user the returned entry id, badge URL, and entry URL" and "A failed request is reported in one line and never retried automatically."
**The break:** `-sS` without `-f` or `-w '%{http_code}'` exits 0 on a 429 or 503 and prints the error body (often HTML from a CDN). There is no `--max-time`, so a hung TCP connection blocks the turn indefinitely. The skill then instructs the agent to "show the returned entry id" — with no id in the response, the failure mode is a model inventing or mis-parsing one, right after it just told the user their entry is live.
**Wrong outcome:** at best a confusing error dump at the emotional high point of the project; at worst a fabricated entry id and badge URL the user pastes into their README.
**Severity:** IMPORTANT.
**Cheapest fix:** `curl -sS --max-time 20 -w '\n%{http_code}\n' ...` and an explicit branch: non-2xx or empty body → one line "itworks.dev did not accept it (<code>); nothing was published", no id shown.

#### I9 — publish.md's "not sent" list contradicts what the `summary` field is
**Where:** references/publish.md:12 and :50; README.md:102; references/state-format.md:16-17.
**Exact text:** publish.md:12 "summary | one line | first sentence of the \"What it is\" section body in `.itworks/PROJECT.md`"; publish.md:50 (Not sent) "- the user's own words"; state-format.md:17 defines that section body as "<one or two sentences **in the user's own words**, then one sentence in precise terms>".
**Wrong outcome:** the field sent to a public wall is, by the state contract, the user's own sentence — the exact thing the privacy list promises never leaves the project. A user who reads the Not-sent list and approves on that basis has been told something false, and the user's own first sentence is where an internal client name or an embarrassing framing lives.
**Severity:** IMPORTANT (false claim in the document the user is pointed at to decide).
**Reproduce:** the three quoted lines.
**Cheapest fix:** either take `summary` from the "one sentence in precise terms" clause, or drop "the user's own words" from Not sent and say "your accepted-risk wording and your review notes are never sent; the one-line summary is your own description, shown to you before sending."

#### I10 — The resume rebuild path can silently downgrade an open CRITICAL to ADVISORY
**Where:** skills/project-resume/SKILL.md:57.
**Exact text:** "A guessed severity is written as the bare token `ADVISORY` with \"severity best-guess, pending re-review\" appended inside the description text."
**User behavior:** the user opens REVIEWS.md in a editor and mangles a line (the file is explicitly "theirs to touch", :54). The mangled line was the open `CRITICAL | security-auth | API key in client code`. Rebuild carries the words verbatim but the severity is not legible.
**Wrong outcome:** the finding is rewritten as ADVISORY. Consequences chain: checkpoint no longer blocks new feature work on it; closeout's HARD-GATE no longer holds; state-format.md:177 validation rule 5 (SHIPPED.md must not coexist with an unchecked CRITICAL) now passes; and publish.md's `critical_open` grep returns 0, so the public badge goes green. The rebuild's single confirmation question (:58) is about the code summary, not about downgraded findings, so the user is never asked.
**Severity:** IMPORTANT (a silent path from an open CRITICAL to a green public badge).
**Cheapest fix:** guessed severities default to CRITICAL pending re-review, or the rebuild's confirmation question must list every line whose severity could not be read.

#### I11 — The closeout HARD-GATE gates deployment steps on the sweep completing, not on the reckoning resolving
**Where:** skills/project-closeout/SKILL.md:12-14.
**Exact text:** "SHIPPED.md is not written while a CRITICAL is open and unacknowledged. Explicit, logged acknowledgment is the only escape hatch. **No deployment steps before the sweep completes.**"
**The break:** read literally, once Step 1's sweep has completed the second sentence is satisfied and deployment steps are permitted, while the reckoning (Step 3) is still walking open CRITICALs. Only SHIPPED.md is bound to the CRITICAL state. The prose at :46 does hold the line ("A refusal never includes the deploy commands themselves"), but it sits 34 lines below the gate and is framed as the stalemate rule, not the gate. An agent under pressure quotes the gate.
**Severity:** IMPORTANT (a gate skippable by wording; the README:66 summary repeats the same shape: "The one hard stop: the final ship document is not written...").
**Cheapest fix:** "No deployment steps until the sweep has completed AND every CRITICAL is fixed or individually acknowledged in writing."

#### I12 — The backup, spend-cap and role checks are all gated on PROJECT.md fields a novice filled in, with no correction path
**Where:** references/lens-production-readiness.md:21 ("only if PROJECT.md says data is real"), :42 ("only if the app calls paid services per PROJECT.md"); references/lens-security-auth.md:47 ("only if PROJECT.md says roles exist"); skills/project-checkpoint/SKILL.md:46.
**Exact text (checkpoint:46):** "Runbook steps gated by their own \"only if\" are skipped when the condition is absent. But if PROJECT.md REQUIRES the missing thing (auth needed: yes and no auth code exists), the absence itself is a finding, not a skip."
**The gap:** that edge rule covers only the direction PROJECT.md-says-yes-code-says-no. The dangerous direction is the reverse: PROJECT.md says "Real data: none / sample only" because at kickoff the novice answered question 4 honestly about a prototype, and three weeks later the app holds their friends' email addresses and photos. Nothing re-asks question 4, and no lens says "check whether the Data line is still true against the database". lens-production-readiness step 3 then never fires, so "no backup for real user data is CRITICAL at closeout" never triggers. Same shape for paid services (the surprise-bill CRITICAL) and roles.
**Wrong outcome:** ships with real user data and no backup, with every runbook having correctly recorded "not applicable".
**Severity:** IMPORTANT (invariant 1: the backup check never actually runs).
**Cheapest fix:** one line in the closeout Step 4 checklist: "re-confirm PROJECT.md's Data and Where it will live lines against the actual store and the actual providers before trusting any 'only if' skip."

### ADVISORY

- **A1 — Confirmation standard is stated two ways.** kickoff:13 "until PROJECT.md exists and the user confirms the summary **in their own words**" vs kickoff:70 "Proceed only on **explicit confirmation**". A novice's "yep sounds good" satisfies one and not the other; the agent decides. Pick one.
- **A2 — hooks.json declares no `timeout`.** hooks/hooks.json:1-14 relies on the Claude Code default. The script is instantaneous, so this is hygiene, but an explicit `"timeout": 10` documents the intent.
- **A3 — The publish payload file has no specified location.** closeout:82 "write it to a payload file" — unqualified, so it can land in the project root and be swept into the ship commit. Say `.itworks/` or a temp path, and say it is deleted after.
- **A4 — publish.md:35 cites "The example from itworks `docs/SPEC.md`"**; no `docs/` directory exists in the repo at 0b972ac. Dangling pointer in a file an agent is told to build a payload from.
- **A5 — Missing glossary card.** lens-real-data.md:63 names "dev vs production data" among its guided cards; `grep -x '## dev vs production data' references/glossary.md` finds nothing (the nearest is `## staging vs production`). In guided profile the agent is told to show a card that does not exist. Same shape, milder: dependency-vetting.md:43 names "dependency (package)", the card is `## dependency`.
- **A6 — The one-card-per-message cap is scoped to the interview only.** kickoff:52 "at most one card per message **during the interview**, so questions stay questions". Step 4's structure proposal is one message that can introduce frontend/backend split, persistence, environment variables, .gitignore, lockfile, version pinning, rate limit, spend cap and test harness — nine terms, no cap, to a guided user. This is the wall the skill elsewhere forbids.
- **A7 — The hook injects the plugin.json version string verbatim into the prompt** (hooks/session-start.sh, the `parsed=` sed). Not a project-content injection surface — `plugin_root` derives from `BASH_SOURCE`, never from `CLAUDE_PROJECT_DIR` — but a forked/tampered plugin.json `"version"` value becomes unquoted prompt text. Installing a plugin is already full trust, so this is noted for completeness, not as a defect.

### Explicitly checked and found clean

- **Invariant 6 (pasting secrets):** grep across `skills/` and `references/` for paste/enter-your-key wording found no place any skill asks the user for a secret, token, password or production credential. lens-production-readiness.md:44 asks whether a spend cap exists, never for the credential. The only "paste" instructions are for pasting *command output*. Clean.
- **Publish opt-in and ordering:** closeout:81 "Runs only after `SHIPPED.md` is written"; :84 "Ask exactly once, in these words ... Anything other than a clear yes means no: nothing is sent, and the question is never repeated in this session"; :82 the exact JSON is shown before asking; :96 "never a gate and never blocks the ship". Publish cannot fire before SHIPPED.md. Clean except I8/I9 above.
- **Expert profile skipping a gate:** state-format.md:152 "The profile changes wording ONLY. Checks and gates never vary by profile", kickoff:99, checkpoint:98, README:116 all agree. No path found where `expert` removes a check.
- **Hook injection surface:** the script `eval`s nothing, sources nothing, and prints no project file content. It reads only `$dir/.itworks` (existence test), `$dir/.itworks-off` (existence test) and the plugin's own plugin.json. A hostile repo cannot inject prompt text through it.
- **Packaging:** plugin.json, marketplace.json and hooks.json all parse (`python3 -m json.tool`). plugin.json version `1.0.0` matches CHANGELOG.md's `## 1.0.0 - 2026-09-12` and the tag at 0b972ac. `SessionStart` is a valid Claude Code hook event; omitting `matcher` correctly means all start types. Command frontmatter carries only `description`, valid. The README install pair (`marketplace add parallaxintelligencepartnership/itworks` then `install itworks@itworks`) matches marketplace.json's `"name": "itworks"` and its plugin entry `"name": "itworks", "source": "./"`. `bash -n hooks/session-start.sh` clean.
- **Lens cap consistency:** checkpoint:36 caps at 2 and names exactly two sanctioned exceptions (kickoff adoption baseline, closeout sweep); kickoff:89 and closeout:18 are those two exceptions and describe themselves as such; audit-method.md:9-11 restates the same three tiers. No contradiction.
- **Tier triggers:** the phrase-to-tier table in audit:22-26, README:19-23 and the hook's rule (4) agree. Checkpoint:18 hands off the audit phrases rather than absorbing them. No skill claims checkpoint or closeout reads application logic; closeout:22 and its rationalization row at :118 say the opposite explicitly.

---

## 2. Questions for the owner

1. **The model note is the largest single risk in this lane and it lives only in the README.** Is there any appetite for a runtime check (the closeout skill states its model requirement and refuses to claim a sweep it could not run)? If the honest answer is "the gates only work on Opus", the install instructions should say it before the install command, not at README:112.
2. **Should an accepted CRITICAL turn the badge amber or red?** Right now publish.md counts only unchecked lines, so the most dangerous projects on the wall are indistinguishable from the cleanest. This is settled-decision-adjacent (the acceptance mechanism is deliberate), so it goes here rather than as an unqualified finding — but as built, the badge cannot express what the README says it expresses.
3. **Is leaving existing un-instrumented repos alone (hook, README:64) a deliberate politeness choice?** It costs you the adoption baseline for exactly the user in the product brief. A middle path: the non-state hook branch offers kickoff adoption once, in one line, instead of staying silent.
4. **`references/` path resolution** — is the intent that the agent globs for it, or should the skills spell out `${CLAUDE_PLUGIN_ROOT}`? Everything else in this lane is prose; this one is mechanical and cheap to make certain.
5. **Does anything re-ask kickoff question 4 ("is any of it real or sensitive")?** Half the runbook's CRITICAL checks self-gate on that answer, and it is captured once, at the moment the novice knows least about their own project.
6. **Windows:** README:108 says on Windows outside Git Bash/WSL "the reviews still happen but the model substitutes equivalent checks by hand." That is precisely the "I checked" without a command that invariant 1 forbids, sanctioned in writing. Should the skills instead refuse to claim a secret scan ran when the grep could not run?

---

## 3. Novice walkthrough gaps

Reading `skills/project-kickoff/SKILL.md` as someone who has never used git, never heard of an env var, and does not know what "auth" means.

1. **Question 2 ("Who uses it: just you, or others too?") silently decides authentication** (:46) but the novice is never told that is what they are answering. "Others too" means "some strangers" to them; it means "you must build a login" to the skill.
2. **Question 3 ("Do different people need to see or do different things?")** is unanswerable before the app exists. A novice building a recipe site says "no" thinking about screens, when the real answer is "yes, each person owns their own recipes". The glossary's `## authorization` card ("apps commonly check that you are logged in but not that this recipe is YOURS") is exactly the explanation they need and there is no instruction to show it with question 3.
3. **Question 4 ("is any of it real or sensitive?")** — a novice reads "sensitive" as medical records, not as their friends' email addresses. Yet this one answer gates the backup check, the restore rehearsal and the dev-vs-prod checks. No examples are offered to calibrate it.
4. **Question 5 bundles three decisions** (:43): where it lives, whether paid services are used, and by implication whether spend caps are needed. A novice does not know that "I want it to have AI in it" means "I will be billed per request and a stranger can run that bill up".
5. **Question 6 is the hardest question in the interview and is marked not optional** (:44, :46): "What does 'done' look like, and how would we prove a feature works, including what should happen when it fails?" A first-time builder cannot enumerate failure behaviours per feature. There is no worked example in the skill and no instruction to propose a draft table for the user to correct.
6. **Step 4 hands a guided novice nine unexplained terms in one message** (:56-66; see A6): frontend/backend split, real persistence, environment variables, `.gitignore`, git init, exact version pins, lockfile, spend cap, rate limit, test harness. The one-card-per-message rule does not reach here.
7. **"git initialized before the first file"** (:63) assumes git is installed. Nothing checks, and nothing tells the novice what to do if it is not.
8. **"a spend cap set at the provider"** (:65) — the novice does not know what a provider console is, that they have an account on one, or where the billing page is. lens-production-readiness.md:44 makes this an ask-the-user check, so the burden lands on the least-equipped participant, and an unverified "yes" is accepted into the record.
9. **The test harness step** (:66, "one passing test and one intentionally failing test ... show the failure being reported, then fix the failing one") is excellent pedagogy and is never explained as such to the guided user; there is no card for "test harness".
10. **The Step 5 confirmation asks the novice to confirm a summary "in their own words"** (:13) about a structure they have just been told about for the first time. A novice's genuine state is "I don't know enough to disagree." Nothing in the skill handles a confirmation given out of deference rather than understanding — and that confirmation is the gate that releases all code writing.
11. **The versioning rule** (:74-78) is folded into the playback as a non-question. The guided wording is good, but "the small build number" and "the version people see" are two concepts introduced in one sentence at the moment the user is trying to say yes to something else.
12. **Nothing in kickoff tells the novice what happens next or how long any of it takes.** The six questions are stated as a fixed cost ("The interview is six questions", :96) but the user is never given that framing up front, only the calibration question.

---

## 4. Coverage

**Files read in full (18 in scope, 0 skipped):**
skills/project-kickoff/SKILL.md, skills/project-checkpoint/SKILL.md, skills/project-closeout/SKILL.md, skills/project-audit/SKILL.md, skills/project-resume/SKILL.md, commands/{audit,checkpoint,closeout,kickoff,resume}.md, hooks/hooks.json, hooks/session-start.sh, .claude-plugin/plugin.json, .claude-plugin/marketplace.json, README.md, CHANGELOG.md, ROADMAP.md.

**Referenced files opened to check the seams (lane Q owns their contents):**
references/state-format.md (full), references/publish.md (full), references/audit-method.md (full), references/dependency-vetting.md (full), references/lens-security-auth.md (full), references/lens-production-readiness.md (full), references/lens-real-data.md (full), references/lens-testing.md (full), references/lens-llm-security.md (full), references/secret-patterns.grep (full), references/glossary.md (structure + spot-read of cards; full prose read is lane Q's), scripts/itworks-lint.sh (first 80 lines — the PROFILE/MAP/REVIEWS rules relevant to the seams; the remaining finding-line parser was not read in full because lane P's claims about it rest on state-format.md:169-181, which the script's header says it encodes).

**Not read:** tests/pressure/** and tests/scenarios/** (not in scope for this lane; the pressure results are cited from README:112 as the owner's own evidence, not independently re-run — re-running the Sonnet closeout case would strengthen C1 and is the recommended verification step).

**Probes run:**
- `bash -n hooks/session-start.sh` → clean, "SYNTAX OK".
- `python3 -m json.tool` on plugin.json, marketplace.json, hooks.json → all three parse.
- Hook executed under `<scratch>/audit/` in five states:
  - no `.itworks`: emits the short new-project branch, `(itworks v1.0.0)`, ending "Existing projects without .itworks/ are left alone unless the user runs a /itworks command."
  - `.itworks` present, **path containing a space** (`<scratch>/audit/with state/`): emits the full five-rule lifecycle block correctly; no word-splitting problem. Quoting in the script is sound throughout.
  - `.itworks` present but **no PROFILE.md**: byte-identical output to the healthy case. The hook makes no state-validity judgement; detecting the missing PROFILE.md is left entirely to project-resume's linter. Correct division of labour, no finding.
  - `ITWORKS_DISABLE=1`: no output, exit 0.
  - `.itworks-off` present: no output, exit 0.
- `ls skills/project-kickoff/` → `SKILL.md` only; no `references/` under any skill directory (basis for I1).
- Glossary card existence check by exact heading for the 15 terms the lenses and dependency-vetting name → all present except "dev vs production data" and "dependency (package)" (A5).
- grep across `skills/` and `references/` for paste / "give me your key" / "enter your" wording → no skill asks the user for a secret (invariant 6 clean).
- Publish count greps traced by hand against the state-format.md:131-133 example lines → confirms C2 (`critical_open` = 0 for an accepted CRITICAL).

**No file inside the repository was created, modified or deleted. No agents were spawned.**
