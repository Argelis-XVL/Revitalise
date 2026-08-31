const { Button, Input } = window.RevitaliseDesignSystem_a4dff3;

const ROWS = [
  { id: 'REV-2026-1057', score: '60', region: 'North East', dates: '5 Oct 2026 to 12 Oct 2026', status: 'Eligible for Panel' },
  { id: 'REV-2026-1060', score: '21', region: 'East Midlands', dates: '17 Oct 2026 to 19 Oct 2026', status: 'Borderline' },
  { id: 'REV-2026-1061', score: '20', region: 'West Midlands', dates: '7 Dec 2026 to 14 Dec 2026', status: 'Under Review' },
  { id: 'REV-2026-1068', score: '10', region: 'Northern Ireland', dates: '5 Oct 2026 to 9 Oct 2026', status: 'Auto-reject' },
  { id: 'REV-2026-1065', score: 'Not scored', region: 'South West', dates: '9 Nov 2026 to 16 Nov 2026', status: 'Eligible for Panel' },
];

function Select({ label }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-sm)', color: 'var(--text-heading)' }}>
      {label}
      <select style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-default)', color: 'var(--text-body)' }}>
        <option>All {label.toLowerCase()}</option>
      </select>
    </label>
  );
}

function ApplicationsList({ onBack, onOpenCase }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div>
        <a href="#" onClick={(e) => { e.preventDefault(); onBack(); }} style={{ fontWeight: 700 }}>← Back to the round overview</a>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', color: 'var(--text-heading)', marginTop: 'var(--space-2)' }}>Applications under review</h1>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', alignItems: 'flex-end' }}>
        <Select label="Review round" />
        <Select label="Status" />
        <Select label="Region" />
        <Input label="Score from" />
        <Input label="Score to" />
        <Input label="Application reference contains" />
        <Button variant="secondary" size="sm">Clear filters</Button>
      </div>
      <div>
        <Button variant="secondary" size="sm">Print this list</Button>
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>5 applications under review.</p>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-base)' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid var(--border-strong)' }}>
            {['Application', 'Circumstance score', 'Region', 'Preferred dates', 'Status', 'Decision'].map((h) => (
              <th key={h} style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-2)', fontFamily: 'var(--font-display)', color: 'var(--text-heading)' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map((r) => (
            <tr key={r.id} style={{ borderBottom: '1px solid var(--border-default)' }}>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}><a href="#" onClick={(e) => { e.preventDefault(); onOpenCase(r.id); }} style={{ fontWeight: 700 }}>{r.id}</a></td>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}>{r.score}</td>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}>{r.region}</td>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}>{r.dates}</td>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}>{r.status}</td>
              <td style={{ padding: 'var(--space-3) var(--space-2)' }}><Button size="sm" onClick={() => onOpenCase(r.id)}>Record verdict</Button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
window.ApplicationsList = ApplicationsList;
