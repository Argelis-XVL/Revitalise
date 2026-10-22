<#
.SYNOPSIS
    Creates/verifies the recurring Dataverse bulk-delete jobs that enforce the
    feature's retention schedule.

.DESCRIPTION
    Per-environment script — a `post_deploy` step behind each environment's gate in
    config/<slug>-pipeline.yml ("Create/verify the recurring bulk-delete retention
    jobs"). Implements the retention schedule of C-DOM-003 / ADR-004 and the derived
    orphan sweep identified in TAD §3.4 gap 1.

    A bulk-delete job is environment state, not solution content — it cannot be
    packaged — so it is provisioned here. One job per entry in settings key
    `dataverse.bulkDeleteJobs`; each entry names the job, the table, the recurrence
    pattern and (where the rule has one) the retention period, so no period is ever a
    literal in this script.

    The six jobs (TAD section 3.4.1, ADR-083), in the order they run:
      - Paid-grant applications   - deleted 72 months (6 years) after the grant's
                                    rev_finalpaymentdate; the cascade removes Review,
                                    Grant and Payment. TST/ACC and PRD.
      - Rejected applications     - a fixed period after rev_decisiondate
      - Withdrawn/incomplete      - a fixed period after the parent applicant's
                                    rev_lastcontactdate
      - Orphaned applicants       - applicants left with no application at all; runs
                                    after every application sweep
      - Error log                 - a fixed number of days after rev_occurredon
      - AI events (msdyn_aievent) - AI Builder's own copy of each call's input text,
                                    deleted 30 days after createdon, DAILY. PRD ONLY:
                                    DEV and TST/ACC hold test text, so their settings
                                    files carry no entry for it (ADR-083 item 2).
    Which job runs where is decided by the entries in each environment's settings
    file, not by this script: it creates exactly the entries it is given.

    Request shape (D-ADR083-2 / D-ADR083-3, measured in DEV 2026-10-22): every condition
    value is a typed Microsoft.Dynamics.CRM.Object (New-Int32Value), and the existence
    check selects only columns that bulkdeleteoperation has and reads the recurrence
    pattern through $expand=asyncoperationid (D-ADR083-4).

    Idempotency (C-TECH-042): a recurring bulk-delete job leaves one
    `bulkdeleteoperation` row per past occurrence in statecode 3 (Completed) plus one
    row for the occurrence still to come, which is not Completed. Looking for a row
    with the job's name and `statecode ne 3` therefore finds the pending occurrence of
    an already-provisioned job and nothing else, which makes it a safe existence check
    that neither duplicates jobs on a pipeline retry nor mistakes finished history for
    a live schedule.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS). Creating bulk-delete jobs requires an application user with
    the Bulk Delete privilege (System Administrator in practice).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per job and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json. For this feature `test` IS
    the combined TST/ACC environment (TAD ADR-006) and `acc` is never used.

.NOTES
    Job names are the idempotency key, so they must be stable: they deliberately do
    NOT encode the retention period, because changing a period would then create a
    second job while the first kept running. Names are ASCII-only because they are
    used inside an OData $filter in a request URI.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-bulk-delete-jobs.ps1 -Env prd
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# rev_applicationstatus option values — src/solutions/RevitaliseGrantAutomation/
# OptionSets/rev_applicationstatus.xml. Kept here rather than in settings because
# they are solution content, not per-environment configuration.
$statusRejected   = 8
$statusWithdrawn  = 9
$statusIncomplete = 10
$statusGrantPaid  = 11

function New-Int32Value {
    <#
      Types one ConditionExpression value. The BulkDelete action binds `Values` as
      Collection(Edm.Untyped) and DROPS a bare JSON number, so the condition arrives with
      zero values and the platform refuses it (0x80040203 "requires 1 value/s, not 0",
      D-ADR083-2). Each value is therefore sent as a typed Microsoft.Dynamics.CRM.Object;
      this exact shape is what DEV accepted on 2026-10-22 for every option-set and
      OlderThanX value used below (all are Int32; the string form of Value is the wire
      format, not a mistake).
    #>
    param([Parameter(Mandatory)][int]$Value)
    return @{
        '@odata.type' = 'Microsoft.Dynamics.CRM.Object'
        Type          = 'System.Int32'
        Value         = [string]$Value
    }
}

