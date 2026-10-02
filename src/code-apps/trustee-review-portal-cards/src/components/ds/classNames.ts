/**
 * Join CSS-Module class names, dropping the ones that are absent.
 *
 * WHY THIS EXISTS RATHER THAN A TEMPLATE LITERAL. Vite types a CSS Module as
 * `{ readonly [key: string]: string }` (`node_modules/vite/client.d.ts:4`), which is an INDEX
 * SIGNATURE — and `tsconfig.json` sets `noUncheckedIndexedAccess`, so `styles.button` has type
 * `string | undefined`, not `string`. A template literal would therefore interpolate the word
 * "undefined" into a `class` attribute the moment a class name is renamed in the stylesheet and
 * not in the component. This filters instead, and returns `undefined` rather than an empty
 * string when nothing survives, so a component never emits a bare `class=""`.
 *
 * It is the same reason the variant maps in `Button.tsx` and `Notice.tsx` are declared
 * `Record<Variant, string | undefined>` rather than the `Record<Variant, string>` TAD §2.1.3
 * names — see those files.
 *
 * Not exported from `index.ts`: the barrel is the design-system COMPONENT surface, and this is
 * an internal detail of the conversion.
 */
export function classNames(
  ...parts: (string | false | null | undefined)[]
): string | undefined {
  const kept = parts.filter((part): part is string => typeof part === "string" && part !== "");
  return kept.length === 0 ? undefined : kept.join(" ");
}
