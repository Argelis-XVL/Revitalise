# Skill: How to Estimate Effort

Used by: `plan-agent`

---

## Approach

Use a **T-shirt sizing** model for high-level estimates in the SDD.
Use **story points** or **hours** if the team has a calibrated velocity.

| Size | Typical Effort | Indicators |
|---|---|---|
| XS | < 1 day | Single config change, copy edit, minor UI tweak |
| S | 1–3 days | Single new field/endpoint, simple form, small script |
| M | 3–8 days | New feature with UI + logic + data model |
| L | 2–4 weeks | Multi-component feature with integrations |
| XL | > 4 weeks | Platform-level change; should be broken into smaller items |

---

## Estimation Checklist

For each work item, consider:

- [ ] Data model changes (schema migrations, new entities)
- [ ] Backend / service logic
- [ ] UI / frontend changes
- [ ] Automation / workflow design
- [ ] Integration with external systems
- [ ] Security controls
- [ ] Unit tests
- [ ] Integration / E2E tests
- [ ] Documentation (TAD, Dev Summary, runbook)
- [ ] Deployment and configuration
- [ ] Accessibility compliance
- [ ] Regulatory / compliance verification

---

## Complexity Multipliers

Apply a multiplier to your base estimate when:

| Factor | Multiplier |
|---|---|
| First time using this technology | 1.5× |
| Integration with a poorly-documented external system | 1.5× |
| Strict regulatory compliance required | 1.25× |
| High security classification (PII, financial, medical) | 1.25× |
| Unclear requirements (open questions remain) | 1.5× |
| Tight deadline / change-freeze constraints | 1.25× |

---

## Presenting Estimates

Always express estimates as a **range**, not a single number:
> "Estimated effort: M (3–8 days), most likely 5 days assuming no integration blockers."

State assumptions explicitly:
> "This estimate assumes the external API has a working sandbox environment available."

Flag uncertainty:
> "⚠️ Open question OQ-002 must be resolved before this estimate can be confirmed."
