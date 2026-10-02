
# Revitalise Design System

## What is Revitalise
Revitalise is a UK national charity providing respite grants to disabled adults and their family carers. Founded in 1963 as The Winged Fellowship Trust, renamed Revitalise in 1996, it delivered over 42,000 respite breaks through its own specialist holiday centres. In November 2024, rising costs and falling Local Authority/grant funding forced the closure of its centres (Jubilee Lodge, Sandpipers). The Trustees decided to relaunch Revitalise as a **grantmaker**: instead of running its own holidays, it now funds grants (up to £500/person for breaks, £100/person for day trips) so disabled people and carers can book respite themselves, in partnership with other providers.

Vision: *a society in which every disabled person and every carer is able to take the break or holiday they want.*
Purpose: to enable disabled people and their families to access and enjoy amazing holidays, breaks and experiences tailored to them, to escape, relax and have fun.
Values (2026 refresh): **inclusive, change-makers, caring, joyful, hardworking.**

Single product surface: the public website, **revitalise.org.uk** — informational/fundraising site with an application-for-funding flow, donations, case studies, FAQs, and an e-newsletter signup. No app or internal tool was provided.

## Sources
- `uploads/Item 6a - Revitalise Strategy.pptx` — Board strategy deck (Nov 2024–2026 relaunch plan). Used for organisational context, values, tone of the "who we are / what we do" copy, and grant-programme facts. Extracted text saved to `research/pptx_text.txt`; extracted media saved to `research/media/`.
- `uploads/Screenshot 2026-08-27 at 19.27.38.png` — revitalise.org.uk homepage (header, hero, intro copy, cookie banner).
- `uploads/Screenshot 2026-08-27 at 19.27.52.png` — revitalise.org.uk footer + "Receive Funding" band + newsletter signup form.
- `uploads/Screenshot 2026-08-27 at 19.30.18.png` — revitalise.org.uk FAQ page (accordion pattern).
- No Figma file, codebase, or GitHub repo was attached. **This design system was built from screenshots and the strategy deck only** — screenshots are lossy, so visual values here (exact spacing, radii, hover states) are best-effort reconstructions, not pixel-exact extraction. If a real codebase or Figma file for revitalise.org.uk becomes available, re-derive tokens from it.

## Content fundamentals
- **Voice:** warm, plain-spoken charity voice. Short declarative sentences. First-person plural ("we") describing the org, second person ("you") when addressing guests/donors is used sparingly — copy tends to describe guests in third person ("disabled people and their carers") more than direct "you" address.
- **Tone words from the brand's own values:** inclusive, change-making, caring, joyful, hardworking. Copy leans earnest and mission-first, not jokey — no emoji anywhere in site copy or the strategy deck.
- **Casing:** Title Case for nav items, headings and buttons ("What We Fund", "Apply Now", "Donate Today"). Body copy is standard sentence case.
- **Structure:** headline + one-line strapline + single primary CTA is the recurring pattern ("Revitalise — Funding vital respite for disabled people & carers — Apply Now"). FAQs use question-as-label accordions, not long-form prose.
- **Specific example (site hero):** "Revitalise Is A National Charity Providing Respite Grants To Disabled Adults And Their Family Carers" — Title Case even in a full sentence headline, a distinctive house style.
- **Specific example (strategy deck, values):** "We are joyful. Fun, warmth and laughter are at the heart of everything we do." — short, rhythmic, values stated then immediately made concrete.
- No slang, no exclamation-heavy copy. Numbers/facts (grant amounts, eligibility ages) are stated plainly and precisely.

## Visual foundations
- **Colour:** one saturated signature colour — a hot pink/magenta (`--pink-600 #E6027F`) — carries logo, all primary buttons, section banner backgrounds and link colour. It is used boldly and full-strength, not tinted down. A pale lavender (`--lavender-100 #EDE8F1`) appears as a secondary band background (e.g. "Receive Funding" section) — the only other tint used at page-background scale. Everything else is white/near-white surfaces with charcoal-grey text (`#5A5A5A` body, near-black headings). No secondary brand hue, no rainbow palette.
- **Type:** headlines are set in an elegant high-contrast serif (site uses something in the Playfair/Caslon family; substituted with **Playfair Display** — see Typography note below). Nav, buttons and UI chrome are sans-serif. The wordmark itself is a bespoke rounded hand-lettered script — that is a locked logo asset, never reset in a live font.
- **Backgrounds:** mostly flat white or pale-lavender bands; no gradients, no patterns/textures, no illustration style. Photography is full-bleed and warm/candid (real guests, real settings — parks, gardens), not styled stock. One large hero photo per page is typical, overlaid with a solid-pink text card rather than a text-on-image treatment.
- **Buttons:** solid pink fill, white bold text, generous horizontal padding, rounded-pill or large-radius corners. Secondary/tertiary actions appear as plain underlined pink text links rather than outline buttons.
- **Cards / panels:** minimal shadow, white surface, thin light-grey border or no border at all; the FAQ accordion uses a very light grey (`#F8F7F7`) row fill with a pink chevron. Corner radii are moderate (8–12px) — nothing pill-shaped except buttons/CTAs and the circular social icons.
- **Shadows:** very subtle, near-flat design; shadows (where present) are soft and low-contrast, not skeuomorphic.
- **Iconography:** simple, monochrome, circular social icons (Facebook, Instagram, LinkedIn) filled solid pink with white glyphs — the only icon usage visible in source material. No custom icon font or SVG icon set was found in the provided sources. See Iconography section.
- **Motion:** no animation was observable in static screenshots; standard web conventions (fast, subtle hover states) are assumed. Hover states are assumed to be a darker pink (`--pink-700`) based on typical solid-fill button conventions — not directly confirmed from a static screenshot.
- **Transparency/blur:** none observed.
- **Layout:** conventional charity-site structure — sticky-feeling top utility bar (social icons), logo-left header with two pill CTA buttons and search, horizontal nav, full-bleed hero with an overlaid pink content card, three-column footer (Explore / Legal / newsletter signup card), cookie-consent banner bottom-left (CookieYes-branded, third-party).

