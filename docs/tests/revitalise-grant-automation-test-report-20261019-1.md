# Test Report — revitalise-grant-automation, Create Envelope drops p_type (wbs:3.2)

Artifact: build/artifacts/revitalise-grant-automation-20261019-1  |  Date: 2026-10-19  |  Result: PARTIAL

## Scope
Single change: REVAcceptanceCreateEnvelope no longer fills prefill tab p_type ("Holiday type"); required read-back ids 15 to 14; rev_breaktype dropped from Get_the_application $select; Compose_tab_values 57 to 55 keys.

## Results
| Case | Result | Evidence |
|---|---|---|
| Source flow has no p_type / breaktype / Holiday type reference | PASS | grep over the flow json: 0 hits; json parses |
| Artifact (RevitaliseGrantAutomation.zip) flow equals source flow | PASS | unzipped, parsed json equal, 0 hits |
| Compose_tab_values = 55 keys, 4 prefill keys, label|p_type and prefill|Holiday type absent | PASS | counted from json (55); AcceptanceEnvelopeContract Pester |
| Filter_missing_tabs from = 14 ids (4 prefill + 5 per signer) | PASS | json read-back of the list |
| $select lists 14 columns, rev_breaklocation kept for p_venue | PASS | diff |
| AcceptanceEnvelopeContract.Tests.ps1 | PASS | 71 passed, 0 failed |
| Full Pester suite | PASS | 1350 total, 1349 passed, 0 failed, 1 skipped (same skip as build) |
| Build result | PASS | run-build-result.json SUCCESS, 102 steps |
| verify-flow-definition-language, verify-guid-syntax | PASS | exit 0 |
| Old template (still has Holiday type) is stopped before send | PARTIAL | Generic unmapped-tab case is tested (Shoe size); no test names Holiday type specifically |
| Live DocuSign run against the new template | NOT RUN (V5) | Needs DEV flow run; template version dependency (V4 human step) |

## Doc-vs-artifact gap (not a code failure)
Architecture doc still describes 57 keys / 15 ids / five prefills at L1540, L1543, L1586, L1682 (and per the Dev Summary L1547, L1664, L3971-3973, L12304). architect-agent owns the update.

## Constraints
No new data column, no secret, no new connection; rev_breaktype was classified not personal (2026-09-30 ruling), so dropping it changes no personal-data exposure. No HARD constraint touched. Full constraint sweep not re-run beyond the build's own gates.

IMPROVEMENT LOG: none
