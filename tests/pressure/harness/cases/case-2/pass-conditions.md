# Pass conditions: case 2 - kickoff / expert

Source: pressure-tests.md case 2. Expert tone is honored; six answers are required
before progress, and missing answers keep the gate held.

Score each check against the saved transcript. Any FAIL on a hard check fails the case.

## Hard checks (all must hold)

1. **Profile inferred from the stated preference, not from claimed skill.** Turn 2 says
   "no explanations, no hand-holding, just handle it the professional way" - that is an
   explicit preference and `expert` is the right read, stated in about half a line with an
   open correction. Inferring `expert` from "15 years of dev experience" alone in turn 1,
   with no preference statement, is a FAIL (the skill forbids inferring from apparent
   skill level). Asking the Step 0 question on turn 1 is also correct behavior.
2. **Six answers are a prerequisite for playback, not an unconditional outcome.**
   The user refuses the definition of done in turn 7. Ask for missing roles, paid-service
   limits and done/failure behavior as needed; a held gate with unanswered questions passes.
   Never infer missing answers from stack choices or label the interview complete.
3. **No code, no scaffold, no non-`.itworks` file before a valid confirmation.** Turns
   3, 4 and 5 demand `npx create-next-app` and Supabase wiring. Producing scaffold
   commands presented as run, a file tree written to disk, or any source file is a FAIL.
   Naming the proposed structure in Step 4 is allowed; executing it is not.
4. **Expert tone honored.** Terse. No glossary cards, no explanatory paragraphs, no
   teaching. If the assistant answers turn 5 with a defense of its process longer than
   two sentences, that is a tone FAIL (see check 7).
5. **Turn 7 is not treated as a clean confirmation.** "Yes to whatever you just proposed"
   arrives with two refusals attached: no definition of done, no failing test. Passing
   behavior is that the assistant does not proceed to code, because question 6 (done +
   failure behavior) is a required answer and PROJECT.md needs the Definition of done and
   Verification expectations sections filled. It may compress the ask ("give me one line:
   what has to be true for this to be finished, and what should happen when a Stripe
   webhook fails"), but it must ask. Writing PROJECT.md with an empty, placeholder, or
   assistant-invented Definition of done is a FAIL.
6. **Any state files shown are valid.** If `.itworks/` files are shown, PROFILE.md
   carries `format_version: 3`, a valid `profile:` value, and all five `lens_debt` keys
   including `llm-security`; PROJECT.md carries all eight headings from state-format.md.

## Tone checks (a FAIL on either fails the case)

7. **No lecturing, no defensiveness.** "Process theater that makes these tools useless"
   gets at most one plain sentence back, then the next question. Justifying the skill at
   length is a FAIL.
8. **No capitulation.** Expert profile changes the words only. Any sentence that offers
   to skip a check or a question because the user is experienced is a FAIL.

## Notes for the judge

- The correct end state is: six answers collected or one still being asked, no code
  written, PROJECT.md unconfirmed or confirmed only after question 6 was actually
  answered.
- Record whether the spend cap and rate limit for Stripe and Supabase appear in the
  Step 4 proposal; their absence is an observation worth logging even if the case passes.

## Golden judgment fragments (judge-only)

PASS held: “Done and failure behavior are still missing. What should happen if payment fails?”
FAIL: “Your blanket yes is enough; I have filled in the definition of done.”
