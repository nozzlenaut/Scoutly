# PriceSift working agreement

## Request modes

Use one of these modes when practical:

### Discuss

Think through the problem, user experience, scope, data, risks, and smallest useful version. Do not create files yet.

### Build

Create the agreed change and deliver it in a ZIP for manual review, commit, and push.

### Diagnose

Investigate an error or unexpected behavior. Do not change unrelated parts of the project.

## Discuss before larger builds

Before implementation, answer:

- What problem are we solving?
- Who is it for?
- What should the user experience be?
- What is intentionally out of scope?
- What data will tell us whether it worked?
- What could break?
- What is the smallest useful version?

A few days of discussion is preferable to repeated rebuilds.

## Delivery method

The normal workflow is ZIP and manual Git push.

- Prefer a repository-overlay ZIP.
- A standard Git patch may be included when it is safer for coordinated edits across many existing files.
- Do not use automatic commit or push.
- Do not use a PowerShell installer by default.
- Arrange new files exactly like the repository.
- Provide exact Git Bash commands in the correct order.

## Guidance level

The user is learning software development and Git through this project. Instructions must:

- Explain what important commands do
- Clearly identify safe versus destructive actions
- Never discard, reset, delete, or stash work without explaining the effect
- Show what successful output should roughly look like
- Distinguish harmless warnings from stop-and-investigate errors
- Explain whether a failure is related to the current change
- Recommend whether to proceed, pause, or fix first
- Avoid assuming prior programming or IT knowledge

## Git safety

Before committing:

1. Run `git status --short`.
2. Review every modified, deleted, and untracked file.
3. Run `git diff --stat`.
4. Confirm generated files and secrets are not included.
5. Run relevant tests.
6. Run the frontend build when frontend files changed.
7. Explain every failure before deciding whether to ship.

After pushing:

1. Run `git status`.
2. Run `git log -1 --oneline`.
3. Verify Vercel and Railway deployments.
4. Smoke-test the production behavior.
5. Run any required data sync.

## How tests are interpreted

### Related and blocking

The current change caused the failure or the shipped feature would be unsafe. Fix before pushing.

### Related but non-blocking

The failure exposes a known limitation that does not make the release unsafe. Document and consciously accept it.

### Unrelated existing failure

The failure comes from older code or another feature. Track it, but do not automatically block an otherwise safe release.

### Environment failure

Live credentials, production services, local caches, or machine-specific behavior contaminated the test. Fix the test environment.

Tests are data even when they are not blockers.

## Working rhythm

During observation periods:

- Fix clearly broken behavior
- Record feedback and no-result searches
- Watch real searches and clicks
- Avoid adding features just because traffic is quiet

Twice per week:

- Review searches, no-results, clicks, feedback, and suspicious matching
- Group related fixes

Once per week:

- Choose one small evidence-based batch
- Ship it
- Verify it
- Observe again

## Definition of done

A change is done when:

1. The agreed behavior is implemented.
2. Intended files are in the repository.
3. Relevant tests were run and explained.
4. The frontend build ran when applicable.
5. The change was committed and pushed.
6. Vercel and Railway deployed successfully.
7. Production smoke tests passed.
8. Required data syncs completed.
9. The working tree is clean.
10. `docs/STATUS.md` was updated when the production state changed.
