repo: Argelis-XVL/Revitalise
branch: deploy-first-learning-and-item-closure
path: src/code-apps/trustee-review-portal

## Last sync
date: 2026-09-30T18:03:16Z
commit: 4eb731ee2a44

### Updated in this project
- Application detail now shows the Trustee Pack's five sections row by row (Summary, Application Details, About Applicant, Current Circumstances, Financial Eligibility), using the Pack's own labels. The narrative panel and the portal-only fields are removed.
- Current Circumstances is split into four groups (the score, Life satisfaction, In the last 2 weeks…, In the last year…) with extra space between them.
- Nav order is now Round overview, Group applications, Individual applications. "Applications list" is renamed "Individual applications".

## Screen map
| Design system screen | Repo source |
| --- | --- |
| ui_kits/trustee-review-portal/AppFrame.jsx | src/App.tsx |
| ui_kits/trustee-review-portal/RoundOverview.jsx | src/pages/LandingPage.tsx, src/components/RoundStatistics.tsx, src/components/RoundFinancePanel.tsx, src/components/DistributionChart.tsx |
| ui_kits/trustee-review-portal/ApplicationsList.jsx | src/pages/ApplicationsListPage.tsx, src/components/ApplicationFilters.tsx, src/components/ApplicationsTable.tsx |
| ui_kits/trustee-review-portal/GroupScreens.jsx | src/pages/GroupsListPage.tsx, src/pages/GroupDetailPage.tsx, src/components/GroupsTable.tsx |
| ui_kits/trustee-review-portal/ApplicationDetail.jsx | src/pages/ApplicationDetailPage.tsx, src/components/CasePanels.tsx, src/domain/applicationDetailLayout.ts, src/components/VerdictSection.tsx |
| ui_kits/trustee-review-portal/Shared.jsx | src/components/Panel.tsx, src/components/VerdictDialog.tsx, src/domain/visibility.ts |

(src paths are relative to `src/code-apps/trustee-review-portal/`.)

## Sync history
- 2026-09-30T15:51:46Z — branch main. The Code App source landed, and the kit was rebuilt from it (four nav tabs, group screens, Pack panel order).
- 2026-08-27T17:50:14Z — commit b77ae88a0435. No Code App source in the repo yet. The kit was built from user screenshots.