function New-RetentionQuerySet {
    <#
      Returns the `QuerySet` value for one retention job.

      The BulkDelete action does NOT take FetchXML: `QuerySet` is
      Collection(mscrm.QueryExpression), so each job's criteria are built here as the
      JSON projection of a QueryExpression — EntityName, ColumnSet, Criteria
      (FilterExpression with Conditions/FilterOperator) and LinkEntities — with the
      @odata.type annotation each complex type needs to bind.

      Every date test uses a RELATIVE date operator (OlderThanXMonths /
      OlderThanXDays) instead of an absolute cut-off computed at creation time. That
      is what keeps a recurring job correct: an absolute date would be frozen at the
      moment the job was provisioned and the job would delete the same shrinking set
      forever, whereas a relative operator is re-evaluated on every occurrence.
    #>
    param(
        [Parameter(Mandatory)][string]$JobKey,
        [int]$RetentionValue
    )

    $emptyFilter = @{
        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
        FilterOperator = 'And'
        Conditions     = @()
    }

    switch ($JobKey) {

        # Rejected applications: retention runs from the decision date, which is the
        # point at which the charity's purpose for holding the application ended.
        'rejectedApplications' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'rev_application'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('rev_applicationid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'rev_status'
                                Operator      = 'Equal'
                                Values        = @(New-Int32Value $statusRejected)
                            },
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'rev_decisiondate'
                                Operator      = 'OlderThanXMonths'
                                Values        = @(New-Int32Value $RetentionValue)
                            }
                        )
                    }
                    LinkEntities  = @()
                }
            )
        }

        # Withdrawn / incomplete applications: the retention clock is the APPLICANT's
        # rev_lastcontactdate, not a column on the application, so the query joins to
        # the parent applicant and puts the date test in LinkCriteria. QueryExpression
        # supports this directly; if a future org version rejects a link-entity
        # criterion in a bulk-delete job, the documented fallback is to test
        # rev_submittedon on the application instead — which is an APPROXIMATION,
        # because a withdrawn application can have been re-contacted long after it was
        # submitted, and would have to be recorded as such before being adopted.
        'withdrawnIncompleteApplications' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'rev_application'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('rev_applicationid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'rev_status'
                                Operator      = 'In'
                                Values        = @((New-Int32Value $statusWithdrawn), (New-Int32Value $statusIncomplete))
                            }
                        )
                    }
                    LinkEntities  = @(
                        @{
                            '@odata.type'         = 'Microsoft.Dynamics.CRM.LinkEntity'
                            LinkFromEntityName    = 'rev_application'
                            LinkFromAttributeName = 'rev_applicantid'
                            LinkToEntityName      = 'rev_applicant'
                            LinkToAttributeName   = 'rev_applicantid'
                            JoinOperator          = 'Inner'
                            EntityAlias           = 'parentapplicant'
                            Columns               = @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                                AllColumns    = $false
                                Columns       = @()
                            }
                            LinkCriteria          = @{
                                '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                                FilterOperator = 'And'
                                Conditions     = @(
                                    @{
                                        '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                        AttributeName = 'rev_lastcontactdate'
                                        Operator      = 'OlderThanXMonths'
                                        Values        = @(New-Int32Value $RetentionValue)
                                    }
                                )
                            }
                            LinkEntities          = @()
                        }
                    )
                }
            )
        }

        # Orphaned applicants (the derived sweep): an applicant whose last application
        # has already been deleted by one of the jobs above has no remaining purpose,
        # so it carries no retention period of its own — it inherits the period of
        # whichever job removed the last child. Expressed as an outer join to
        # rev_application plus a null test on the child key, which is the
        # QueryExpression equivalent of a FetchXML link-entity with
        # link-type="outer" and a null condition on the aliased child column.
        'orphanedApplicants' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'rev_applicant'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('rev_applicantid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                EntityName    = 'childapplication'   # the outer-joined alias
                                AttributeName = 'rev_applicationid'
                                Operator      = 'Null'
                            }
                        )
                    }
                    LinkEntities  = @(
                        @{
                            '@odata.type'         = 'Microsoft.Dynamics.CRM.LinkEntity'
                            LinkFromEntityName    = 'rev_applicant'
                            LinkFromAttributeName = 'rev_applicantid'
                            LinkToEntityName      = 'rev_application'
                            LinkToAttributeName   = 'rev_applicantid'
                            JoinOperator          = 'LeftOuter'
                            EntityAlias           = 'childapplication'
                            Columns               = @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                                AllColumns    = $false
                                Columns       = @('rev_applicationid')
                            }
                            LinkCriteria          = $emptyFilter
                            LinkEntities          = @()
                        }
                    )
                }
            )
        }

        # Error log: retention in DAYS from the moment the error happened. Error rows
        # never contain personal data (C-DOM-004), so the period is an operational
        # one, not a data-protection one.
        'errorLog' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'rev_errorlog'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('rev_errorlogid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'rev_occurredon'
                                Operator      = 'OlderThanXDays'
                                Values        = @(New-Int32Value $RetentionValue)
                            }
                        )
                    }
                    LinkEntities  = @()
                }
            )
        }

        # Paid-grant applications (ADR-083 item 1): the clock is the GRANT's
        # rev_finalpaymentdate, a column on a related row, so the query starts at the
        # application (the row the schedule deletes: deleting the grant alone would
        # leave the application and its narratives behind) and joins to rev_grant with
        # the date test in LinkCriteria, the same shape as the withdrawn/incomplete
        # branch. The cascade from Application removes Review, Grant and Payment; the
        # orphan sweep then removes the applicant. An application at Grant Paid with no
        # grant row, or a grant with no final payment date, matches nothing and is kept.
        # A-RET-1: not yet run against a live environment.
        'paidGrantApplications' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'rev_application'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('rev_applicationid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'rev_status'
                                Operator      = 'Equal'
                                Values        = @(New-Int32Value $statusGrantPaid)
                            }
                        )
                    }
                    LinkEntities  = @(
                        @{
                            '@odata.type'         = 'Microsoft.Dynamics.CRM.LinkEntity'
                            LinkFromEntityName    = 'rev_application'
                            LinkFromAttributeName = 'rev_applicationid'
                            LinkToEntityName      = 'rev_grant'
                            LinkToAttributeName   = 'rev_applicationid'
                            JoinOperator          = 'Inner'
                            EntityAlias           = 'paidgrant'
                            Columns               = @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                                AllColumns    = $false
                                Columns       = @()
                            }
                            LinkCriteria          = @{
                                '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                                FilterOperator = 'And'
                                Conditions     = @(
                                    @{
                                        '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                        AttributeName = 'rev_finalpaymentdate'
                                        Operator      = 'OlderThanXMonths'
                                        Values        = @(New-Int32Value $RetentionValue)
                                    }
                                )
                            }
                            LinkEntities          = @()
                        }
                    )
                }
            )
        }

        # AI events (ADR-083 item 2): AI Builder writes one msdyn_aievent row per call,
        # holding the call's input text. One condition, no status test: every row is a
        # call's input. Daily, so a row is gone at most 31 days after it was written.
        # A-NS-45: no application role can read these rows (verification, ADR-083 item 4).
        # A-NS-46: whether deleting rows changes Microsoft's credit reporting is not stated.
        # msdyn_aieventid as the primary key follows the platform's <table>id naming; it is
        # part of A-NS-47's check (the first PRD run reports CREATED or FAILED).
        # A-NS-47: Microsoft documents this job in the admin center wizard, not through
        # the BulkDelete action; if the action refuses it, the job is created by hand to
        # the same criteria and the next run of this script reports it EXISTS by name.
        'aiEvents' {
            return @(
                @{
                    '@odata.type' = 'Microsoft.Dynamics.CRM.QueryExpression'
                    EntityName    = 'msdyn_aievent'
                    ColumnSet     = @{
                        '@odata.type' = 'Microsoft.Dynamics.CRM.ColumnSet'
                        AllColumns    = $false
                        Columns       = @('msdyn_aieventid')
                    }
                    Criteria      = @{
                        '@odata.type'  = 'Microsoft.Dynamics.CRM.FilterExpression'
                        FilterOperator = 'And'
                        Conditions     = @(
                            @{
                                '@odata.type' = 'Microsoft.Dynamics.CRM.ConditionExpression'
                                AttributeName = 'createdon'
                                Operator      = 'OlderThanXDays'
                                Values        = @(New-Int32Value $RetentionValue)
                            }
                        )
                    }
                    LinkEntities  = @()
                }
            )
        }

        default {
            throw ("Unknown bulk-delete jobKey '$JobKey'. Add a branch to " +
                   'New-RetentionQuerySet in this script before adding the job to ' +
                   'dataverse.bulkDeleteJobs in the settings file.')
        }
    }
}

