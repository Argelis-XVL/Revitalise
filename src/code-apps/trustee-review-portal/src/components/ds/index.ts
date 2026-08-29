/**
 * The design-system component surface — ADR-033, ADR-034.
 *
 * Consumers import from `components/ds`, never from a component file directly. The design
 * system's own adherence lint asks for exactly this (`_adherence.oxlintrc.json` →
 * "Import design-system components from 'index.js', not component internals") and it costs one
 * file.
 *
 * SEVEN COMPONENTS, AND SIX DELIBERATELY ABSENT ONES. `Accordion`, `Badge`, `Navbar`, `Footer`,
 * `CookieBanner` and `NewsletterForm` are NOT converted (§2.1.2): no screen in this app renders
 * an accordion, a social icon, a marketing navbar, a site footer, a cookie banner or a
 * newsletter form, and converting a component nothing renders is dead code that still has to be
 * maintained, audited and counted in the coverage denominator (A-R41). The conversion procedure
 * is in ADR-034 and unchanged if a later pass needs one.
 *
 * FLUENT UI v9 IS NOT REPLACED, AND THAT IS NOT HALF-HEARTEDNESS (§2.1.4). The design system
 * ships no spinner, no dialog, no toast, no select, and no accessible table or chart — precisely
 * the components whose value is focus management, ARIA wiring and keyboard behaviour, and
 * precisely the parts a prototype kit reconstructed from screenshots does not have.
 * `FluentProvider`, `theme.ts`, `Spinner`, `Dialog`, `Toast`, `Field`, `Label`, `RadioGroup`,
 * `Select` and `Textarea` all stay.
 *
 * `classNames` is intentionally not re-exported: the barrel is the component surface, and that
 * helper is an internal detail of the conversion.
 */
export { Button } from "./Button";
export type { ButtonProps, ButtonSize, ButtonVariant } from "./Button";

export { Card } from "./Card";
export type { CardProps } from "./Card";

export { Checkbox } from "./Checkbox";
export type { CheckboxProps } from "./Checkbox";

export { Input } from "./Input";
export type { InputProps } from "./Input";

export { Notice } from "./Notice";
export type { NoticeProps, NoticeTone } from "./Notice";

export { Radio } from "./Radio";
export type { RadioProps } from "./Radio";

export { StatTile } from "./StatTile";
export type { StatTileProps } from "./StatTile";
