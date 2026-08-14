<#
    Contract tests over EVERY script under provisioning/.

    provisioning/README.md § Script Contract states five numbered rules and C-TECH-042
    makes them enforceable. Until now they were verified by a human reading the scripts —
    which is how test-agent's Provisioning layer had to do it, and why its verdict was
    "PASS (source review)" rather than "PASS". These tests assert the rules mechanically,
    from the abstract syntax tree rather than by grepping text, so a comment mentioning
    New-MgGroup cannot make a verify-* script look mutating and a real call cannot hide.

    The value of a contract suite is that it covers scripts nobody has written yet: add a
    script to provisioning/ that breaches the contract and this file fails, without anyone
    remembering to write a test for it. The Phase 1 behavioural tests are in
    EntraScripts.Tests.ps1 and DataverseScripts.Tests.ps1.
#>

BeforeDiscovery {
    $harnessPath = Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1'
    Import-Module $harnessPath -Force
    $repoRoot         = Get-RepoRoot
    $provisioningRoot = Join-Path $repoRoot 'provisioning'

    # Discovery-time data so each script gets its own named test case in the output.
    $script:AllScripts = Get-ChildItem -Path $provisioningRoot -Recurse -Filter '*.ps1' |
        Sort-Object FullName |
        ForEach-Object {
            $relative = $_.FullName.Substring($provisioningRoot.Length).TrimStart([IO.Path]::DirectorySeparatorChar, '/', '\')
            [pscustomobject]@{
                Name       = $_.Name
                FullName   = $_.FullName
                Relative   = ($relative -replace '\\', '/')
                Area       = (Split-Path -Leaf (Split-Path -Parent $_.FullName))
                IsCommon   = ($_.Name -eq 'provisioning-common.ps1')
                IsVerify   = ($_.Name -like 'verify-*')
            }
        }

    $script:EntryScripts   = @($script:AllScripts | Where-Object { -not $_.IsCommon })
    $script:MutatingScripts = @($script:EntryScripts | Where-Object { -not $_.IsVerify })
    $script:VerifyScripts   = @($script:EntryScripts | Where-Object { $_.IsVerify })

    # provisioning/README.md's Script Contract section names this ONE script exempt from
    # rules 1 (idempotent check-before-create) and 4 (-Env): it mints a local cryptographic
    # artifact via .NET APIs, not a tenant resource looked up via Graph, so there is no
    # -Env-scoped settings file to check-before-create against — regenerating is a rare,
    # deliberate, human-triggered rotation, never a pipeline retry.
    $script:EnvContractScripts = @($script:EntryScripts | Where-Object { $_.Name -ne 'create-self-signed-cert.ps1' })
}

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    $script:RepoRoot         = Get-RepoRoot
    $script:ProvisioningRoot = Join-Path $script:RepoRoot 'provisioning'

    # Rebuilt for the RUN phase. BeforeDiscovery's variables exist only during discovery,
    # so a test body that read $script:AllScripts would silently iterate nothing and pass
    # vacuously — which is exactly the failure mode a test suite must not have.
    $script:ScriptFiles = @(
        Get-ChildItem -Path $script:ProvisioningRoot -Recurse -Filter '*.ps1' | Sort-Object FullName
    )

    function Get-ScriptAst {
        param([Parameter(Mandatory)][string]$Path)
        $errors = $null
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$null, [ref]$errors)
        return [pscustomobject]@{ Ast = $ast; Errors = @($errors) }
    }

    function Get-InvokedCommandNames {
        param([Parameter(Mandatory)]$Ast)
        $commands = $Ast.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true)
        return @($commands | ForEach-Object { $_.GetCommandName() } | Where-Object { $_ } | Sort-Object -Unique)
    }

    function Get-InvokedParameterNames {
        param([Parameter(Mandatory)]$Ast, [Parameter(Mandatory)][string[]]$ForCommands)
        $result = [System.Collections.Generic.List[string]]::new()
        $commands = $Ast.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true)
        foreach ($command in $commands) {
            $name = $command.GetCommandName()
            if (-not $name -or $ForCommands -notcontains $name) { continue }
            foreach ($element in $command.CommandElements) {
                if ($element -is [System.Management.Automation.Language.CommandParameterAst]) {
                    $result.Add($element.ParameterName)
                }
            }
        }
        return @($result | Sort-Object -Unique)
    }
}

