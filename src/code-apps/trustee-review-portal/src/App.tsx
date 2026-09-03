/**
 * The trustee portal shell — WBS 6.1 (the screen design over the secured tables).
 *
 * Landmarks: a skip link, a `<header>`, and a `<main id="main">` that the skip link
 * targets (WCAG 2.4.1, 1.3.1). One `<h1>` per view.
 *
 * Navigation is in-app view state rather than a router — see hooks/usePageTitle.ts for
 * why, and for the deviation that records it.
 *
 * ## Revision 4 (2026-08-27) — NAVIGATION STAYS A `<button>`; only `.rowLink` was restyled
 *
 * TAD §2.2.1's last row. The two navigation controls this shell owns — the skip link and
 * "Back to the round overview" — are unchanged in element and in role, and that is the whole
 * decision rather than an oversight:
 *
 *   - **"Back to the round overview" is a `<button>` and stays one.** It changes in-app view
 *     state; it navigates to no URL. The supplied mockup uses
 *     `<a href="#" onClick={e => e.preventDefault()}>` for the equivalent control
 *     (`ui_kits/trustee-review-portal/ApplicationsList.jsx:26`), which is a semantics
 *     regression — a screen reader announces "link", a keyboard user expects Enter-only
 *     rather than Enter-and-Space, and nothing is at the other end — and an `href="#"` inside
 *     a Power Apps Code App host is a navigation risk rather than a style choice.
 *   - **The skip link IS a real `<a href="#main">`**, because that one genuinely navigates to
 *     a fragment, and `<main id="main">` is what it targets (WCAG 2.4.1).
 *
 * `.rowLink` — the class both this control and the table's per-row reference button use — now
 * takes its colour from `--link-default`, which resolves to the same supplied brand[70]
 * `#cc0078` it already carried through `--colorBrandForegroundLink` (5.47:1). A change of
 * vocabulary, not of colour. It stays underlined, so colour is never the only carrier of the
 * fact that it is a control (WCAG 1.4.1).
 *
 * ## Revision 7 (2026-08-30, `IMP-0510`, ADR-040) — a persistent nav bar replaces the
 * `list` view's contextual "Back to the round overview" button
 *
 * `AppFrame.jsx`/`TrusteePortalApp.jsx` (the supplied app-specific ui_kit, read in full for
 * the first time this revision) show a fixed bar of three buttons naming every screen —
 * Round overview / Applications list / Application detail — always present, indicating the
 * current view via a filled/unfilled contrast. This shell had no equivalent: only a
 * one-directional contextual link on the `list` view. The nav bar below REPLACES that
 * control (it becomes redundant once every screen is one click away at all times) but does
 * **not** replace `ApplicationDetailPage`'s own "back to the list" — that stays as a second,
 * faster route back from the one screen deepest in the flow.
 *
 * **Still real `<button type="button">`s, still no router** — the same two decisions the
 * Revision 4 comment above already made, restated because they apply again: `TrusteePortalApp
 * .jsx:10`'s tab markup is already a plain `<button>` (unlike the `<a href="#">` regression
 * elsewhere in the ui_kit), so it is adopted as markup, not merely as visual reference; and
 * `hooks/usePageTitle.ts`'s reasoning for in-app view state over a router is untouched — the
 * bar changes which `View` is active through the same `setView` calls every other control
 * here already uses, exactly as the ui_kit's own `useState('overview')` does.
 *
 * **THE "STAYS AS A SECOND, FASTER ROUTE BACK" HALF OF THE PARAGRAPH ABOVE IS REVERSED BY
 * REVISION 11'S ITEM 7 (2026-09-02, wbs:6.8), AT THE REVIEWER'S DIRECTION.** The detail screen's
 * own "Back to the list" button is removed as redundant with this bar's "Applications list" tab,
 * and `onBack` is removed from `ApplicationDetailPage`'s props with it. The reasoning, and what
 * the reversal costs, is in that file's own Revision 11 header rather than restated here; the
 * paragraph above is left standing so the decision it recorded is still legible.
 *
 * **The "Application detail" control is disabled — not hidden — until a case is open.** The
 * ui_kit sidesteps this with a hardcoded fallback case id (`TrusteePortalApp.jsx:17`,
 * `'REV-2026-1057'`), which is prototype convenience this app does not inherit: `view.name
 * !== "detail"` has no application to show. `aria-disabled` (not the native `disabled`
 * attribute) keeps the control in the tab order — a native `disabled` button is pulled out of
 * it, which would change how many stops the bar has between its two states, one more
 * inconsistency than the caption below already carries alone — and a visible caption gives
 * the reason rather than leaving a control that looks present but silently does nothing on
 * click (A-R55).
 *
 * ## Revision 9 (2026-09-01, wbs:6.9) — reviewer item 5 REVERSES THE PARAGRAPH ABOVE, AND
 * THAT IS A DOCUMENTED DEVIATION FROM ADR-040, NOT A CORRECTION OF IT
 *
 * **The "Application detail" control is now rendered ONLY on the detail view.** On the landing
 * and list screens it is absent from the bar entirely — not disabled, not captioned, not
 * present. The reviewer asked for that explicitly against the live DEV portal, having seen the
 * disabled-and-captioned state ADR-040 designed and A-R55 accepted.
 *
 * **WHAT THIS CONTRADICTS, STATED PLAINLY SO IT IS NOT READ LATER AS DRIFT.** ADR-040
 * (Revision 7, `IMP-0510`) decided a PERSISTENT three-button bar naming every screen at all
 * times, and the paragraph above records the reasoning for the disabled-not-hidden half twice
 * over: an appearing/disappearing control is harder to learn than a legible disabled one, and
 * `aria-disabled` was chosen over the native attribute specifically so the bar's tab-stop count
 * would not change between states. **Item 5 gives up both of those properties**: the bar now
 * has two controls on two screens and three on the third, and its tab-stop count changes with
 * the view. That is the reviewer's call to make — it is a design preference about their own
 * product, not a standard — but it is a reversal of a recorded architecture decision and
 * `development-agent` carries it into the Dev Summary as one, for the TAD to amend rather than
 * for a later reader to find as an unexplained contradiction between ADR-040 and this file.
 *
 * **WHAT IT DOES NOT GIVE UP.** No accessibility contract rests on the third button: it never
 * navigated anywhere (its `onClick` was empty by construction — when it was enabled the app was
 * already on that view), so removing it removes no route to any screen. The one thing it
 * carried was the CAPTION explaining why a visible control did nothing, and a control that is
 * not rendered needs no such explanation — the WCAG 3.3.1-shaped problem the caption solved
 * only exists while the control is on screen. `aria-current="page"` still marks the detail
 * button when it is shown, so the bar still states the current view rather than only colouring
 * it (WCAG 1.4.1). `.viewNavButtonDisabled` and `.viewNavCaption` are removed from
 * `app.module.css` in the same change: a class no call site can reach is dead code that reads
 * as a live decision.
 *
 * ## Revision 10 (2026-09-02, wbs:6.8) — reviewer item 6: the applications-list title moves
 * OUT of the header and UNDER the nav bar, to match the other two screens
 *
 * `LandingPage`'s and `ApplicationDetailPage`'s own `<h1>`s were already rendered by those
 * page components themselves, inside `<main>` and therefore visually and structurally BELOW
 * the persistent nav bar this file renders above `{view.name === ... ? <Page .../> : ...}`.
 * This shell's own conditional `<h1>Applications under review</h1>` — rendered here, inside
 * `<header>`, which comes before `<main>` and the nav bar entirely — was the one title that
 * did not match. It is removed from here and now lives in `ApplicationsListPage` itself,
 * rendered in the same position its sibling pages already use theirs. `usePageTitle` (the
 * document-title / browser-tab side of this) is unchanged in every page — this is a VISUAL
 * heading position fix, not a navigation or document-title one.
 */
