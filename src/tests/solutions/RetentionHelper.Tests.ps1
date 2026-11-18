<#
    Tests for `REV | Retention | Retention & Erasure Helper` (wbs:0.13, change order CO-011, TAD rev 33/34 sections 4.2
    and 5.12 to 5.12.4, ADR-088, ADR-089): five flow definitions, the rev_retentionlog table, the role privileges, the
    two settings keys, the SAR folder environment variable and (TAD rev 37, ADR-091) the protected-sender variable.

    TWO KINDS OF TEST. (1) The Python suite under src/tests/solutions/retention_helper/ reads the five definitions as
    values (read-only mode 3, no Dataverse delete in mode 1, one delete in mode 2, the periods held equal to
    dataverse.bulkDeleteJobs, rev_detail never from a case column, every content-carrying action secured) and RUNS them
    with the repository's WDL executor over in-memory stores. (2) The static tests below pin the solution-level pieces a
    later edit could silently drop.

    WHAT NEITHER CAN DO. Nothing here ran on the platform. A-ERA-1 to A-ERA-5, A-SAR-4, A-SAR-6 to A-SAR-14, A-RH-1 to
    A-RH-3 (docs/development/retention-erasure-helper-dev-summary.md section 10) stay open until the DEV run of TAD
    12.11/12.12; A-SAR-4, A-SAR-13 and A-SAR-14 close in the ADR-091 check.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    $script:Root = Get-SolutionRoot
    $script:Repo = Get-RepositoryRoot
    $script:Manifest = Get-Content (Join-Path $script:Root 'Other' 'Solution.xml') -Raw
    $script:Service = Get-Content (Join-Path $script:Root 'Roles' 'REV Service Automation' 'REV Service Automation.xml') -Raw
    $script:Admin = Get-Content (Join-Path $script:Root 'Roles' 'REV Admin' 'REV Admin.xml') -Raw
}

Describe 'REV | Retention | Retention & Erasure Helper - definitions read and executed' {
    It 'passes the Python suite (boundaries, periods, rev_detail, secure data, modes 1-3 and both children executed)' {
        $dir = Join-Path $PSScriptRoot 'retention_helper'
        $output = & python3 -m unittest discover -s $dir -p 'test_*.py' 2>&1
        $code = $LASTEXITCODE
        if ($code -ne 0) { Write-Host ($output | Out-String) }
        $code | Should -Be 0
        ($output | Out-String) | Should -Match 'OK'
    }
}

Describe 'REV | Retention | Retention & Erasure Helper - solution components (TAD 5.12.4)' {
    It 'declares the five flow definitions, the table and the SAR folder variable' {
        foreach ($n in 14..18) {
            $script:Manifest | Should -Match ('<RootComponent type="29" id="\{8f1c2a44-10' + $n + '-4b7a-9e21-0a1b2c3d4e' + $n + '\}" />')
        }
        $script:Manifest | Should -Match '<RootComponent type="1" schemaName="rev_retentionlog" behavior="0" />'
        $script:Manifest | Should -Match '<RootComponent type="380" schemaName="rev_SpoSarFolderUrl" />'
    }
    It 'makes the SAR folder variable required with no default (the import pane refuses a blank)' {
        $x = Get-Content (Join-Path $script:Root 'environmentvariabledefinitions' 'rev_SpoSarFolderUrl' 'environmentvariabledefinition.xml') -Raw
        $x | Should -Match '<isrequired>1</isrequired>'
        $x | Should -Not -Match '<defaultvalue>'
    }
    It 'ships the protected-sender variable NOT required, with no default, so every environment starts on option A (ADR-091 items 4 and 7)' {
        $script:Manifest | Should -Match '<RootComponent type="380" schemaName="rev_SarProtectedSender" />'
        $x = Get-Content (Join-Path $script:Root 'environmentvariabledefinitions' 'rev_SarProtectedSender' 'environmentvariabledefinition.xml') -Raw
        $x | Should -Match '<isrequired>0</isrequired>'
        $x | Should -Not -Match '<defaultvalue>'
        foreach ($pair in @(@('pac-import-tstacc.json', 'TSTACC'), @('pac-import-prd.json', 'PROD'))) {
            $j = Get-Content (Join-Path $script:Repo 'provisioning' 'deploymentSettings' $pair[0]) -Raw | ConvertFrom-Json
            $v = @($j.EnvironmentVariables | Where-Object { $_.SchemaName -eq 'rev_SarProtectedSender' })
            $v.Count | Should -Be 1
            $v[0].Value | Should -Be ('{{SAR_PROTECTED_SENDER_' + $pair[1] + '}}')
        }
    }
    It 'adds Retained (audit) as outcome 8 and keeps values 1 to 7 (TAD 5.12.3, rev 37 approval amendment)' {
        $o = Get-Content (Join-Path $script:Root 'OptionSets' 'rev_retentionoutcome.xml') -Raw
        $labels = 'Scheduled', 'Deleted', 'Not due', 'Overdue', 'Retained \(hold\)', 'Retained \(finance\)', 'Extract written', 'Retained \(audit\)'
        for ($i = 0; $i -lt $labels.Count; $i++) {
            $o | Should -Match ('<option value="{0}">\s*<labels>\s*<label description="{1}"' -f ($i + 1), $labels[$i])
        }
    }
    It 'ships the log table organisation-owned, audited and with no secured column (TAD 5.12.3)' {
        $e = Get-Content (Join-Path $script:Root 'Entities' 'rev_retentionlog' 'Entity.xml') -Raw
        $e | Should -Match '<OwnershipType>OrganizationOwned</OwnershipType>'
        $e | Should -Match '<IsAuditEnabled>1</IsAuditEnabled>\s*<IsRetrieveAuditEnabled>'
        $e | Should -Not -Match '<IsSecured>1</IsSecured>'
        $e | Should -Match '<AutoNumberFormat>RL-\{DATETIMEUTC:yyyy\}-\{SEQNUM:6\}</AutoNumberFormat>'
    }
}

