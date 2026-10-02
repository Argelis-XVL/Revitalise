/**
 * Keeps `document.title` in step with the visible view.
 *
 * WCAG 2.4.2 asks for a descriptive, unique title per view. This app navigates by
 * in-app state rather than by URL, so nothing updates the title for us.
 *
 * Why in-app state and not a router: whether the Power Apps player supports HTML5
 * history routing is a platform contract this project has not ground-truthed, and a
 * broken back button on a decision screen is worse than a URL that does not deep-link.
 * A deviation from `code-apps.md`'s implied `/case-detail/:id` route convention,
 * recorded rather than assumed.
 */
import { useEffect } from "react";

const SUFFIX = "Trustee Review Portal";

export function usePageTitle(title: string): void {
  useEffect(() => {
    document.title = `${title} — ${SUFFIX}`;
  }, [title]);
}
