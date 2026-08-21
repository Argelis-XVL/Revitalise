/**
 * "Who am I, as a Dataverse systemuser?" — isolated here on purpose.
 *
 * Everything about this module is an UNVERIFIED PLATFORM CONTRACT. Resolving the
 * signed-in user of a Code App to the `systemuserid` that `rev_review.rev_trustee1` /
 * `rev_trustee2` point at has not been ground-truthed on this project, and it cannot be
 * from a workstation: it needs the app running in the Power Apps host, signed in as a
 * trustee. So it lives in one file with one exported function, and the rest of the app
 * consumes only its result.
 *
 * A-TR-11 (GUESS, E2) — the whole chain below. Three links, each unobserved:
 *
 *   1. `getContext()` from `@microsoft/power-apps/app` resolves inside the host and
 *      populates `user.objectId` with the signed-in user's Entra object id.
 *      Evidence: the SDK's own shipped type declarations for 1.3.0 (IUserContext).
 *   2. `systemuser` is readable through the Dataverse connector by a trustee. The
 *      `REV Trustee` role does hold `prvReadUser`
 *      (Roles/REV Trustee/REV Trustee.xml), which is why this route was chosen over
 *      expanding the lookup — but privilege present is not the same as row returned.
 *   3. A `uniqueidentifier` column filters as a BARE guid in OData
 *      (`azureactivedirectoryobjectid eq 00000000-...`), unquoted.
 *
 * Cheapest verification, all three at once: run the app in the Power Apps host as a
 * trustee once and read the "signed in as" line — it prints the resolved name and
 * states plainly when the id could not be resolved.
 *
 * Failure here is not an authorisation failure and must not read like one. It makes the
 * verdict control read-only and says why (see domain/slots.ts → `unknown-user`).
 */
import { getContext } from "@microsoft/power-apps/app";
import { listRecords } from "./client";
import { asGuid, asString, odataString } from "./odata";
import { ENTITY_SETS, PRIMARY_KEYS, SYSTEM_USER_COLUMNS } from "./schema";
import type { CurrentUser } from "./types";

interface HostUser {
  fullName: string | null;
  entraObjectId: string | null;
  userPrincipalName: string | null;
}

async function readHostUser(): Promise<HostUser | null> {
  try {
    const context = await getContext();
    return {
      fullName: asString(context.user.fullName),
      entraObjectId: asGuid(context.user.objectId),
      userPrincipalName: asString(context.user.userPrincipalName),
    };
  } catch {
    return null;
  }
}

/**
 * Finds the systemuser row for the signed-in user.
 *
 * Entra object id is tried first because it is stable; the UPN is a fallback because it
 * is not (a rename breaks it). Only ONE row is accepted — two rows matching means the
 * question was ambiguous, and guessing between them is how the wrong trustee's verdict
 * gets overwritten.
 */
async function findSystemUserId(host: HostUser): Promise<
  { id: string } | { reason: string }
> {
  const attempts: { filter: string; describe: string }[] = [];
  if (host.entraObjectId !== null) {
    attempts.push({
      filter: `azureactivedirectoryobjectid eq ${host.entraObjectId}`,
      describe: "your Entra ID account",
    });
  }
  if (host.userPrincipalName !== null) {
    attempts.push({
      filter: `domainname eq ${odataString(host.userPrincipalName)}`,
      describe: "your sign-in name",
    });
  }
  if (attempts.length === 0) {
    return {
      reason:
        "The Power Apps host did not tell this app who is signed in, so your user record " +
        "could not be looked up.",
    };
  }

  const problems: string[] = [];
  for (const attempt of attempts) {
    let rows;
    try {
      const result = await listRecords({
        entityName: ENTITY_SETS.systemUser,
        select: SYSTEM_USER_COLUMNS,
        filter: attempt.filter,
      });
      rows = result.rows;
    } catch (caught) {
      problems.push(
        `Looking you up by ${attempt.describe} failed: ${
          caught instanceof Error ? caught.message : "unknown error"
        }.`,
      );
      continue;
    }
    if (rows.length === 1) {
      const id = asGuid(rows[0]?.[PRIMARY_KEYS.systemUser]);
      if (id !== null) return { id };
      problems.push(`Your user record was found by ${attempt.describe} but carries no id.`);
      continue;
    }
    if (rows.length > 1) {
      problems.push(
        `More than one user record matches ${attempt.describe}, so the portal cannot tell ` +
          "which one is you.",
      );
      continue;
    }
    problems.push(`No user record matches ${attempt.describe}.`);
  }

  return { reason: problems.join(" ") };
}

/** Resolves the signed-in user. Never throws — an unresolved user is a valid result. */
export async function resolveCurrentUser(): Promise<CurrentUser> {
  const host = await readHostUser();
  if (host === null) {
    return {
      systemUserId: null,
      fullName: null,
      entraObjectId: null,
      unresolvedReason:
        "This app could not read the signed-in user from the Power Apps host. It may not be " +
        "running inside Power Apps.",
    };
  }

  const found = await findSystemUserId(host);
  if ("id" in found) {
    return {
      systemUserId: found.id,
      fullName: host.fullName,
      entraObjectId: host.entraObjectId,
      unresolvedReason: null,
    };
  }
  return {
    systemUserId: null,
    fullName: host.fullName,
    entraObjectId: host.entraObjectId,
    unresolvedReason: found.reason,
  };
}
