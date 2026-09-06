# Skill: Accessibility Checklist

Used by: `architect-agent`, `development-agent`, `test-agent`

Standard: **WCAG 2.1 Level AA**
Apply to every new or modified UI screen, form, component, or modal.

---

## 1. Perceivable

### 1.1 Text Alternatives
- [ ] All non-text content (images, icons, charts) has a meaningful `alt` attribute
- [ ] Decorative images use `alt=""` (empty) so they are skipped by screen readers
- [ ] Complex images (charts, diagrams) have a long-text description nearby

### 1.2 Time-Based Media
- [ ] Video content has accurate captions
- [ ] Audio-only content has a text transcript

### 1.3 Adaptable
- [ ] Page structure uses semantic HTML / ARIA landmarks (`main`, `nav`, `header`, `footer`, `region`)
- [ ] Reading and interaction order is logical when CSS is removed
- [ ] Instructions do not rely solely on shape, colour, or position ("click the green button on the right")
- [ ] Portrait/landscape orientation is not restricted without necessity

### 1.4 Distinguishable
- [ ] Colour is never the only means of conveying information (e.g. error states also have text/icon)
- [ ] Text colour contrast ratio ≥ 4.5:1 for normal text; ≥ 3:1 for large text (18pt / 14pt bold)
- [ ] UI component and graphic contrast ≥ 3:1 against adjacent colours
- [ ] Text can be resized to 200% without loss of content or functionality
- [ ] No text is rendered as an image (except logos)
- [ ] Content does not require horizontal scrolling at 320px wide
- [ ] **Every font file shipped has a WEB-EMBEDDING licence, checked separately from the desktop one.** An Office / Microsoft 365 bundled font (Aptos, Segoe UI) is licensed for **device install and document embedding**, not for a site to serve — the web-serving right is a separate commercial SKU, and nothing in a brand guide distinguishes the two, so *"the brand font is X"* reads as an implementable instruction when the implementable part is only the font-stack **name**. The compliant, zero-cost default is **name-only in the CSS stack with a full system fallback chain**: the viewer's own installed copy is used where present and nothing is served. **Record the substitution rather than making it silently**, because the rendered result differs per device — which is also a contrast-checking consideration, since the face you measured may not be the face that renders (`IMP-0354`)

### 1.4a Adopting an externally supplied palette or design system

**A supplied brand asset is an INPUT, not an audited one.** Added 2026-08-28 (`IMP-0385`), after
the design system supplied for this project was measured pair by pair and found non-compliant.

- [ ] **Compute every text/background and every UI-graphic pair yourself, before adoption.**
      Contrast is a property of **pairs**, and a palette can be authored — legitimately — without
      any pair ever being computed. The Revitalise design system says so in its own
      `readme.md:18`: *"best-effort reconstructions, not pixel-exact extraction."*
- [ ] **Record each ratio beside the value that ships it**, in the stylesheet, so a later change
      cannot quietly undo the measurement. `src/theme.ts`'s header is the pattern.
- [ ] **Check specifically for a REMOVED FOCUS INDICATOR.** `outline: 'none'` with no replacement
      is a WCAG 2.4.7 failure outright, not a contrast miss, and it survives every contrast audit
      because it is not a contrast problem.
- [ ] **Count the surfaces, not just the page background.** A token that passes on white can fail
      on a band or tint the same design system defines.

What the measurement found, as the worked example — every figure from the supplied tokens:

| Pair | Measured | Floor |
|---|---|---|
| white on `--brand-primary` `#e6027f` (every primary button label) | 4.49 | 4.5 |
| `--link-default` `#e6027f` on white (every link) | 4.49 | 4.5 |
| `--text-muted` `#8a8a8a` on white → on `--surface-band` `#ede8f1` | 3.45 → **2.86** | 4.5, and below even 3.0 |
| `--success` `#3a8a52` on white (latent — no component uses it yet) | 4.25 | 4.5 |
| `--focus-ring` `#ec4ea3` on three of the system's own six surfaces | 2.82–2.94 | 3.0 |
| `--border-default` `#e0dede` vs white, serving as the `Input` border | 1.34 | 3.0 |

**Four text pairings failed by 0.01 to 1.05, and 0.01 is still a fail.** The same defect class had
already been found once on this project, in Fluent's own defaults for the supplied ramp, where
white on `brand[80]` measured 4.22. The fix both times was to **route the colour through the
supplied 16-shade ramp** rather than invent a darker tint — a three-shade brand ramp cannot supply
an AA-clean rest/hover/active ladder at all.

**One half of this is now mechanical:** `scripts/verify-design-doc-claims.py` check (b) recomputes
every contrast ratio a design document's table row states from the hex values that row itself
names. The rest of this section is not, and will not be — a gate for a removed focus indicator
would have to read CSS-in-JS props across a component tree, and this project has one supplied
design system.

---

## 2. Operable

### 2.1 Keyboard Accessible
- [ ] All interactive elements are reachable by keyboard (Tab / Shift+Tab)
- [ ] All interactive elements are operable by keyboard (Enter, Space, arrow keys as appropriate)
- [ ] No keyboard traps — focus never gets stuck
- [ ] Keyboard shortcuts do not conflict with browser/OS shortcuts

