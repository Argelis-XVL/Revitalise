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
 */
import { useState } from "react";
import type { ApplicationSummary } from "./dataverse/types";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsListPage } from "./pages/ApplicationsListPage";
import { LandingPage } from "./pages/LandingPage";
import { StateMessage } from "./components/Panel";
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
          {view.name === "list" ? <h1>Applications under review</h1> : null}
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
          The way back up FR-056's chain (landing -> list -> detail). The detail screen
          already has its own "back to the list"; without this the list would be a dead end
          and a trustee would have to reload the app to see the round's figures again.

          Rendered by the shell rather than inside `ApplicationsListPage`, on purpose: the
          TAD's component diagram has that page unchanged by this pass (WBS 6.2, FR-034),
          and navigation between views is already the shell's job — this file owns the view
          state, so it owns the controls that change it.

          "Portal sections" is the same landmark name the landing screen's nav uses. Only
          one is ever rendered, and a consistently-named navigation landmark is easier to
          move between views by than two differently-named ones (WCAG 2.4.1, 3.2.3).
        */}
        {view.name === "list" ? (
          <nav aria-label="Portal sections" className={styles.backNav} data-print="hide">
            <button
              type="button"
              className={styles.rowLink}
              onClick={() => {
                setView({ name: "landing" });
              }}
            >
              Back to the round overview
            </button>
          </nav>
        ) : null}

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
          <ApplicationDetailPage
            applicationId={view.application.id}
            fallbackReference={view.application.reference}
            user={user}
            onBack={() => {
              setView({ name: "list" });
            }}
          />
        )}
      </main>
    </div>
  );
}
