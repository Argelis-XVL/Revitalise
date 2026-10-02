// Mirrors pages/LandingPage.tsx + RoundStatistics.tsx + RoundFinancePanel.tsx — playful presentation layer.
const RV_PURPLE = '#49345b', RV_PURPLE_FADED = '#6a5774', RV_TEAL = '#14adbb';
const PALETTE = ['var(--brand-primary)', RV_PURPLE, RV_TEAL, 'var(--pink-300)', RV_PURPLE_FADED];

function Eyebrow({ children, color = 'var(--brand-primary)' }) {
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: 'var(--text-xs, 12px)', fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: color }}></span>{children}</span>;
}

function Card({ eyebrow, eyebrowColor, heading, children, style }) {
  return (
    <section className="rv-card rv-lift" style={{ padding: 'var(--space-8)', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', borderRadius: '16px', ...style }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {eyebrow && <Eyebrow color={eyebrowColor}>{eyebrow}</Eyebrow>}
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', color: 'var(--text-heading)', margin: 0 }}>{heading}</h2>
      </div>
      {children}
    </section>
  );
}

function RoundHero() {
  const opened = 1, closed = 30, today = 30;
  const pct = Math.round(((today - opened) / (closed - opened)) * 100);
  return (
    <section className="rv-card" style={{ borderRadius: '20px', padding: 'var(--space-8)', background: 'linear-gradient(135deg, var(--lavender-100) 0%, var(--pink-50) 100%)', display: 'grid', gridTemplateColumns: 'auto minmax(0, 1fr)', gap: 'var(--space-8)', alignItems: 'center' }}>
      <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: 'var(--white)', boxShadow: '0 6px 20px rgba(73,52,91,.14)', display: 'grid', placeItems: 'center', textAlign: 'center' }}>
        <div>
          <div style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: RV_PURPLE }}>Round</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '52px', lineHeight: 1, color: 'var(--brand-primary)' }}>5</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', minWidth: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <Eyebrow color={RV_PURPLE}>This round</Eyebrow>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', color: 'var(--text-heading)', margin: 0 }}>Open from 1 Sep to 30 Sep 2026</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <div style={{ height: '10px', borderRadius: '999px', background: 'rgba(255,255,255,.8)', overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', borderRadius: '999px', background: `linear-gradient(90deg, ${RV_PURPLE} 0%, var(--brand-primary) 100%)` }}></div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>
            <span><strong style={{ color: 'var(--text-heading)' }}>Opened</strong> 1 Sep 2026</span>
            <span><strong style={{ color: 'var(--text-heading)' }}>Closed</strong> 30 Sep 2026</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function ProgressTiles({ items }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
      {items.map(([label, value, color, tint]) => (
        <div key={label} style={{ borderRadius: '14px', padding: 'var(--space-5)', background: tint, display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <span style={{ width: '28px', height: '6px', borderRadius: '999px', background: color }}></span>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '40px', lineHeight: 1.05, color: 'var(--text-heading)' }}>{value}</span>
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>{label}</span>
        </div>
      ))}
    </div>
  );
}

function Bars({ rows, n }) {
  const total = n || rows.reduce((s, r) => s + r[1], 0);
  const max = Math.max(1, ...rows.map((r) => r[1]));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      {rows.map(([label, v], i) => (
        <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 'var(--space-3)', fontSize: 'var(--text-sm)' }}>
            <span style={{ color: 'var(--text-heading)', fontWeight: 700 }}>{label}</span>
            <span style={{ color: 'var(--ink-700)' }}><strong style={{ color: 'var(--text-heading)' }}>{v}</strong> · {pct(v, total)}%</span>
          </div>
          <div style={{ height: '12px', borderRadius: '999px', background: 'var(--grey-100)', overflow: 'hidden' }}>
            <div style={{ width: `${(v / max) * 100}%`, minWidth: v ? '12px' : 0, height: '100%', borderRadius: '999px', background: PALETTE[i % PALETTE.length] }}></div>
          </div>
        </div>
      ))}
    </div>
  );
}

const pct = (n, t) => (t ? Math.round((n / t) * 1000) / 10 : 0);

function Counted({ n }) {
  return <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--ink-600)' }}>Counted over {n} applications in this round.</p>;
}

