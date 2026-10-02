// Mirrors pages/GroupsListPage.tsx + GroupsTable.tsx and pages/GroupDetailPage.tsx (EF-43).
function GroupsList({ onOpenGroup }) {
  const Button = window.PButton;
  const [filters, setFilters] = React.useState(window.EMPTY_FILTERS);
  const groups = window.deriveGroups(window.applyFilters(window.APPLICATIONS, filters));
  const { thStyle, tdStyle, tableCardStyle, captionStyle } = window;
  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}><window.Eyebrow>Round 5</window.Eyebrow><window.PageTitle>Group applications</window.PageTitle></div>
      <window.ApplicationFilters filters={filters} onChange={setFilters} />
      <window.ActionRow><Button variant="secondary">Print this list</Button></window.ActionRow>
      {groups.length === 0 ? (
        <window.StateMessage heading="No groups match these filters" explanation="Clear or widen the filters above to see the groups under review again." />
      ) : (
        <div className="rv-card" style={tableCardStyle}>
          <table className="rv-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-base)' }}>
            <caption style={captionStyle}>{groups.length} group{groups.length === 1 ? '' : 's'} of linked applications.</caption>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-default)' }}>
                <th scope="col" style={thStyle}>Group</th>
                <th scope="col" style={{ ...thStyle, textAlign: 'right' }}>Members</th>
                <th scope="col" style={{ ...thStyle, textAlign: 'right' }}>Group total requested</th>
                <th scope="col" style={thStyle}>Shared dates</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g) => (
                <tr key={g.code} style={{ borderBottom: '1px solid var(--border-default)' }}>
                  <th scope="row" style={{ ...tdStyle, textAlign: 'left' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
                      <span aria-hidden="true" style={{ width: '36px', height: '36px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--lavender-100), var(--pink-50))', display: 'grid', placeItems: 'center', fontFamily: 'var(--font-display)', color: 'var(--brand-primary)', fontSize: '15px' }}>{g.code.slice(-2)}</span>
                      <window.RowLink label={`Group ${g.code}, open the group's applications`} onClick={() => onOpenGroup(g)}>{g.code}</window.RowLink>
                    </span>
                  </th>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
                      <span aria-hidden="true" style={{ display: 'inline-flex' }}>{g.members.map((m, i) => <span key={m.id} style={{ width: '22px', height: '22px', borderRadius: '50%', border: '2px solid #fff', marginLeft: i ? '-7px' : 0, background: ['var(--brand-primary)', window.RV.purple, window.RV.teal, 'var(--pink-300)'][i % 4] }}></span>)}</span>
                      <strong style={{ color: 'var(--text-heading)' }}>{g.memberCount}</strong>
                    </span>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-heading)' }}>{window.gbp(g.total)}</td>
                  <td style={tdStyle}>{g.shared}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function GroupDetail({ group, onOpenCase }) {
  const [verdictFor, setVerdictFor] = React.useState(null);
  return (
    <>
      <window.PageTitle>Group {group.code}</window.PageTitle>
      <window.HeroBand badgeLabel="Members" badgeValue={group.memberCount} eyebrow="Group summary" heading={`${window.gbp(group.total)} requested together`}>
        <window.FactChips items={[['Group code', group.code], ['Members', String(group.memberCount)], ['Group total requested', window.gbp(group.total)], ['Shared dates', group.shared]]} />
      </window.HeroBand>
      <window.Eyebrow color={window.RV.purple}>Applications in this group</window.Eyebrow>
      <window.ApplicationsTable rows={group.members} caption={`${group.memberCount} application${group.memberCount === 1 ? '' : 's'} in group ${group.code}.`} onOpen={onOpenCase} onRecordVerdict={setVerdictFor} />
      {verdictFor && <window.VerdictDialog application={verdictFor} onClose={() => setVerdictFor(null)} />}
    </>
  );
}
Object.assign(window, { GroupsList, GroupDetail });
