// Shared primitives mirroring src/components/Panel.tsx (Panel, Definitions, StateMessage, StatTileRow) + mock data.
const { Notice: _Notice, StatTile: _StatTile, Button: _DSButton, Radio: _Radio } = window.RevitaliseDesignSystem_a4dff3;
// Kit-scoped button: DS Button + gradient/shadow treatment from index.html (.rv-btn).
function PButton({ variant = 'primary', className, ...rest }) {
  return <_DSButton variant={variant} className={['rv-btn', 'rv-btn-' + variant, className].filter(Boolean).join(' ')} {...rest} />;
}
const _Button = PButton;

const h2Style = { fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', color: 'var(--text-heading)', margin: '0 0 var(--space-4)' };
const h3Style = { fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-heading)', margin: 0 };

const RV = { purple: '#49345b', purpleFaded: '#6a5774', teal: '#14adbb', tealTint: '#e7f6f8' };

function Eyebrow({ children, color = 'var(--brand-primary)' }) {
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: color }}></span>{children}</span>;
}

function Panel({ heading, eyebrow, eyebrowColor, children }) {
  return (
    <section className="rv-card rv-lift" style={{ padding: 'var(--space-8)', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {eyebrow && <Eyebrow color={eyebrowColor}>{eyebrow}</Eyebrow>}
        <h2 style={{ ...h2Style, margin: 0 }}>{heading}</h2>
      </div>
      {children}
    </section>
  );
}

// Hero band — same treatment as the Round overview's round header.
function HeroBand({ badgeLabel, badgeValue, eyebrow, heading, children }) {
  return (
    <section className="rv-card" style={{ borderRadius: '20px', padding: 'var(--space-8)', background: 'linear-gradient(135deg, var(--lavender-100) 0%, var(--pink-50) 100%)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-8)', alignItems: 'center' }}>
      <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: 'var(--white)', boxShadow: '0 6px 20px rgba(73,52,91,.14)', display: 'grid', placeItems: 'center', textAlign: 'center', flex: 'none' }}>
        <div>
          <div style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: RV.purple }}>{badgeLabel}</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: String(badgeValue).length > 3 ? '30px' : '46px', lineHeight: 1.05, color: 'var(--brand-primary)' }}>{badgeValue}</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', flex: '1 1 320px', minWidth: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <Eyebrow color={RV.purple}>{eyebrow}</Eyebrow>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', color: 'var(--text-heading)', margin: 0 }}>{heading}</h2>
        </div>
        {children}
      </div>
    </section>
  );
}

function FactChips({ items }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
      {items.map(([label, value]) => (
        <span key={label} style={{ display: 'inline-flex', flexDirection: 'column', gap: '2px', background: 'rgba(255,255,255,.85)', borderRadius: '12px', padding: '8px 14px', boxShadow: '0 1px 3px rgba(73,52,91,.08)' }}>
          <span style={{ fontSize: '12px', color: 'var(--ink-600)' }}>{label}</span>
          <span style={{ fontWeight: 700, color: 'var(--text-heading)', fontSize: 'var(--text-sm)' }}>{value}</span>
        </span>
      ))}
    </div>
  );
}