$settings = Get-ProvisioningSettings -Env $Env
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$jobs = Get-Setting -Settings $settings -Path 'dataverse.bulkDeleteJobs'

foreach ($jobDef in @($jobs)) {
    $jobName = Get-Setting -Settings $jobDef -Path 'name'
    $label   = "Bulk-delete job '$jobName'"
    try {
        $jobKey            = Get-Setting -Settings $jobDef -Path 'jobKey'
        $recurrencePattern = Get-Setting -Settings $jobDef -Path 'recurrencePattern'
        $startTimeUtc      = Get-Setting -Settings $jobDef -Path 'startTimeUtc'

        # Retention value is optional: the orphan sweep has no period of its own.
        $retentionValue = 0
        $retentionRaw   = Get-Setting -Settings $jobDef -Path 'retentionValue' -Optional
        if ($null -ne $retentionRaw) { $retentionValue = [int]$retentionRaw }

        # ── Existence check — see .DESCRIPTION for why `statecode ne 3` ───────
        # $select names only columns bulkdeleteoperation has (D-ADR083-3): it has no
        # `recurrencepattern` (DEV refused it with 0x80060888). The pattern lives on the
        # related asyncoperation, read through $expand=asyncoperationid(...), which DEV
        # accepted read-only on 2026-10-22 (D-ADR083-4). The $expand's own $select is
        # inside the parentheses and is not a second top-level $select.
        $existing = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('bulkdeleteoperations?$filter=name eq ''{0}'' and statecode ne 3&$select=bulkdeleteoperationid,name,statecode,isrecurring,nextrun&$expand=asyncoperationid($select=recurrencepattern)' -f (ConvertTo-ODataLiteral -Value $jobName))
        if ($existing.value -and $existing.value.Count -gt 0) {
            $live = $existing.value[0]
            $livePattern = $null
            if ($live.PSObject.Properties['asyncoperationid'] -and $live.asyncoperationid -and
                $live.asyncoperationid.PSObject.Properties['recurrencepattern']) {
                $livePattern = $live.asyncoperationid.recurrencepattern
            }
            # Schedule drift: the job exists, so this script must not create a second
            # one, but its schedule no longer matches settings. Surfaced in the
            # Deployment Summary for the process owner to reconcile.
            if ($live.isrecurring -eq $false) {
                Write-ResourceStatus -Status EXISTS -Name $label `
                    -Detail ('⚠ schedule drift: the live job is not recurring, settings say ' +
                             "'$recurrencePattern' - delete the job in the maker portal and re-run this script to re-provision it")
            }
            elseif ($livePattern -ne $recurrencePattern) {
                Write-ResourceStatus -Status EXISTS -Name $label `
                    -Detail ("⚠ recurrence drift: live '$livePattern' vs settings '$recurrencePattern' - " +
                             'delete the job in the maker portal and re-run this script to re-provision it')
            }
            else {
                Write-ResourceStatus -Status EXISTS -Name $label
            }
            continue
        }

        # ── Create ───────────────────────────────────────────────────────────
        # First occurrence is the next `startTimeUtc` that has not passed yet. Jobs
        # are staggered in settings so the application sweeps finish before the
        # orphan sweep looks for applicants without applications.
        $timeParts = @($startTimeUtc -split ':')
        if ($timeParts.Count -ne 2) {
            throw "startTimeUtc '$startTimeUtc' is not in HH:mm format"
        }
        $start = [datetime]::UtcNow.Date.AddHours([int]$timeParts[0]).AddMinutes([int]$timeParts[1])
        if ($start -le [datetime]::UtcNow) { $start = $start.AddDays(1) }

        $body = @{
            QuerySet              = @(New-RetentionQuerySet -JobKey $jobKey -RetentionValue $retentionValue)
            JobName               = $jobName
            SendEmailNotification = $false      # failures surface through rev_errorlog + the Failure Alert flow, not mail
            ToRecipients          = @()
            CCRecipients          = @()
            RecurrencePattern     = $recurrencePattern   # RFC 2445, e.g. FREQ=MONTHLY;INTERVAL=1
            StartDateTime         = $start.ToString('yyyy-MM-ddTHH:mm:ssZ')
        }
        Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
            -Path 'BulkDelete' -Body $body | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label `
            -Detail "$recurrencePattern, first run $($start.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

Exit-Provisioning