Describe 'Every provisioning script parses' {
    It '<_.Relative> parses with zero syntax errors' -ForEach $script:AllScripts {
        $parsed = Get-ScriptAst -Path $_.FullName
        $reason = (@($parsed.Errors) | ForEach-Object { $_.Message }) -join '; '
        @($parsed.Errors).Count | Should -Be 0 -Because $reason
        $parsed.Ast | Should -Not -BeNullOrEmpty
    }
}

Describe 'Script contract — provisioning/README.md rule 4 (the -Env parameter)' {
    It '<_.Relative> declares -Env as mandatory with the four-value ValidateSet' -ForEach $script:EnvContractScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        $paramBlock = $ast.ParamBlock
        $paramBlock | Should -Not -BeNullOrEmpty -Because 'the contract requires -Env <dev|test|acc|prd>'

        $envParam = $paramBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'Env' }
        $envParam | Should -Not -BeNullOrEmpty

        $attributeText = ($envParam.Attributes | ForEach-Object { $_.Extent.Text }) -join ' '
        $attributeText | Should -Match 'Mandatory'
        $attributeText | Should -Match 'ValidateSet'
        foreach ($value in @('dev', 'test', 'acc', 'prd')) {
            $attributeText | Should -Match "'$value'"
        }
        $envParam.StaticType.Name | Should -Be 'String'
    }

    It '<_.Relative> resolves per-environment values from settings, never a hardcoded environment URL (C-TECH-047)' -ForEach $script:EntryScripts {
        $text = Get-Content -Path $_.FullName -Raw
        # Comment lines are stripped first: several scripts legitimately cite a Microsoft
        # Learn URL or an example crm URL in their help block.
        $code = ($text -split "`n" | Where-Object { $_ -notmatch '^\s*#' }) -join "`n"
        $code | Should -Not -Match 'https://[a-z0-9-]+\.crm[0-9]*\.dynamics\.com'
        $code | Should -Not -Match '(?i)@revitalise\.org'
    }
}

