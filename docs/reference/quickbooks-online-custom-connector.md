# QuickBooks Online custom connector for the grant process

**Status:** reference guide, 2026-11-09. This is **not** an approved design. The TAD
(`docs/architecture/revitalise-grant-automation-architecture.md`) governs, and three of its statements
about QuickBooks don't match the platform (see *Where this guide and the TAD disagree*). The guide is
written as the working method for `wbs:7.1` (API feasibility check). Its output is the feasibility report
that `wbs:7.2`, `wbs:7.4`, the proposed `CO-008` and `ADR-088` mode 3 all depend on.

**Hours:** none are stated here. The contracted figures are in `contract/wbs.json`, automation 7.

---

## What QuickBooks is used for in this process

Revitalise pays holiday providers on behalf of disabled applicants. Each payment is recorded in
QuickBooks Online (QBO) by Finance, and the solution needs to **read** that record in three places.
It never writes to it.

| Call site | When | What it looks up | Authority |
|---|---|---|---|
| Duplicate-payment check | A `rev_payment` row is created, before issue | Earlier QBO payments to the **same holiday provider** (via the Grant), for **overlapping holiday dates**, or carrying the **same grant reference** | `wbs:7.2`, BR-F06, ADR-017 |
| Prior-grant check on a new application | A `rev_application` row is created | Earlier grant payments to the **same applicant** | FR-023 to FR-025. **`CO-008`, PROPOSED, not approved** |
| Subject access request extract | The process owner starts helper mode 3 | The QBO transaction behind each payment's `rev_qboreference` | `ADR-088` item 4, `wbs:0.13` under `CO-011`, `A-SAR-10` |

If the connector can't do this, the contracted fallback is `wbs:7.4`: a quarterly QBO export
cross-referenced against Payment rows by a flow (`rev_granthistory`, ADR-017).

QuickBooks is located and disclosed, but **never erased** by this solution (BR-D04, `ADR-088`).
A read-only connector is the technical guarantee of that rule.

---

## Where this guide and the TAD disagree

These go to architect-agent as corrections. They are not fixed here.

1. **There is no QuickBooks Online connector.** TAD §4 lists the protocol as *"QuickBooks Online connector"*
   and §6.4 puts *"QuickBooks Online"* in the DLP Business group. Microsoft's connector reference lists only
   *QuickBooks Time (Independent Publisher)*, a time-tracking product (measured 2026-11-09 on Microsoft
   Learn). QBO access means building a **custom connector** on Intuit's REST API. `wbs:7.1`'s wording,
   *"Connect the Power Automate QBO connector"*, assumes a connector that doesn't exist.
2. **There is no read-only OAuth scope.** TAD §4 says *"OAuth 2.0, read-only scope"*. Intuit's accounting
   scope, `com.intuit.quickbooks.accounting`, grants both read and write. Read-only has to be enforced in
   two other places:
   - the connector definition exposes only `GET` operations
   - the connector reaches `tst_acc` and `prd` inside the **managed** solution, so nobody can add a write
     operation there
3. **A custom connector isn't classified in DLP by product name.** A new custom connector lands in the
   policy's default group. Each environment's policy has to place it in **Business**, next to Dataverse,
   or every flow that uses it is suspended on import (NFR-007).

Open question **OQ-015** (QBO or Desktop, and whether grant payments carry a searchable applicant name
or email) is the first thing `wbs:7.1` has to answer. Nothing below is worth building until it's answered.

---

## 0. Questions for Finance before any build

Ask the Revitalise finance contact (owner of OQ-015) these questions. Write each answer, with date and
name, into the `wbs:7.1` feasibility report.