function ChartBlock({ title, n, rows, series, children }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', minWidth: 0 }}>
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-heading)', margin: 0 }}>{title}</h3>
      {n != null && <Counted n={n} />}
      {children}
      <div><window.RowLink onClick={() => setOpen((o) => !o)}>{open ? 'Hide the data table' : 'Show the data table'}</window.RowLink></div>
      {open && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
          <thead><tr style={{ borderBottom: '1px solid var(--border-default)' }}>
            <th style={{ textAlign: 'left', padding: '6px 8px', color: 'var(--text-heading)' }}>Category</th>
            {(series || ['Applications']).map((s) => <th key={s} style={{ textAlign: 'right', padding: '6px 8px', color: 'var(--text-heading)' }}>{s}</th>)}
            {!series && <th style={{ textAlign: 'right', padding: '6px 8px', color: 'var(--text-heading)' }}>Share of round</th>}
          </tr></thead>
          <tbody>{rows.map((r) => (
            <tr key={r[0]} style={{ borderBottom: '1px solid var(--grey-100)' }}>
              <td style={{ padding: '6px 8px' }}>{r[0]}</td>
              {series ? r[1].map((v, i) => <td key={i} style={{ textAlign: 'right', padding: '6px 8px' }}>{v}%</td>)
                : <><td style={{ textAlign: 'right', padding: '6px 8px' }}>{r[1]}</td><td style={{ textAlign: 'right', padding: '6px 8px' }}>{pct(r[1], n)}%</td></>}
            </tr>))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// Vertical columns with rounded tops — maps to Recharts <BarChart><Bar radius={[8,8,0,0]}/>.
function Columns({ rows, n, color = 'var(--brand-primary)', height = 180 }) {
  const [hover, setHover] = React.useState(null);
  const max = Math.max(1, ...rows.map((r) => r[1]));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
      <div style={{ position: 'relative', height: height + 'px', display: 'flex', alignItems: 'flex-end', gap: '6px', padding: '0 2px', backgroundImage: 'repeating-linear-gradient(to top, var(--grey-100) 0 1px, transparent 1px ' + height / 4 + 'px)', borderBottom: '1.5px solid var(--grey-200)' }}>
        {rows.map(([label, v], i) => (
          <div key={label} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} style={{ flex: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'center', position: 'relative' }}>
            {hover === i && <span style={{ position: 'absolute', bottom: `calc(${(v / max) * 100}% + 8px)`, background: 'var(--ink-900)', color: '#fff', fontSize: '12px', fontWeight: 700, padding: '4px 8px', borderRadius: '8px', whiteSpace: 'nowrap', zIndex: 2 }}>{label} · {pct(v, n)}%</span>}
            <div style={{ width: '100%', maxWidth: '44px', height: `${(v / max) * 100}%`, minHeight: v ? '4px' : 0, borderRadius: '8px 8px 3px 3px', background: color, opacity: hover === null || hover === i ? 1 : 0.55, transition: 'opacity var(--duration-fast)' }}></div>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '6px', padding: '0 2px' }}>
        {rows.map(([label]) => <span key={label} style={{ flex: 1, textAlign: 'center', fontSize: '12px', color: 'var(--ink-700)', lineHeight: 1.25 }}>{label}</span>)}
      </div>
    </div>
  );
}

// Grouped columns (one colour per question) — Recharts <BarChart> with several <Bar>s.
function GroupedColumns({ categories, series, colors, height = 200 }) {
  const max = Math.max(1, ...series.flatMap((s) => s.values));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ height: height + 'px', display: 'flex', alignItems: 'flex-end', gap: '14px', backgroundImage: 'repeating-linear-gradient(to top, var(--grey-100) 0 1px, transparent 1px ' + height / 4 + 'px)', borderBottom: '1.5px solid var(--grey-200)', padding: '0 4px' }}>
        {categories.map((c, ci) => (
          <div key={c} style={{ flex: 1, height: '100%', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', gap: '3px' }}>
            {series.map((s, si) => <div key={s.name} title={`${s.name}: ${s.values[ci]}%`} style={{ flex: 1, maxWidth: '18px', height: `${(s.values[ci] / max) * 100}%`, minHeight: s.values[ci] ? '4px' : 0, borderRadius: '6px 6px 2px 2px', background: colors[si] }}></div>)}
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '14px', padding: '0 4px' }}>
        {categories.map((c) => <span key={c} style={{ flex: 1, textAlign: 'center', fontSize: '12px', color: 'var(--ink-700)', lineHeight: 1.25 }}>{c}</span>)}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2) var(--space-4)' }}>
        {series.map((s, i) => <span key={s.name} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: 'var(--text-sm)', color: 'var(--ink-700)', background: 'var(--grey-50)', borderRadius: '999px', padding: '4px 12px 4px 8px' }}><span style={{ width: '10px', height: '10px', borderRadius: '50%', background: colors[i] }}></span>{s.name}</span>)}
      </div>
    </div>
  );
}