import { useState } from "react";
import type { ApplicationSummary } from "./dataverse/types";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsListPage } from "./pages/ApplicationsListPage";
import { LandingPage } from "./pages/LandingPage";
import { StateMessage } from "./components/Panel";
import { classNames } from "./components/ds/classNames";
import { useCurrentUser } from "./hooks/queries";
// A-BRAND-1 CLOSED, 2026-08-27. Vite's default asset handling (`import logoUrl from
// "./assets/revitalise-logo.png"`) compiles to a RUNTIME `new URL("revitalise-logo-<hash>.png",
// import.meta.url).href` in the built JS — confirmed live: a real trustee opened the app and
// the logo did not render, while the JS/CSS bundle itself (referenced by plain relative paths
// in index.html, not `import.meta.url`) loaded fine. The Power Apps Code App host does not
// resolve that runtime construction the way a plain static host does.
//
// The `?inline` suffix forces Vite to embed the file as a base64 data URI at build time
// instead, regardless of its size — no runtime URL construction, so nothing left for the host
// to resolve incorrectly. The file stays a copy inside `src/assets/` rather than a reference
// to `docs/Import/LogoRev.png`, because nothing outside `src/` is part of the app's build.
// Trade-off, accepted: adds ~270KB (base64 overhead) to the built JS for this one-time brand
// asset.
import logoUrl from "./assets/revitalise-logo.png?inline";
import styles from "./styles/app.module.css";

