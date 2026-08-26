/**
 * The trustee portal shell — WBS 6.1 (the screen design over the secured tables).
 *
 * Landmarks: a skip link, a `<header>`, and a `<main id="main">` that the skip link
 * targets (WCAG 2.4.1, 1.3.1). One `<h1>` per view.
 *
 * Navigation is in-app view state rather than a router — see hooks/usePageTitle.ts for
 * why, and for the deviation that records it.
 */
import { useState } from "react";
import type { ApplicationSummary } from "./dataverse/types";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsListPage } from "./pages/ApplicationsListPage";
import { LandingPage } from "./pages/LandingPage";
import { StateMessage } from "./components/Panel";
import { useCurrentUser } from "./hooks/queries";
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
        {view.name === "list" ? <h1>Applications under review</h1> : <span />}
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