// Donut — Recharts <Pie innerRadius outerRadius paddingAngle cornerRadius>.
function Donut({ rows, n }) {
  let acc = 0;
  const stops = rows.map(([, v], i) => { const a = acc; acc += (v / n) * 100; return `${PALETTE[i]} ${a}% ${acc}%`; }).join(', ');
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)', alignItems: 'center' }}>
      <div style={{ width: '160px', height: '160px', borderRadius: '50%', background: `conic-gradient(${stops})`, display: 'grid', placeItems: 'center', flex: 'none' }}>
        <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: '#fff', display: 'grid', placeItems: 'center', textAlign: 'center', boxShadow: 'inset 0 1px 4px rgba(43,43,43,.06)' }}>
          <div><div style={{ fontFamily: 'var(--font-display)', fontSize: '28px', color: 'var(--text-heading)', lineHeight: 1 }}>{n}</div><div style={{ fontSize: '11px', color: 'var(--ink-600)' }}>applications</div></div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', flex: '1 1 200px' }}>
        {rows.map(([label, v], i) => (
          <div key={label} style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'baseline' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: PALETTE[i], flex: 'none', transform: 'translateY(1px)' }}></span>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-heading)', minWidth: '56px' }}>{pct(v, n)}%</span>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MoneyTiles({ items }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--space-3)' }}>
      {items.map(([label, value]) => {
        const absent = value === 'Not recorded';
        return (
          <div key={label} style={{ borderRadius: '14px', padding: 'var(--space-4) var(--space-5)', background: absent ? 'transparent' : 'var(--grey-50)', border: absent ? '1.5px dashed var(--grey-200)' : '1.5px solid transparent', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>{label}</span>
            <span style={absent ? { fontSize: 'var(--text-base)', color: 'var(--ink-600)', fontStyle: 'italic' } : { fontFamily: 'var(--font-display)', fontSize: '26px', color: 'var(--text-heading)', lineHeight: 1.15 }}>{value}</span>
          </div>
        );
      })}
    </div>
  );
}