Describe 'Script contract — shared implementation and safety defaults' {
    It '<_.Relative> requires PowerShell 7' -ForEach $script:AllScripts {
        Get-Content -Path $_.FullName -Raw | Should -Match '#Requires\s+-Version\s+7'
    }

    It '<_.Relative> sets StrictMode Latest and stops on error' -ForEach $script:AllScripts {
        $text = Get-Content -Path $_.FullName -Raw
        $text | Should -Match "Set-StrictMode\s+-Version\s+Latest"
        $text | Should -Match "\`$ErrorActionPreference\s*=\s*'Stop'"
    }

    It '<_.Relative> dot-sources common/provisioning-common.ps1 rather than reimplementing the contract' -ForEach $script:EntryScripts {
        Get-Content -Path $_.FullName -Raw | Should -Match "provisioning-common\.ps1"
    }

    It '<_.Relative> carries comment-based help with a SYNOPSIS' -ForEach $script:AllScripts {
        $text = Get-Content -Path $_.FullName -Raw
        $text | Should -Match '\.SYNOPSIS'
    }

    It '<_.Relative> ends by calling Exit-Provisioning, so the exit code reflects the failure count (rule 3)' -ForEach $script:EntryScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        Get-InvokedCommandNames -Ast $ast | Should -Contain 'Exit-Provisioning'
        # And it is the last statement, not merely present somewhere.
        $statements = $ast.EndBlock.Statements
        $statements[-1].Extent.Text.Trim() | Should -Be 'Exit-Provisioning'
    }

    It '<_.Relative> contains no work-in-progress marker (C-TECH-011)' -ForEach $script:AllScripts {
        # The three tokens are ASSEMBLED rather than written out. C-TECH-011 is also checked
        # by a repository-wide grep, and a test file that spelled the words would trip that
        # grep on itself — a false positive in the gate this test exists to support.
        $markers = @(('TO' + 'DO'), ('FIX' + 'ME'), ('HA' + 'CK'))
        $pattern = '\b(' + ($markers -join '|') + ')\b'
        Get-Content -Path $_.FullName -Raw | Should -Not -Match $pattern
    }

    It '<_.Relative> hardcodes no secret, credential or token (C-TECH-001)' -ForEach $script:AllScripts {
        $text = Get-Content -Path $_.FullName -Raw
        if ($_.Name -ne 'create-self-signed-cert.ps1') {
            # create-self-signed-cert.ps1 is the one script that legitimately calls
            # ConvertTo-SecureString: it wraps a PASSWORD IT JUST RANDOM-GENERATED
            # (RandomNumberGenerator]::Fill, never a hardcoded literal) so it can export a
            # password-protected .pfx. This exact regex cannot distinguish "converting a
            # hardcoded string" from "converting a freshly random one" — the distinction
            # is checked directly below instead of by exemption alone.
            $text | Should -Not -Match '(?i)ConvertTo-SecureString'
        }
        $text | Should -Not -Match '(?i)-ClientSecret\b'
        $text | Should -Not -Match '(?i)client_secret\s*='
        $text | Should -Not -Match '(?i)(password|apikey|api_key)\s*=\s*[''"][^''"]+[''"]'
    }

    It 'create-self-signed-cert.ps1''s ConvertTo-SecureString call wraps a random-generated value, never a literal' {
        $path = Join-Path (Get-RepoRoot) 'provisioning' 'entra' 'create-self-signed-cert.ps1'
        $text = Get-Content -Path $path -Raw
        $text | Should -Match '(?i)ConvertTo-SecureString\s+-String\s+\$generatedPassword\b' `
            -Because 'the argument must be the variable holding the random-generated bytes, never a string literal'
        $text | Should -Match '(?i)RandomNumberGenerator\]::Fill' `
            -Because 'confirms $generatedPassword is actually random, not just named to look like it'
    }
}

Describe 'Script contract — rule 2, the three-state status line' {
    It '<_.Relative> reports CREATED, EXISTS and FAILED' -ForEach $script:MutatingScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        Get-InvokedCommandNames -Ast $ast | Should -Contain 'Write-ResourceStatus'

        $text = Get-Content -Path $_.FullName -Raw
        # EXISTS is the interesting one: a script can only report it if it checked before
        # creating, so its presence is the mechanical proxy for rule 1 (idempotency).
        $text | Should -Match '-Status\s+CREATED'
        $text | Should -Match '-Status\s+EXISTS'
        $text | Should -Match '-Status\s+FAILED'
    }

    It '<_.Relative> reports PASS/FAIL and never CREATED/EXISTS/FAILED' -ForEach $script:VerifyScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        $invoked = Get-InvokedCommandNames -Ast $ast
        $invoked | Should -Contain 'Write-CheckResult'
        $invoked | Should -Not -Contain 'Write-ResourceStatus' -Because 'a read-only script creates nothing, so the resource-status contract does not apply to it'
    }
}

