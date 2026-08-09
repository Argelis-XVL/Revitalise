# sharepoint/templates/

Versioned PnP site templates (XML) — the **source of truth** for each site's structure
(document libraries, content types, site columns, views). `ensure-site.ps1` applies the
template named in `sharepoint.site.templateFile` of `deploymentSettings/<env>-settings.json`
via `Invoke-PnPSiteTemplate` on every run, which is idempotent by design: change the site
by editing the template here and re-running the pipeline step, never by clicking in the
site itself. One template per site purpose (e.g. `casedocs-template.xml`), committed to
git and reviewed like code; `verify-sharepoint.ps1` asserts the template's libraries
(settings key `expectedLibraries`) exist after application.