### 2.2 Enough Time
- [ ] Time limits can be turned off, adjusted, or extended (unless essential)
- [ ] Auto-updating content can be paused or stopped

### 2.3 Seizures and Physical Reactions
- [ ] No content flashes more than 3 times per second

### 2.4 Navigable
- [ ] Descriptive, unique `<title>` on every page / view
- [ ] Focus order is logical and matches reading order
- [ ] Focus is visible — keyboard focus indicator is clearly visible (do not remove `:focus` outline)
- [ ] Links and buttons have descriptive labels — not "click here" or "read more"
- [ ] Headings (`h1`–`h6`) form a logical hierarchy; `h1` is unique per page
- [ ] Skip navigation link is present on pages with repeated navigation blocks

### 2.5 Input Modalities
- [ ] Pointer gestures (swipe, drag) have a single-pointer alternative
- [ ] Click/tap targets are at least 44×44 CSS pixels

---

## 3. Understandable

### 3.1 Readable
- [ ] Page language is declared (`<html lang="en">`)
- [ ] Sections in a different language are marked with `lang` attribute

### 3.2 Predictable
- [ ] Focus does not trigger unexpected context changes
- [ ] Input does not auto-submit or auto-navigate without warning

### 3.3 Input Assistance
- [ ] Form inputs have a visible, associated label (not placeholder text only)
- [ ] Required fields are indicated (not by colour alone)
- [ ] Input errors are identified in text — clearly describe what went wrong
- [ ] Error suggestions are provided where possible
- [ ] For legal/financial/data-deletion actions: confirmation step or undo mechanism is present

---

## 4. Robust

### 4.1 Compatible
- [ ] HTML is valid and well-formed (run through a validator)
- [ ] All interactive components have correct ARIA roles, states, and properties
- [ ] Status messages are announced to screen readers via `aria-live` regions

---

## Testing Approach

| Method | Tool |
|---|---|
| Automated scan | axe-core, Lighthouse, or equivalent |
| Keyboard navigation | Manual walk-through — no mouse |
| Screen reader | NVDA+Chrome (Windows), VoiceOver+Safari (Mac/iOS), TalkBack (Android) |
| Colour contrast | Colour Contrast Analyser or browser dev tools |
| Zoom test | Browser zoom to 200%, 400% |
| Mobile | Resize to 320px wide; test on real device or emulator |

Automated tools catch ~30–40% of issues. Manual testing is required.

---

## Reporting Failures

In the Test Report, record accessibility failures as:

| ID | WCAG Criterion | Component | Severity | Description |
|---|---|---|---|---|
| A-001 | 1.4.3 Contrast | Login button | P2 | Contrast ratio 2.8:1; fails 4.5:1 threshold |

---

## When a customer instruction conflicts with a success criterion

**Every other conflicting-input class in this system has a route. This one had none.** A constraint
is HARD or SOFT; a scope change goes to `commercial-agent` as a change order; a platform guess goes
to `skills/how-to-verify-a-platform-contract.md`. A legitimate, explicit styling instruction that
would delete accessible content resolved to whatever the agent holding the keyboard decided — and
it resolved **invisibly**, because both wrong answers are one-line diffs.

`IMP-0567` is the worked example. The instruction was *"every chart renders a data table
underneath it; only the chart itself should be shown."* Executed literally, it deletes the
`<table>` that `components/DistributionChart.tsx` documents as its own WCAG 1.1.1 text alternative
and 1.3.1 structured content, for every distribution on the round-statistics screen. The dispatch
happened to spot it. Nothing in the repository made that likely.

The route, in three steps:

1. **Name the criterion, and name the component's own documented claim to satisfy it.** Not "this
   might be an accessibility problem" — the criterion number, and the comment or doc line where
   the component says it is the thing satisfying it. If no such claim exists, this section does not
   apply and the instruction is just an instruction.
2. **Look for the interpretation that satisfies the instruction VISUALLY and the criterion
   STRUCTURALLY.** These are usually both available, because the instruction is nearly always
   about what is *seen*. Prefer visually-hidden-in-the-DOM over any disclosure that **unmounts**
   content: a collapsed `<details>` or a conditionally-rendered branch removes the alternative from
   assistive technology exactly as deletion does, while looking like a compromise.
3. **Report it to the approval gate as an INTERPRETATION, never as a completed instruction.** One
   line naming what was asked, what was done, and which criterion forced the difference. The
   reviewer may still want the literal thing; that is their call to make, and they cannot make it
   from a summary that says "done".

**Do not silently narrow the ask instead.** Quietly implementing less than was requested and
reporting it as complete is the same defect as deleting the content, minus the audit trail.

**Deliberately not a gate.** No gate reads a reviewer instruction — a dispatch instruction is a
Task-tool prompt, never a file (`IMP-0470`), so there is nothing for a script to open. The gap was
in this skill's own text, which is where a route lives.
