# Skill: How to Estimate Effort

Used by: `plan-agent`

---

## When a contracted baseline exists, it IS the estimate

**Read this before estimating anything on this project.** `contract/wbs.json` carries 61 tasks with
low/high hours, and WBS v0.5 is the customer-accepted Agreed Specification (Build Terms B1, decision
D-5). So:

- For work covered by an accepted WBS task, the estimate **is** that task's range. Do not re-derive
  it, and do not restate it in a document — cite the baseline (`C-COM-008`). `IMP-0029`: the approved
  SDD §10 stated 106–160 hours over 7 automations against a signed 292 over 9, and every downstream
  document inherited the error.
- **Do not re-estimate downward because AI assistance makes the work faster.** D-6: estimates stay at
  the WBS figures, capacity is 16 h/week physical, and actuals are expected well below. A large
  negative delta is the planned outcome, not evidence the estimate was wrong.
- The T-shirt model below applies only to work **no accepted task covers** — which by definition is a
  change-order candidate, so size it and route it to `commercial-agent` before building it.

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
