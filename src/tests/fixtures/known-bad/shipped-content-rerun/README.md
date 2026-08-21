# known-bad fixture — `shipped-content` check 7 (prose promises an unbuilt re-run)

`FixtureRerunFlow` triggers on row CREATED only (`subscriptionRequest/message: 1`, the same
shape `REVScoringCalculateAndFlag` used) and its Teams message tells the process owner to
"re-run scoring" — the exact defect `IMP-0139` recorded: there is no re-run mechanism behind a
create-only trigger, and Resubmit in the run history replays the cached payload rather than
re-running anything.

The flow's own `description` field ALSO contains the phrase "safe to re-run this flow by hand"
— deliberately, to prove the check does not fire on developer-facing documentation, only on
what actually ships to a user (`body/messageBody`, `item/<column>` writes, etc.).

```bash
python3 scripts/verify-shipped-content.py <this dir>   # must FAIL, naming the Teams message
```