Describe 'Script contract — verify-* scripts are read-only' {
    # This is the assertion that stops a verification script quietly acquiring a side
    # effect. verify-* scripts are reused as pipeline smoke tests and by the test-agent, so
    # a mutation hidden in one would run against PRD after every deployment.
    It '<_.Relative> invokes no mutating Graph, PnP or PowerApps command' -ForEach $script:VerifyScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        foreach ($command in (Get-InvokedCommandNames -Ast $ast)) {
            $command | Should -Not -Match '^(New|Set|Remove|Add|Update|Grant)-(Mg|PnP|Admin|PowerApps)' `
                -Because "$($_.Relative) must not change anything"
        }
    }

    It '<_.Relative> issues no write against the Dataverse Web API' -ForEach $script:VerifyScripts {
        $ast = (Get-ScriptAst -Path $_.FullName).Ast
        $commands = $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true)
        foreach ($command in $commands) {
            if ($command.GetCommandName() -ne 'Invoke-DataverseApi') { continue }
            $elements = $command.CommandElements
            for ($i = 0; $i -lt $elements.Count; $i++) {
                if ($elements[$i] -is [System.Management.Automation.Language.CommandParameterAst] -and
                    $elements[$i].ParameterName -eq 'Method') {
                    $value = $elements[$i].Argument
                    if ($null -eq $value -and ($i + 1) -lt $elements.Count) { $value = $elements[$i + 1] }
                    "$($value.Extent.Text)" | Should -Match '(?i)^GET$' -Because 'a verify script only reads'
                }
            }
        }
    }

    It 'verify-intake-endpoint-auth.ps1 is the one read-only-by-effect exception, and says so' {
        # It sends an HTTP POST — that is the C-TECH-006 `Verify By` and cannot be done any
        # other way. What it must not do is touch Dataverse or Graph, and it must explain
        # why the POST writes nothing. Both are asserted here so the exception stays narrow.
        $path = Get-ProvisioningScriptPath -RelativePath 'entra/verify-intake-endpoint-auth.ps1'
        $ast  = (Get-ScriptAst -Path $path).Ast
        $invoked = Get-InvokedCommandNames -Ast $ast

        $invoked | Should -Contain 'Invoke-WebRequest'
        $invoked | Should -Not -Contain 'Invoke-DataverseApi'
        $invoked | Should -Not -Contain 'Invoke-RestMethod'
        foreach ($command in $invoked) {
            $command | Should -Not -Match '^(New|Set|Remove|Add|Update|Get)-Mg'
        }

        $text = Get-Content -Path $path -Raw
        $text | Should -Match '(?s)WHY THIS IS SAFE TO RUN AGAINST PRD'
        $text | Should -Match 'SkipHttpErrorCheck' -Because 'the status code must be read, not thrown on'
    }
}

Describe 'Script contract — the settings-file contract holds both ways' {
    It 'every settings path a Phase 1 script reads exists in test-settings.json and prd-settings.json' {
        # The failure this catches is the expensive one: a script that reads a key nobody
        # added, discovered at deploy time behind a gate. Only the scripts the Phase 1
        # pipeline actually invokes are in scope — sharepoint/ and teams/ are later phases
        # and their settings blocks are deliberately absent (see _comment_omitted_blocks).
        $phase1 = @(
            'entra/ensure-app-registration.ps1', 'entra/ensure-groups.ps1',
            'entra/grant-admin-consent.ps1', 'entra/verify-entra.ps1',
            'entra/ensure-intake-client.ps1', 'entra/verify-intake-endpoint-auth.ps1',
            'dataverse/bind-roles-to-groups.ps1', 'dataverse/ensure-group-teams.ps1',
            'dataverse/ensure-column-security-profile-members.ps1', 'dataverse/ensure-auditing.ps1',
            'dataverse/ensure-bulk-delete-jobs.ps1', 'dataverse/seed-settings.ps1',
            'dataverse/share-apps.ps1', 'dataverse/verify-role-bindings.ps1'
        )
        $settings = @{
            test = (Get-Content (Join-Path $script:ProvisioningRoot 'deploymentSettings' 'test-settings.json') -Raw | ConvertFrom-Json)
            prd  = (Get-Content (Join-Path $script:ProvisioningRoot 'deploymentSettings' 'prd-settings.json')  -Raw | ConvertFrom-Json)
        }

        $missing = [System.Collections.Generic.List[string]]::new()
        foreach ($relative in $phase1) {
            $path = Get-ProvisioningScriptPath -RelativePath $relative
            $text = Get-Content -Path $path -Raw
            # Only the calls made against the whole settings object; nested Get-Setting
            # calls take a sub-object and their paths are relative to it.
            $paths = [regex]::Matches($text, "Get-Setting\s+-Settings\s+\`$settings\s+-Path\s+'([^']+)'") |
                ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
            foreach ($settingPath in $paths) {
                # An -Optional read is allowed to be absent by definition.
                if ($text -match ([regex]::Escape("-Path '$settingPath'") + "\s+-Optional")) { continue }
                foreach ($env in $settings.Keys) {
                    $current = $settings[$env]
                    foreach ($segment in ($settingPath -split '\.')) {
                        if ($null -eq $current -or -not ($current.PSObject.Properties.Name -contains $segment)) {
                            $missing.Add("$relative reads '$settingPath' — absent from $env-settings.json")
                            $current = $null
                            break
                        }
                        $current = $current.$segment
                    }
                }
            }
        }
        $missing | Should -BeNullOrEmpty -Because ($missing -join '; ')
    }
}

Describe 'Test harness completeness — the fakes must keep up with provisioning/' {
    # If the harness silently falls behind, the behavioural tests stop covering what they
    # claim to. These two tests make that impossible to miss.
    It 'every external Graph / PnP / MSAL / PowerApps command used in provisioning/ has a fake' {
        $faked = @()
        foreach ($module in (Get-FakeModuleMap).Keys) { $faked += (Get-FakeModuleMap)[$module] }

        $used = [System.Collections.Generic.List[string]]::new()
        foreach ($file in $script:ScriptFiles) {
            $ast = (Get-ScriptAst -Path $file.FullName).Ast
            foreach ($command in (Get-InvokedCommandNames -Ast $ast)) {
                if ($command -match '^(Connect|Get|New|Set|Remove|Add|Update|Invoke|Grant)-(Mg|PnP|Msal|Admin|PowerApps)') {
                    $used.Add($command)
                }
            }
        }
        $used = @($used | Sort-Object -Unique)
        $used.Count | Should -BeGreaterThan 20 -Because 'provisioning/ demonstrably calls more than twenty external commands; a low count means this test is iterating nothing'
        foreach ($command in $used) {
            $faked | Should -Contain $command -Because 'ProvisioningTestHarness.psm1 FakeModuleMap must list it'
        }
    }

    It 'every named parameter passed to a faked command is declared on the fakes' {
        $faked = @()
        foreach ($module in (Get-FakeModuleMap).Keys) { $faked += (Get-FakeModuleMap)[$module] }
        $declared = Get-FakeParameterNames

        $used = [System.Collections.Generic.List[string]]::new()
        foreach ($file in $script:ScriptFiles) {
            $ast = (Get-ScriptAst -Path $file.FullName).Ast
            foreach ($name in (Get-InvokedParameterNames -Ast $ast -ForCommands $faked)) { $used.Add($name) }
        }
        # Common parameters come free from [CmdletBinding()] on the fakes.
        $common = [System.Management.Automation.PSCmdlet]::CommonParameters +
                  [System.Management.Automation.PSCmdlet]::OptionalCommonParameters
        $used = @($used | Sort-Object -Unique | Where-Object { $common -notcontains $_ })
        $used.Count | Should -BeGreaterThan 20 -Because 'a low count means this test is iterating nothing'
        foreach ($name in $used) {
            $declared | Should -Contain $name `
                -Because 'an undeclared parameter binds into $Rest and silently breaks every Should -Invoke -ParameterFilter assertion'
        }
    }
}

Describe 'provisioning/README.md stays in step with the directory' {
    It '<_.Relative> appears in the README script inventory' -ForEach $script:AllScripts {
        $readme = Get-Content -Path (Join-Path $script:ProvisioningRoot 'README.md') -Raw
        $readme | Should -Match ([regex]::Escape($_.Name))
    }
}