/**
 * The three views, in the order FR-056 puts them: landing -> list -> detail.
 *
 * `landing` is the ENTRY state (FR-056: "trustees have a clear starting point instead of
 * landing directly inside case data"). Before WBS 6.9 the app started at `list`, which
 * opened straight onto the round's cases.
 */
type View =
  | { name: "landing" }
  | { name: "list" }
  | { name: "detail"; application: ApplicationSummary };

export function App() {
  const [view, setView] = useState<View>({ name: "landing" });
  const currentUser = useCurrentUser();

  // `resolveCurrentUser` never rejects — an unresolved user is a valid result carrying
  // its own reason — so this branch is the "the query itself blew up" case.
  const user = currentUser.data ?? {
    systemUserId: null,
    fullName: null,
    entraObjectId: null,
    unresolvedReason:
      currentUser.error?.message ??
      "The portal is still working out who you are signed in as.",
  };

  return (
    <div className={styles.page} data-print="page">
      <a className={styles.skipLink} href="#main">
        Skip to the applications
      </a>

      <header className={styles.header}>
        <div className={styles.brandLockup}>
          {/*
            The charity's logo. NFR-026 asks for brand-consistent rendering but names no
            placement, and neither does the TAD (grepped) — so the shell header is this
            pass's own reasoned choice: it is the one element all three views share, so one
            placement brands every screen and the print output with no per-page work.

            `alt` is the organisation's name, not `alt=""`: this identifies the charity whose
            money the round distributes, which is content rather than decoration
            (WCAG 1.1.1). The name is the one this repository already records for it —
            knowledge/technology/stack-overview.md's publisher display name.

            It deliberately does NOT transcribe the strapline the image also carries
            ("Funding vital respite for disabled people & carers"). A logo's text
            alternative serves the purpose of identifying the organisation; repeating a
            marketing line to a screen-reader user on every one of the three views, when no
            sighted reader can read it at this render size either (see `.logo` in
            app.module.css), would be noise rather than an equivalent.

            `width`/`height` are the file's real intrinsic pixels (1340x434). They are there
            so the browser reserves the right box before the image loads; the rendered size
            comes from `.logo`, which pins the height and lets the width follow the ratio.
          */}
          <img
            className={styles.logo}
            src={logoUrl}
            alt="Revitalise Respite Holidays"
            width={1340}
            height={434}
            data-print="brand"
          />
        </div>
        <p className={styles.signedInAs}>
          {user.fullName === null
            ? "Signed in — your name was not available from Power Apps."
            : `Signed in as ${user.fullName}.`}
          {user.systemUserId === null ? " Your trustee record is not confirmed yet." : ""}
        </p>
      </header>

      <main id="main">
        {user.systemUserId === null ? (
          // Shown once, at the top, rather than repeated on every verdict control. It
          // does not block reading the cases — only recording a verdict, which the
          // verdict panel explains again in place.
          <StateMessage
            heading="You can read cases, but not record a verdict yet"
            explanation={
              (user.unresolvedReason ?? "Your trustee record could not be confirmed.") +
              " Everything anonymised on these screens is still readable."
            }
          />
        ) : null}

        {/*
          ADR-040 (Revision 7) — the persistent view-switching bar, rendered on every view.
          Replaces the `list` view's old contextual "Back to the round overview" `<button>`
          (redundant once every screen is one click away at all times) and, as of Revision 11's
          reviewer item 7, `ApplicationDetailPage`'s own "Back to the list" as well — this tab is
          now the only route back from the detail screen. See this file's Revision 7 header for
          the decision that reverses.

          Rendered by the shell rather than inside any one page, on purpose: this file owns
          the view state, so it owns the controls that change it — the same reasoning the
          control it replaces already used.

          Named "Screen navigation" rather than reusing `LandingPage`'s own "Portal sections"
          landmark name: `LandingPage` renders its own `<nav aria-label="Portal sections">`
          (the single "open the applications list" link) at the SAME time this bar is on
          screen, and two landmarks sharing one accessible name are indistinguishable to a
          screen-reader user navigating by landmark (WCAG 2.4.1, 4.1.2).
        */}
        <nav aria-label="Screen navigation" className={styles.viewNav} data-print="hide">
          <button
            type="button"
            className={classNames(
              styles.viewNavButton,
              view.name === "landing" ? styles.viewNavButtonSelected : undefined,
            )}
            aria-current={view.name === "landing" ? "page" : undefined}
            onClick={() => {
              setView({ name: "landing" });
            }}
          >
            Round overview
          </button>
          <button
            type="button"
            className={classNames(
              styles.viewNavButton,
              view.name === "list" ? styles.viewNavButtonSelected : undefined,
            )}
            aria-current={view.name === "list" ? "page" : undefined}
            onClick={() => {
              setView({ name: "list" });
            }}
          >
            Applications list
          </button>
          {/*
            REVIEWER ITEM 5 (Revision 9, wbs:6.9) — shown ONLY while the detail view is the
            active one. This REVERSES ADR-040 / A-R55's "disabled, not hidden" decision at the
            reviewer's explicit direction; this file's Revision 9 header states what that gives
            up and why it costs no accessible behaviour. It is kept as a rendered control
            rather than dropped altogether so the bar still names the screen a trustee is on
            and still carries `aria-current="page"` for it.
          */}
          {view.name === "detail" ? (
            <button
              type="button"
              className={classNames(styles.viewNavButton, styles.viewNavButtonSelected)}
              aria-current="page"
              onClick={() => {
                // Already on this view whenever this control exists at all — it is a state
                // indicator that happens to be a button, which is what the other two are too.
              }}
            >
              Application detail
            </button>
          ) : null}
        </nav>

        {view.name === "landing" ? (
          <LandingPage
            onOpenList={() => {
              setView({ name: "list" });
            }}
          />
        ) : view.name === "list" ? (
          <ApplicationsListPage
            user={user}
            onOpenApplication={(application) => {
              setView({ name: "detail", application });
            }}
          />
        ) : (
          // `onBack` is gone as of Revision 11, reviewer item 7 — the detail screen's own
          // "Back to the list" button is removed and the nav bar's "Applications list" tab
          // above is the only route back. See `ApplicationDetailPage`'s Revision 11 header
          // for the reversal that records.
          <ApplicationDetailPage
            applicationId={view.application.id}
            fallbackReference={view.application.reference}
            user={user}
          />
        )}
      </main>
    </div>
  );
}
