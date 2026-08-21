// KNOWN-BAD fixture for the `no-secured-columns-in-code-app` build gate
// (scripts/verify-code-app-column-bindings.py). DELIBERATELY WRONG — never copy into
// src/code-apps/. The gate must exit 1 on this directory.
//
// The defect: the $select below names a column that Dataverse column security hides from the
// trustee role. For a trustee it returns empty, so the screen "looks fine" in testing; for the
// process owner — who IS a member of REV_TrusteeRestricted and who also has access to this
// portal per TAD §6.1 — it returns the raw Article 9 narrative. A trustee-facing query that
// leaks under a different role is not a trustee-facing query.
//
// The three fail-closed visibility columns ARE present below, so this fixture isolates the
// forbidden-column failure rather than tripping the required-column checks as well.
// Asserted by src/tests/build/BuildGates.Tests.ps1.

export const APPLICATION_DETAIL_SELECT = [
  'rev_applicationid',
  'rev_circumstancescore',
  'rev_scorebreakdown',
  'rev_eligibleforround',
  'rev_reviewround',
  'rev_redactionreleased',
  'rev_narrativeredacted',
  // THE DEFECT — Article 9 special-category data, secured to Admin + Service only.
  'rev_narrativeraw',
].join(',');