Describe 'REV | Retention | Retention & Erasure Helper - privileges (TAD 5.12.4, section 12, A-ERA-2, A-SAR-11)' {
    It 'gives REV Service Automation create, read and update on the log, and never delete (decision D5)' {
        foreach ($v in 'Create', 'Read', 'Write') { $script:Service | Should -Match ('name="prv{0}rev_retentionlog"' -f $v) }
        $script:Service | Should -Not -Match 'name="prvDeleterev_retentionlog"'
        $script:Admin | Should -Match 'name="prvReadrev_retentionlog"'
        foreach ($v in 'Create', 'Write', 'Delete') { $script:Admin | Should -Not -Match ('name="prv{0}rev_retentionlog"' -f $v) }
    }
    It 'gives REV Service Automation delete on rev_applicant and its five cascade children' {
        foreach ($t in 'rev_applicant', 'rev_application', 'rev_review', 'rev_grant', 'rev_payment', 'rev_bankaccount') {
            $script:Service | Should -Match ('name="prvDelete{0}"' -f $t)
        }
    }
    It 'gives audit READ and never audit delete (C-DOM-012)' {
        $script:Service | Should -Match 'name="prvReadAuditSummary"'
        $script:Service | Should -Match 'name="prvReadRecordAuditHistory"'
        $script:Service | Should -Not -Match 'name="prvDeleteAudit'
    }
}

Describe 'REV | Retention | Retention & Erasure Helper - provisioning reaches the new table' {
    It 'is created by ensure-schema.ps1 before the import (C-TECH-050) with its systemuser lookup' {
        $h = Get-Content (Join-Path $script:Repo 'provisioning' 'dataverse' 'ensure-schema-helpers.psm1') -Raw
        $h | Should -Match "'rev_retentionlog'\)"
        $h | Should -Match "rev_startedby\s+=\s+'systemuser'"
    }
    It 'is switched on for auditing in every environment that declares audited tables' {
        foreach ($f in 'dev-auditing-settings.json', 'test-settings.json', 'prd-settings.json') {
            $j = Get-Content (Join-Path $script:Repo 'provisioning' 'deploymentSettings' $f) -Raw | ConvertFrom-Json
            $j.dataverse.auditing.auditedTables | Should -Contain 'rev_retentionlog'
        }
    }
    It 'is never in a bulk-delete job (decision D5: kept indefinitely)' {
        foreach ($f in 'test-settings.json', 'prd-settings.json') {
            $j = Get-Content (Join-Path $script:Repo 'provisioning' 'deploymentSettings' $f) -Raw | ConvertFrom-Json
            @($j.dataverse.bulkDeleteJobs | Where-Object { $_.entity -eq 'rev_retentionlog' }).Count | Should -Be 0
        }
    }
}