| # | Question | Why it matters |
|---|---|---|
| F1 | Is it QuickBooks **Online**? Which region (UK)? | Desktop has no REST API. On Desktop, `wbs:7.4` (export fallback) is the route, not the Web Connector or a third-party driver |
| F2 | How is a grant payment recorded: as a Bill plus Bill Payment, an Expense (Purchase), or a Cheque? | Decides which entity the query reads |
| F3 | Is each holiday provider set up as a **Vendor**? Do the names match what Finance types in `rev_provider`? | The provider is the main match key for `wbs:7.2` |
| F4 | Where does the **grant reference** go: Reference no. (`DocNumber`), memo, line description, or a custom field? | Only some fields are filterable in a QBO query (see §3) |
| F5 | Are the **applicant's name or email** on the transaction at all? | Without them, the `CO-008` prior-grant check has no match key, and its re-price trigger fires |
| F6 | What does `rev_qboreference` hold: the transaction's `Id` or its `DocNumber`? | `ADR-088` mode 3 looks up by this value |
| F7 | Which QBO **admin** user will consent to the connection? Does a dedicated user for the service identity use up a paid QBO seat? | OAuth consent needs a QBO admin. The TAD has the service identity own every connection |
| F8 | Do TRIP or Donorfy records also need checking? | OQ-016. The connector doesn't reach them |

---

## 1. Create the Intuit app

1. Sign in at developer.intuit.com and create an app of type *QuickBooks Online and Payments*.
   **Create it under a Revitalise-owned Intuit account, not an Argelis one.** The app outlives the
   engagement and is part of handover.
2. Select one scope: `com.intuit.quickbooks.accounting`. Don't add Payments.
3. Note the **Client ID** and **Client Secret** for each key set. Treat both like any other secret: they
   go into Key Vault and the deployment settings, **never into this repository**.
   - **Development keys** work only with a sandbox company. They serve `dev` and `tst_acc` (see §2).
   - **Production keys** come after the app profile and Intuit's compliance questionnaire are finished.
     The questionnaire asks for a privacy policy URL and terms URL. Use Revitalise's own pages, and leave
     several days for this before the `prd` deploy.
4. Leave **Redirect URIs** empty for now. Each environment's connector generates its own value in step 2.
   Add one URI per environment; the Intuit app holds several.

---

## 2. Build the custom connector in the solution

Create it **in `dev`, inside the solution** (*Solutions → RevitaliseGrantAutomation → New → Automation →
Custom connector*), not under *My connectors*. A connector created outside a solution can't travel through
the pipeline.

### Environment variables

The values that differ per environment are environment variables. A solution custom connector accepts
them in **Host**, **Base URL**, **Client ID**, **Client Secret** and the auth URLs, using the syntax
`@environmentVariables("<schema name>")`. **They don't work inside actions.** The flow passes the realm
ID as a parameter.

| Variable (proposed) | Type | dev | tst_acc | prd |
|---|---|---|---|---|
| `rev_QboHost` | Text | `sandbox-quickbooks.api.intuit.com` | `sandbox-quickbooks.api.intuit.com` | `quickbooks.api.intuit.com` |
| `rev_QboClientId` | Text | development key | development key | production key |
| `rev_QboClientSecret` | **Secret** (Key Vault) | development key | development key | production key |
| `rev_QboRealmId` | Text | sandbox company ID | sandbox company ID | Revitalise company ID |

- **`tst_acc` uses the sandbox.** Under C-TECH-007, Tier 3 data never holds real values outside `prd`,
  and QBO returns payee names and amounts. So `wbs:7.3` ("test with known duplicates") seeds the sandbox
  with matching records. For `wbs:7.5` (walkthrough with Emily using real-world examples), decide whether
  it runs on seeded sandbox data or in `prd`. That decision belongs to the reviewer.
- A **Text** secret isn't encrypted. Use the Secret type backed by Key Vault, as §6.3 already does.
- The connector reads each value **when it is saved**. After an import sets a new value, re-save the
  connector in that environment. Add this as a `post_deploy` step in `config/<slug>-pipeline.yml`.
- Don't export a current value for the four variables. The import then asks for each environment's own
  value.