function RoundOverview({ onOpenList }) {
  const Button = window.PButton;
  const { PageTitle, ActionRow } = window;
  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        <PageTitle>Round overview — 5</PageTitle>
        <p style={{ color: 'var(--text-body)', margin: 0 }}>This portal shows the one grant round currently open for review. There is no round to choose.</p>
      </div>
      <ActionRow>
        <Button variant="primary" onClick={onOpenList}>Open the applications list</Button>
        <Button variant="secondary">Refresh figures</Button>
      </ActionRow>

      <RoundHero />

      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'baseline', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', color: 'var(--text-heading)', margin: 0 }}>Figures of this round</h2>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)', background: 'var(--white)', borderRadius: '999px', padding: '6px 14px', boxShadow: '0 1px 3px rgba(43,43,43,.08)' }}>Computed on 30 Sep 2026 at 15:42</span>
      </div>

      <Card eyebrow="Round progress" heading="48 applications in 59 days">
        <ProgressTiles items={[
          ['Applications received', '48', 'var(--brand-primary)', 'var(--pink-50)'],
          ['Applications per day', '0.81', RV_PURPLE, 'var(--lavender-100)'],
          ['Days the round has been open', '59', RV_TEAL, '#e7f6f8'],
        ]} />
      </Card>

      <Card eyebrow="Exceptional circumstances" heading="1 in 4 applications cite an exceptional circumstance">
        <ProgressTiles items={[
          ['Applications citing any exceptional circumstance', '12', 'var(--brand-primary)', 'var(--pink-50)'],
          ['Share of the round citing any exceptional circumstance', '25.0%', RV_PURPLE, 'var(--lavender-100)'],
          ['Average exceptional funding requested', '£640', RV_TEAL, '#e7f6f8'],
        ]} />
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--ink-600)' }}>The average exceptional funding requested is shown only where enough applications citing exceptional circumstances carry a figure.</p>
        <ChartBlock title="Exceptional circumstance cited" n={48} rows={[['Palliative care', 5], ['Carer breakdown or urgent need', 4], ['Severe financial hardship', 2], ['Other (please specify)', 1]]}>
          <Bars n={48} rows={[['Palliative care', 5], ['Carer breakdown or urgent need', 4], ['Severe financial hardship', 2], ['Other (please specify)', 1]]} />
        </ChartBlock>
      </Card>

      <Card eyebrow="Who applied in this round" eyebrowColor={RV_PURPLE} heading="The people behind the applications">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))', gap: 'var(--space-8) var(--space-10, 40px)' }}>
          <ChartBlock title="Gender" n={48} rows={[['Female', 26], ['Male', 19], ['Non-binary', 2], ['Describes themselves another way', 0], ['Prefer not to say', 1]]}>
            <Bars n={48} rows={[['Female', 26], ['Male', 19], ['Non-binary', 2], ['Describes themselves another way', 0], ['Prefer not to say', 1]]} />
          </ChartBlock>
          <ChartBlock title="Age range" n={48} rows={[['Under 18', 1], ['18 to 24', 3], ['25 to 34', 5], ['35 to 44', 6], ['45 to 54', 8], ['55 to 64', 10], ['65 to 74', 9], ['75 and over', 5], ['Not known', 1]]}>
            <Columns n={48} color={RV_PURPLE} rows={[['Under 18', 1], ['18–24', 3], ['25–34', 5], ['35–44', 6], ['45–54', 8], ['55–64', 10], ['65–74', 9], ['75+', 5], ['Not known', 1]]} />
          </ChartBlock>
          <ChartBlock title="Applicant type" n={48} rows={[['A disabled person', 29], ['A carer applying on behalf of a disabled person', 12], ['A carer applying for yourself', 7]]}>
            <Donut n={48} rows={[['A disabled person', 29], ['A carer applying on behalf of a disabled person', 12], ['A carer applying for yourself', 7]]} />
          </ChartBlock>
          <ChartBlock title="Ethnic group" n={48} rows={[['White', 34], ['Asian or Asian British', 6], ['Black, African, Caribbean or Black British', 4], ['Mixed or Multiple ethnic groups', 2], ['Other ethnic group', 1], ['Prefer not to say', 1]]}>
            <Bars n={48} rows={[['White', 34], ['Asian or Asian British', 6], ['Black, African, Caribbean or Black British', 4], ['Mixed or Multiple ethnic groups', 2], ['Other ethnic group', 1], ['Prefer not to say', 1]]} />
          </ChartBlock>
        </div>
      </Card>

      <Card eyebrow="Level of need" heading="How applicants have been feeling">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))', gap: 'var(--space-8) var(--space-10, 40px)' }}>
          <ChartBlock title="Wellbeing, last year (all questions)" series={['Question 8', 'Question 9', 'Question 10']} rows={[['Strongly Disagree', [10, 8, 6]], ['Disagree', [21, 19, 15]], ['Neutral', [25, 27, 23]], ['Agree', [29, 31, 35]], ['Strongly Agree', [13, 12, 19]], ['Not sure', [2, 3, 2]]]}>
            <GroupedColumns colors={['var(--brand-primary)', RV_PURPLE, RV_TEAL]} categories={['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree', 'Not sure']} series={[
              { name: 'Wellbeing question 8, last year', values: [10, 21, 25, 29, 13, 2] },
              { name: 'Wellbeing question 9, last year', values: [8, 19, 27, 31, 12, 3] },
              { name: 'Wellbeing question 10, last year', values: [6, 15, 23, 35, 19, 2] },
            ]} />
          </ChartBlock>
          <ChartBlock title="Life satisfaction, 0 to 10" n={48} rows={[['0', 2], ['1', 1], ['2', 3], ['3', 5], ['4', 6], ['5', 9], ['6', 8], ['7', 6], ['8', 4], ['9', 2], ['10', 2]]}>
            <Columns n={48} height={200} rows={[['0', 2], ['1', 1], ['2', 3], ['3', 5], ['4', 6], ['5', 9], ['6', 8], ['7', 6], ['8', 4], ['9', 2], ['10', 2]]} />
          </ChartBlock>
        </div>
      </Card>

      <Card eyebrow="Financial position" eyebrowColor={RV_PURPLE} heading="The round's financial position">
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--ink-700)', display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ background: 'var(--lavender-100)', color: RV_PURPLE, fontWeight: 700, borderRadius: '999px', padding: '4px 12px' }}>Entered by hand</span>
          These figures are as at 26 Sep 2026. The application figures above were computed just now.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <Eyebrow color="var(--ink-600)">This round</Eyebrow>
          <MoneyTiles items={[
            ['Committed or spent to date', '£50,000.00'], ['People supported', '1,000'], ['Individuals supported', 'Not recorded'],
            ['People reached by group grants', '200'], ['Suggested maximum spend for this round', '£550,000.00'], ['Monthly disbursement', 'Not recorded'],
          ]} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <Eyebrow color="var(--ink-600)">Charity-wide</Eyebrow>
          <MoneyTiles items={[['Grant-giving capacity (charity-wide)', '£70,000.00'], ['Remaining legacy fund (charity-wide)', '£100,000.00']]} />
        </div>
      </Card>
    </>
  );
}
window.RoundOverview = RoundOverview;
