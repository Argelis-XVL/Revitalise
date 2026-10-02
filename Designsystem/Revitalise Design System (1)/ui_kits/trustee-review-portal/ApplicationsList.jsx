// Mirrors pages/ApplicationsListPage.tsx + ApplicationFilters.tsx + ApplicationsTable.tsx.
const EMPTY_FILTERS = { round: '', status: '', min: '', max: '', text: '' };

function applyFilters(rows, f) {
  return rows.filter((r) =>
    (!f.round || r.round === f.round) && (!f.status || r.status === f.status) &&
    (f.min === '' || (r.score ?? -1) >= Number(f.min)) && (f.max === '' || (r.score ?? 1e9) <= Number(f.max)) &&
    (!f.text || r.ref.toLowerCase().includes(f.text.toLowerCase())));
}

const fieldStyle = { display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-sm)', color: 'var(--text-heading)', width: '200px' };
const controlStyle = { fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', minHeight: '44px', padding: '0 14px', borderRadius: '12px', border: '1.5px solid var(--grey-200)', color: 'var(--text-heading)', background: 'var(--grey-50)', width: '100%', boxSizing: 'border-box' };

function ApplicationFilters({ filters, onChange }) {
  const Button = window.PButton;
  const rows = window.APPLICATIONS;
  const statuses = [...new Set(rows.map((r) => r.status))].sort();
  const rounds = [...new Set(rows.map((r) => r.round))];
  const set = (k) => (e) => onChange({ ...filters, [k]: e.target.value });
  return (
    <div className="rv-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 'var(--space-6) var(--space-8)', borderRadius: '16px' }}>
      <window.Eyebrow color={window.RV.purple}>Filter the round</window.Eyebrow>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', alignItems: 'flex-end' }}>
      <label style={fieldStyle}>Review round
        <select value={filters.round} onChange={set('round')} style={controlStyle}><option value="">All rounds available to you</option>{rounds.map((r) => <option key={r}>{r}</option>)}</select>
      </label>
      <label style={fieldStyle}>Status
        <select value={filters.status} onChange={set('status')} style={controlStyle}><option value="">All statuses</option>{statuses.map((s) => <option key={s}>{s}</option>)}</select>
      </label>
      <label style={{ ...fieldStyle, width: '120px' }}>Score from<input type="number" value={filters.min} onChange={set('min')} style={controlStyle} /></label>
      <label style={{ ...fieldStyle, width: '120px' }}>Score to<input type="number" value={filters.max} onChange={set('max')} style={controlStyle} /></label>
      <label style={{ ...fieldStyle, width: '260px' }}>Application reference contains<input value={filters.text} onChange={set('text')} style={controlStyle} /></label>
      <Button variant="secondary" onClick={() => onChange(EMPTY_FILTERS)}>Clear filters</Button>
      </div>
    </div>
  );
}

const thStyle = { textAlign: 'left', padding: 'var(--space-4) var(--space-4)', background: 'var(--grey-50)', fontFamily: 'var(--font-body)', fontWeight: 700, fontSize: '12px', letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--ink-700)', verticalAlign: 'bottom' };
const tdStyle = { padding: 'var(--space-4)', verticalAlign: 'middle' };
const tableCardStyle = { overflowX: 'auto', overflowY: 'hidden' };
const captionStyle = { textAlign: 'left', color: 'var(--ink-700)', fontSize: 'var(--text-sm)', padding: 'var(--space-6) var(--space-6) var(--space-4)', background: 'var(--white)' };
const COLUMNS = [['ref', 'Application'], ['score', 'Circumstance score', true], ['circ', 'Exceptional circumstance'], ['dates', 'Preferred dates'], ['status', 'Status']];

function ApplicationsTable({ rows, caption, sort, onSort, onOpen, onRecordVerdict }) {
  const Button = window.PButton;
  return (
    <div className="rv-card" style={tableCardStyle}>
      <table className="rv-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-base)' }}>
        <caption style={captionStyle}>{caption}</caption>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border-default)' }}>
            {COLUMNS.map(([k, label, num]) => {
              const dir = sort && sort.key === k ? sort.dir : null;
              return (
                <th key={k} scope="col" aria-sort={dir || 'none'} style={{ ...thStyle, textAlign: num ? 'right' : 'left' }}>
                  <button type="button" onClick={() => onSort && onSort(k)} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', color: 'inherit', cursor: onSort ? 'pointer' : 'default', display: 'inline-flex', gap: '6px', alignItems: 'center' }}>
                    {label}<span aria-hidden="true" style={{ fontSize: '10px', color: 'var(--brand-primary)' }}>{dir === 'asc' ? '▲' : dir === 'desc' ? '▼' : ''}</span>
                  </button>
                </th>
              );
            })}
            <th scope="col" style={thStyle}>Decision</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} style={{ borderBottom: '1px solid var(--border-default)' }}>
              <th scope="row" style={{ ...tdStyle, textAlign: 'left' }}><window.RowLink label={`${r.ref}, open the full case`} onClick={() => onOpen(r)}>{r.ref}</window.RowLink></th>
              <td style={{ ...tdStyle, textAlign: 'right' }}><window.ScoreChip score={r.score} /></td>
              <td style={{ ...tdStyle, color: r.circ === 'None' || r.circ === 'Not recorded' ? 'var(--ink-600)' : 'var(--text-heading)' }}>{r.circ}</td>
              <td style={tdStyle}>{r.dates}</td>
              <td style={tdStyle}><window.StatusPill status={r.status} /></td>
              <td style={tdStyle}><Button variant="primary" aria-label={`Record verdict for ${r.ref}`} onClick={() => onRecordVerdict(r)}>Record verdict</Button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function sortRows(rows, sort) {
  const out = [...rows];
  out.sort((a, b) => {
    const x = a[sort.key] ?? -1, y = b[sort.key] ?? -1;
    return (x > y ? 1 : x < y ? -1 : 0) * (sort.dir === 'asc' ? 1 : -1);
  });
  return out;
}

function ApplicationsList({ onOpenCase }) {
  const Button = window.PButton;
  const [filters, setFilters] = React.useState(EMPTY_FILTERS);
  const [sort, setSort] = React.useState({ key: 'score', dir: 'desc' });
  const [verdictFor, setVerdictFor] = React.useState(null);
  const all = window.APPLICATIONS;
  const rows = sortRows(applyFilters(all, filters), sort);
  const caption = rows.length === all.length ? `${all.length} applications under review.` : `${rows.length} of ${all.length} applications shown by the current filters.`;
  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}><window.Eyebrow>Round 5</window.Eyebrow><window.PageTitle>Applications under review</window.PageTitle></div>
      <ApplicationFilters filters={filters} onChange={setFilters} />
      <window.ActionRow><Button variant="secondary">Print this list</Button></window.ActionRow>
      {rows.length === 0
        ? <window.StateMessage heading="No applications match these filters" explanation="Clear or widen the filters above to see the applications under review again." />
        : <ApplicationsTable rows={rows} caption={caption} sort={sort} onSort={(k) => setSort((s) => ({ key: k, dir: s.key === k && s.dir === 'asc' ? 'desc' : 'asc' }))} onOpen={onOpenCase} onRecordVerdict={setVerdictFor} />}
      {verdictFor && <window.VerdictDialog application={verdictFor} onClose={() => setVerdictFor(null)} />}
    </>
  );
}
Object.assign(window, { ApplicationsList, ApplicationFilters, ApplicationsTable, applyFilters, EMPTY_FILTERS, thStyle, tdStyle, tableCardStyle, captionStyle });
