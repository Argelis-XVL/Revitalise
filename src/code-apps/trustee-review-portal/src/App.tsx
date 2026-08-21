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
import { StateMessage } from "./components/Panel";
import { useCurrentUser } from "./hooks/queries";
import styles from "./styles/app.module.css";

type View = { name: "list" } | { name: "detail"; application: ApplicationSummary };

export function App() {
  const [view, setView] = useState<View>({ name: "list" });
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

        {view.name === "list" ? (
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