const STATUS_TONES = {
  'Eligible for Panel': ['var(--pink-50)', 'var(--pink-800)', 'var(--brand-primary)'],
  'Under Review': ['var(--lavender-100)', RV.purple, RV.purple],
  'Borderline': [RV.tealTint, '#00505a', RV.teal],
  'Auto-reject': ['var(--grey-100)', 'var(--ink-700)', 'var(--ink-400)'],
};
function StatusPill({ status }) {
  const [bg, fg, dot] = STATUS_TONES[status] || STATUS_TONES['Auto-reject'];
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: bg, color: fg, fontWeight: 700, fontSize: '13px', borderRadius: '999px', padding: '4px 12px 4px 10px', whiteSpace: 'nowrap' }}><span style={{ width: '7px', height: '7px', borderRadius: '50%', background: dot }}></span>{status}</span>;
}
function ScoreChip({ score, max = 60 }) {
  if (score == null) return <span style={{ fontStyle: 'italic', color: 'var(--ink-600)', fontSize: 'var(--text-sm)' }}>Not scored</span>;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', justifyContent: 'flex-end' }}>
      <span style={{ width: '56px', height: '6px', borderRadius: '999px', background: 'var(--grey-100)', overflow: 'hidden' }}><span style={{ display: 'block', height: '100%', width: `${(score / max) * 100}%`, borderRadius: '999px', background: `linear-gradient(90deg, ${RV.purple}, var(--brand-primary))` }}></span></span>
      <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-heading)', minWidth: '24px', textAlign: 'right' }}>{score}</span>
    </span>
  );
}
function Definitions({ items }) {
  return (
    <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 'var(--space-3)', margin: 0 }}>
      {items.map((i) => {
        const absent = ABSENT.includes(i.value);
        return (
          <div key={i.label} style={{ borderRadius: '14px', padding: 'var(--space-4) var(--space-5)', background: absent ? 'transparent' : 'var(--grey-50)', border: absent ? '1.5px dashed var(--grey-200)' : '1.5px solid transparent', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <dt style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>{i.label}</dt>
            <dd style={{ margin: 0, color: absent ? 'var(--ink-600)' : 'var(--text-heading)', fontWeight: absent ? 400 : 700, fontStyle: absent ? 'italic' : 'normal', fontSize: 'var(--text-base)' }}>{i.value}</dd>
          </div>
        );
      })}
    </dl>
  );
}
function StateMessage({ heading, explanation }) {
  return (
    <div role="note" style={{ borderRadius: '14px', border: '1.5px dashed var(--lavender-200)', background: 'linear-gradient(135deg, rgba(237,232,241,.5), rgba(253,241,248,.5))', padding: 'var(--space-5) var(--space-6)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <p style={{ margin: 0, fontWeight: 700, color: 'var(--text-heading)' }}>{heading}</p>
      <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--ink-700)', textWrap: 'pretty' }}>{explanation}</p>
    </div>
  );
}
// Selectable verdict choice cards (wrap the radio semantics in a styled label).
const VERDICT_TONES = { Approve: 'var(--brand-primary)', Defer: RV.purple, Reject: 'var(--ink-600)' };
function VerdictChoices({ name, value, onChange }) {
  return (
    <div role="radiogroup" aria-label="Verdict" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 'var(--space-3)' }}>
      {['Approve', 'Defer', 'Reject'].map((v) => {
        const on = value === v, c = VERDICT_TONES[v];
        return (
          <label key={v} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', borderRadius: '14px', padding: '14px 16px', minHeight: '44px', background: on ? 'var(--white)' : 'var(--grey-50)', border: on ? `2px solid ${c}` : '2px solid transparent', boxShadow: on ? '0 4px 14px rgba(43,43,43,.08)' : 'none', transition: 'all var(--duration-fast) var(--ease-standard)' }}>
            <input type="radio" name={name} checked={on} onChange={() => onChange(v)} style={{ accentColor: c, width: '18px', height: '18px', margin: 0 }} />
            <span style={{ fontWeight: 700, color: 'var(--text-heading)' }}>{v}</span>
          </label>
        );
      })}
    </div>
  );
}
const ABSENT = ['Not recorded', 'Not available'];
function StatTileRow({ items }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
      {items.map((i) => <_StatTile key={i.label} label={i.label} value={i.value} absent={ABSENT.includes(i.value)} />)}
    </div>
  );
}
function PageTitle({ children }) {
  return <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px, 6vw, 44px)', lineHeight: 1.2, color: 'var(--text-heading)', margin: 0, overflowWrap: 'break-word' }}>{children}</h1>;
}
function ActionRow({ children }) {
  return <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>{children}</div>;
}
function RowLink({ children, onClick, label }) {
  return <button type="button" aria-label={label} onClick={onClick} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', fontWeight: 700, color: 'var(--link-default, #cc0078)', textDecoration: 'underline', cursor: 'pointer' }}>{children}</button>;
}

function VerdictDialog({ application, onClose }) {
  const [v, setV] = React.useState('Approve');
  return (
    <div role="dialog" aria-modal="true" style={{ position: 'fixed', inset: 0, background: 'rgba(20,10,30,0.45)', display: 'grid', placeItems: 'center', zIndex: 10, padding: 'var(--space-4)' }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: '#fff', borderRadius: 'var(--radius-lg)', padding: 'var(--space-6)', width: 'min(520px, 100%)', borderRadius: '20px', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', boxShadow: 'var(--shadow-lg, 0 12px 40px rgba(0,0,0,.2))' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}><Eyebrow>Record verdict</Eyebrow><h2 style={{ ...h2Style, margin: 0 }}>{application.ref}</h2></div>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-body)' }}>You are recording the <strong>Trustee 1</strong> verdict.</p>
        <VerdictChoices name="dlg-verdict" value={v} onChange={setV} />
        <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-sm)', color: 'var(--text-heading)' }}>
          Notes (optional)
          <textarea rows={3} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', padding: '12px 14px', borderRadius: '12px', border: '1.5px solid var(--grey-200)', background: 'var(--grey-50)' }}></textarea>
        </label>
        <ActionRow>
          <_Button variant="primary" onClick={onClose}>Save verdict</_Button>
          <_Button variant="secondary" onClick={onClose}>Cancel</_Button>
        </ActionRow>
      </div>
    </div>
  );
}