### General

- Host: `@environmentVariables("rev_QboHost")`
- Base URL: `/v3/company`
- Scheme: HTTPS

### Security: OAuth 2.0, Generic OAuth 2

- Client ID: `@environmentVariables("rev_QboClientId")`
- Client Secret: `@environmentVariables("rev_QboClientSecret")`
- Authorization URL: `https://appcenter.intuit.com/connect/oauth2`
- Token URL and Refresh URL: `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer`
- Scope: `com.intuit.quickbooks.accounting`

Save, then copy the generated **Redirect URL** into the Intuit app's Redirect URIs. Repeat after the
first import into `tst_acc` and into `prd`.

### Definition: GET only

| Operation id | Request | Used by |
|---|---|---|
| `GetCompanyInfo` | `GET /{realmId}/companyinfo/{realmId}?minorversion=75` | Connection test, keep-alive |
| `Query` | `GET /{realmId}/query?query={statement}&minorversion=75` | All three call sites |

- Send the header `Accept: application/json` on both operations.
- **Don't add a write operation, and don't add a generic "send HTTP request" action.** The connector
  has to stay read-only (BR-D04). A review of the connector's `apiDefinition` is part of `wbs:7.1`'s
  evidence.
- The Profit and Loss report in the generic version of this guide isn't needed for the grant process.
  It's left out.

### Test

1. Create a connection in `dev`. Sign in as the sandbox company's admin and consent.
2. Run `GetCompanyInfo`.
3. Run a `Query` against one of the entities Finance named in F2.

Record what each returned. That record is the first piece of evidence for `wbs:7.1`.

---

## 3. Use it in the flows

### What the QBO query language can and can't do

The query syntax looks like SQL but is much narrower. This decides the shape of the duplicate check:

- One entity per query. No joins and no `OR`.
- You can filter only on fields Intuit marks **filterable** in its entity reference. Typically that's
  `Id`, `DocNumber`, `TxnDate`, `VendorRef`, `MetaData.LastUpdatedTime`, and `DisplayName` on Vendor.
  **Memo (`PrivateNote`) and line descriptions are not filterable.** Confirm each field you need during
  `wbs:7.1`.
- `LIKE` works only with `%` wildcards, on a few name fields.
- Paginate with `STARTPOSITION` and `MAXRESULTS`, up to 1,000 rows per page.

So **"fuzzy matching" (`wbs:7.2`) happens in the flow, not in QuickBooks.** Narrow the set on the
server, then score the candidates in the flow.

### Duplicate-payment check (`wbs:7.2`)

1. **Trigger:** `rev_payment` row added. Get the Grant, its provider, and the holiday dates.
2. **Resolve the vendor:** `select Id, DisplayName from Vendor where DisplayName like '%<provider>%'`. No
   hit, or several hits, is a result in its own right. Record it as *check inconclusive*, not as *no
   duplicate*.
3. **Candidates:** for each vendor, run
   `select * from Bill where VendorRef = '<id>' and TxnDate >= '<start − n days>' and TxnDate <= '<end + n days>'`.
   Use whichever entity F2 named; if Finance uses more than one, query each. Read the window `n` from
   `rev_setting`, so Emily can tune it the way the other thresholds are tuned (ADR-076, ADR-079).
4. **Exact key:** if the grant reference is in `DocNumber` (F4), run a direct
   `where DocNumber = '<grant ref>'` lookup as well.
5. **Score in the flow:** same provider, overlapping dates, the grant reference appearing in the memo or
   lines, and a similar amount. Write the flag and the matched QBO reference onto the Payment row,
   **before issue**.

### Reading the response

Use **Parse JSON** on `QueryResponse`. **An empty result is `"QueryResponse": {}`, with no array key at
all.** It is not an empty array. Guard with `coalesce(body('Query')?['QueryResponse']?['Bill'], json('[]'))`.
Otherwise *no match* and *query failed* look the same, and the check reports a pass it never ran. This is
the same trap as the empty-value cases in `knowledge/technology/power-automate.md`.