Describe 'REV | Retention | SAR extract - loop output read back through result() (TAD rev 38, ADR-092, A-SAR-16)' {
    # The shipped expressions of the Filters and Selects after mode 3's loops, evaluated by the PowerShell harness over
    # result() in the shape measured in DEV on 2026-11-04 (New-WdlForeachResult). The Python suite runs the whole flow;
    # this pins the second evaluator to the same shape (knowledge note: every platform throw lands in both evaluators).
    BeforeAll {
        Import-Module (Join-Path $PSScriptRoot '_harness' 'WdlExpression.psm1') -Force
        $path = Get-ChildItem (Join-Path $script:Root 'Workflows') -Filter 'REVRetentionSarExtract-*.json' | Where-Object { $_.Name -notlike '*.data.xml' }
        $script:Sar = (Get-Content $path.FullName -Raw | ConvertFrom-Json -AsHashtable).properties.definition.actions
        $script:Docs = $script:Sar['Copy_signed_documents']['actions']
        $script:Mail = $script:Sar['Read_service_mailbox']['actions']
    }

    It 'gathers one table per address from the per-iteration Compose outputs' {
        $loop = $script:Mail['For_each_mailbox_address']['actions'].Keys
        $res = New-WdlForeachResult -Children @($loop) -Iterations @(
            @{ Compose_mailbox_table = @{ inputs = '<table>a</table>'; outputs = '<table>a</table>' } },
            @{ Compose_mailbox_table = @{ inputs = '<table>b</table>'; outputs = '<table>b</table>' } })
        $kept = Invoke-WdlQuery -Inputs $script:Mail['Filter_mailbox_table_records']['inputs'] -Results @{ For_each_mailbox_address = $res }
        $kept.Count | Should -Be 1
        $kept[0]['name'] | Should -Be 'Compose_mailbox_table'
        $tables = Invoke-WdlSelect -Inputs $script:Mail['Select_mailbox_tables']['inputs'] -Outputs @{ Filter_mailbox_table_records = $kept }
        $tables | Should -Be @('<table>a</table>', '<table>b</table>')
    }

    It 'gathers every PDF copy from both loops as {Name, ContentBytes, Size}' {
        $lib = New-WdlForeachResult -Children @($script:Docs['For_each_library_copy']['actions'].Keys) -Iterations @(
            @{ Get_the_signed_pdf_content = @{ inputs = @{}; outputs = @{ statusCode = 200; headers = @{}; body = @{ '$content' = 'QQ==' } } }
               Save_the_signed_pdf_copy = @{ inputs = @{}; outputs = @{ statusCode = 200; headers = @{}; body = @{ Size = 1 } } }
               Compose_signed_pdf_attachment = @{ inputs = [ordered]@{ Name = 'x-signed-acceptance.pdf'; ContentBytes = 'QQ=='; Size = 1 }
                                                  outputs = [ordered]@{ Name = 'x-signed-acceptance.pdf'; ContentBytes = 'QQ=='; Size = 1 } } })
        $env = New-WdlForeachResult -Children @($script:Docs['For_each_envelope_copy']['actions'].Keys) -Iterations @()
        $libKept = Invoke-WdlQuery -Inputs $script:Docs['Filter_library_copy_records']['inputs'] -Results @{ For_each_library_copy = $lib }
        $envKept = Invoke-WdlQuery -Inputs $script:Docs['Filter_envelope_copy_records']['inputs'] -Results @{ For_each_envelope_copy = $env }
        $envKept.Count | Should -Be 0
        $copies = Invoke-WdlSelect -Inputs $script:Docs['Select_document_copies']['inputs'] `
            -Outputs @{ Filter_library_copy_records = $libKept; Filter_envelope_copy_records = $envKept }
        $copies.Count | Should -Be 1
        $copies[0]['Name'] | Should -Be 'x-signed-acceptance.pdf'
        $copies[0]['Size'] | Should -Be 1
    }

    It 'reads a section Compose that never ran as null, so the fixed Not read line is used' {
        (Invoke-WdlExpression -Value "@coalesce(actions('Compose_audit_section')?['outputs'], 'not read')") | Should -Be 'not read'
        (Invoke-WdlExpression -Value "@coalesce(actions('Compose_audit_section')?['outputs'], 'not read')" `
            -Actions @{ Compose_audit_section = @{ name = 'Compose_audit_section'; status = 'Succeeded'; outputs = '<h2>7.' } }) | Should -Be '<h2>7.'
    }
}