const APPLICATIONS = [
  { id: 'a1', ref: 'REV-2026-1057', score: 60, circ: 'Terminal illness', dates: '5 Oct 2026 to 12 Oct 2026', status: 'Eligible for Panel', round: '5', group: 'GRP-014' },
  { id: 'a2', ref: 'REV-2026-1060', score: 21, circ: 'None', dates: '17 Oct 2026 to 19 Oct 2026', status: 'Borderline', round: '5', group: null },
  { id: 'a3', ref: 'REV-2026-1061', score: 20, circ: 'Recent bereavement', dates: '7 Dec 2026 to 14 Dec 2026', status: 'Under Review', round: '5', group: 'GRP-014' },
  { id: 'a4', ref: 'REV-2026-1068', score: 10, circ: 'None', dates: '5 Oct 2026 to 9 Oct 2026', status: 'Auto-reject', round: '5', group: null },
  { id: 'a5', ref: 'REV-2026-1065', score: null, circ: 'Not recorded', dates: '9 Nov 2026 to 16 Nov 2026', status: 'Eligible for Panel', round: '5', group: 'GRP-017' },
  { id: 'a6', ref: 'REV-2026-1072', score: 44, circ: 'Carer breakdown', dates: '9 Nov 2026 to 16 Nov 2026', status: 'Eligible for Panel', round: '5', group: 'GRP-017' },
  { id: 'a7', ref: 'REV-2026-1074', score: 38, circ: 'None', dates: '5 Oct 2026 to 12 Oct 2026', status: 'Under Review', round: '5', group: 'GRP-014' },
];
const REQUESTED = { a1: 1000, a3: 850, a5: 1200, a6: 1100, a7: 900 };

function deriveGroups(rows) {
  const map = {};
  rows.filter((r) => r.group).forEach((r) => { (map[r.group] = map[r.group] || []).push(r); });
  return Object.keys(map).sort().map((code) => {
    const members = map[code];
    const shared = members.every((m) => m.dates === members[0].dates) ? members[0].dates : 'Dates differ between members';
    return { code, members, memberCount: members.length, total: members.reduce((s, m) => s + (REQUESTED[m.id] || 0), 0), shared };
  });
}
const gbp = (n) => '£' + n.toLocaleString('en-GB', { minimumFractionDigits: 2 });

Object.assign(window, { RV, Eyebrow, HeroBand, FactChips, StatusPill, ScoreChip, VerdictChoices, PButton, Panel, Definitions, StateMessage, StatTileRow, PageTitle, ActionRow, RowLink, VerdictDialog, APPLICATIONS, deriveGroups, gbp, h3Style });