### Errors and run history

- **A failed QBO call must not read as "no duplicate".** Set a distinct *check not run* state and alert
  the process owner. This follows the TAD's rule that no integration fails silently.
- **Turn on Secure inputs and Secure outputs on every QBO action.** Responses carry payee names and
  amounts (Tier 3), and run history is a log (`knowledge/technology/power-automate.md`).
- The connection reference is owned by the service identity, like every other connection in the
  solution. The QBO user behind it comes from F7.

---

## Things to know before committing

- **Licensing:** a custom connector is Premium. The solution already depends on Premium connectors
  (DocuSign, the Request trigger, AI Builder), so this adds no new licence class. Confirm that the
  service identity's licence covers the flows that use it. Check this against current Microsoft
  licensing, not from memory.
- **Intuit API fees:** under Intuit's App Partner Program, write calls are free, but read and query calls
  are metered beyond a free monthly allowance. This solution only reads. At about 1,000 applications a
  year (NFR-021), the volume should stay inside the free tier. Check Intuit's current limits before
  relying on that, and if fees apply, record them outside this repository.
- **Rate limits:** about 500 requests per minute per company. The grant process is nowhere near that.
- **Tokens:** refresh tokens rotate, and expire after about 100 days unused. Between application rounds,
  the flows can go quiet for longer than that. Add a weekly scheduled `GetCompanyInfo` call to keep the
  connection alive, and alert if it fails. Re-consenting needs the QBO admin from F7.
- **minorversion:** Intuit has retired the older minor versions. Pin `minorversion=75` or later, and
  review it when Intuit publishes release notes.
- **QuickBooks Desktop:** if F1 comes back *Desktop*, stop. There's no REST API. The contracted route is
  the `wbs:7.4` export fallback, not the Web Connector, an SDK, or a third-party driver with the
  on-premises data gateway. Those would be a change order.

---

## Next steps

1. **Finance** answers F1 to F8. That closes OQ-015, and F8 also answers OQ-016.
2. **`wbs:7.1`** runs this guide in `dev` against a sandbox company and produces the feasibility report.
3. **architect-agent** corrects TAD §4, §6.4 and ADR-017's wording (the three points above) and decides
   the environment variable names.
4. **commercial-agent** checks whether "build a custom connector and an Intuit app" still fits
   `wbs:7.1` as contracted ("connect the Power Automate QBO connector"). It also re-prices `CO-008` once
   F5 is answered, as that order's re-price trigger requires.

---

## Sources

- [Custom connectors overview (Microsoft Learn)](https://learn.microsoft.com/connectors/custom-connectors/)
- [Create a custom connector from scratch (Microsoft Learn)](https://learn.microsoft.com/connectors/custom-connectors/define-blank)
- [Use environment variables in solution custom connectors (Microsoft Learn)](https://learn.microsoft.com/connectors/custom-connectors/environment-variables)
- [Custom connector FAQ (Microsoft Learn)](https://learn.microsoft.com/connectors/custom-connectors/faq)
- [Power Automate connector list (Microsoft Learn)](https://learn.microsoft.com/connectors/connector-reference/connector-reference-powerautomate-connectors)
- [QuickBooks Online release notes (Intuit)](https://developers.intuit.com/app/developer/qbo/docs/release-notes/general-release-notes)
- [QuickBooks API pricing and the Intuit App Partner Program (Apideck)](https://www.apideck.com/blog/quickbooks-api-pricing-and-the-intuit-app-partner-program)
- [How much does the QuickBooks API cost in 2026 (Truto)](https://truto.one/blog/how-much-does-the-quickbooks-api-cost-2026-pricing-rate-limits/)
- [QuickBooks Online API integration guide (Knit)](https://getknit.dev/blog/quickbooks-online-api-integration-guide-in-depth)