### Typography note — font substitution flagged
No webfont files were included in any source. The real site fonts could not be identified with certainty from screenshots alone.
- Headings substituted with **Playfair Display** (nearest Google Fonts match to the elegant serif seen in headlines/FAQ titles).
- Body/UI substituted with **Nunito Sans** (a warm, rounded, friendly sans that echoes the rounded logo lettering).
**Please share the real brand font files (or a link to the live site's font-face rules) so these can be swapped for the authentic typefaces.**

## Iconography
- Only icons found in source material: three solid-pink circular social icons (Facebook, Instagram, LinkedIn) in the site header/footer.
- No icon font, SVG sprite, or icon library was found in the provided materials (the pptx's own clip-art icons — money, committee, rocket — are generic PowerPoint/stock clip-art used only inside the strategy deck, not part of the live site's visual system, and were **not** copied in).
- No emoji used anywhere in site copy or the strategy deck.
- **Substitution:** the `Badge`/`SocialIcon` component uses inline Simple Icons–style glyphs (brand glyphs only, no CDN dependency) recreating the three social marks seen in the screenshots, styled with the brand's solid-pink-circle treatment. Flagged as a substitution — replace with the real SVGs if available.
- No logo mark exists separate from the wordmark — Revitalise's "logo" *is* its hand-lettered wordmark (`assets/logo/`). Do not draw a substitute mark.

## Assets copied in
- `assets/logo/revitalise-logo.png` — wordmark, transparent background.
- `assets/logo/revitalise-logo-tagline-serif.png` — wordmark + serif tagline lockup ("We're the people who create revitalising holidays...").
- `assets/logo/revitalise-logo-tagline-sans.png` — wordmark + sans-serif strapline lockup ("Funding vital respite for disabled people & carers").
- `assets/photography/guests-icecream.jpeg`, `assets/photography/guests-group-garden.jpeg` — real guest/volunteer photography from the strategy deck, representative of the brand's warm candid photography style.

## Index
- `styles.css` — root stylesheet, imports everything under `tokens/`.
- `tokens/colors.css`, `typography.css`, `spacing.css`, `effects.css`, `fonts.css` — design tokens.
- `guidelines/` — specimen cards for the Design System tab (Colors, Type, Spacing, Brand groups).
- `components/core/` — Button.
- `components/forms/` — Input, Checkbox, NewsletterForm.
- `components/content/` — Card, Accordion (FAQ), Badge (social icon).
- `components/navigation/` — Navbar, Footer.
- `components/feedback/` — CookieBanner, Notice.

### Components
Button, Input, Checkbox, Radio, NewsletterForm, Card, Accordion, Badge, StatTile, Navbar, Footer, CookieBanner, Notice. No Figma/codebase component inventory was available, so this is a standard set sized to what revitalise.org.uk actually shows (see Visual foundations) rather than a full enumerated source inventory.

## Trustee Review Portal redesign notes
`ui_kits/trustee-review-portal/` restyles the Power Platform Code App (`Argelis-XVL/Revitalise`, "REV Trustee Review Portal") to fit this design system. The current app (see screenshots in `uploads/`) already uses the correct logo and pink primary buttons, but drifts from the brand in several places — this redesign fixes:
1. **Headings** — the app sets bold navy-blue sans-serif headings; the brand has no navy in its palette and always sets headings in the display serif. Redesign uses Playfair Display in `--text-heading` (near-black), never navy.
2. **Secondary buttons** — the app's "Refresh figures" / "Back to the list" buttons are navy-outlined; redesign uses the DS `Button variant="secondary"` (pink outline), consistent with the one accent colour rule.
3. **Status/explanation panels** — "Round figures are unavailable", "narrative withheld", "no staff recommendation" all use a grey box with a dark-grey left border, an accent-border-card pattern the design system's own guidance avoids. Redesigned as the new flat `Notice` component (rounded, tinted, no left bar).
4. **Stat figures** — plain stacked text is replaced with the new `StatTile` card (serif value + muted label) for scannability, matching the Card/StatTile visual language used elsewhere.
5. **Verdict radios** — already pink-accented in the source app (kept), formalised as the reusable `Radio` component.
The Power Apps platform chrome (top black toolbar, Share/Settings icons) is platform-owned, out of scope for brand restyling.
- `ui_kits/marketing-site/` — click-through recreation of revitalise.org.uk (home, FAQ, funding/apply band).
- `ui_kits/trustee-review-portal/` — redesign of the Power Platform Code App (REV Trustee Review Portal) restyled to the design system.
- `SKILL.md` — portable skill definition for use in Claude Code.

## Caveats / open questions for the user
1. No Figma or codebase was attached — everything here is reconstructed from 3 screenshots + a strategy pptx. Please attach the live site's codebase or a Figma file if pixel-accurate values matter.
2. Real webfonts are unknown — Playfair Display / Nunito Sans are placeholders. Please send the actual font files or the site's font-face CSS.
3. Hover/press/focus states, exact button radii, and exact spacing scale are inferred from static screenshots, not measured from live CSS.
4. Only 3 pages of the live site were seen (home, footer, FAQ) — other pages (About Us, What We Fund, Support Us, Case Studies, Apply Now form) were not visible, so the UI kit's coverage of those views is a best-effort extrapolation of the established style, not a recreation of unseen screens.
