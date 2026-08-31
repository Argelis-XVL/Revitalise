const { Button, Notice, Radio } = window.RevitaliseDesignSystem_a4dff3;

function Section({ title, children }) {
  return (
    <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: 'var(--space-6)' }}>
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-4)' }}>{title}</h3>
      {children}
    </div>
  );
}
function Field({ label, value }) {
  return (
    <div style={{ display: 'flex', gap: 'var(--space-4)', fontSize: 'var(--text-base)', padding: 'var(--space-1) 0' }}>
      <strong style={{ color: 'var(--text-heading)', minWidth: '220px' }}>{label}</strong>
      <span style={{ color: 'var(--text-body)' }}>{value}</span>
    </div>
  );
}

function ApplicationDetail({ id, onBack }) {
  const [verdict, setVerdict] = React.useState('Approve');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
        <Button variant="secondary" size="sm" onClick={onBack}>Back to the list</Button>
        <Button variant="secondary" size="sm">Print this case</Button>
      </div>
      <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', color: 'var(--text-heading)' }}>Application {id}</h1>

      <Section title="Anonymised narrative">
        <Notice tone="muted" title="Anonymised narrative withheld">This narrative has not been released for trustee review yet. Every narrative is withheld until the process owner has checked the anonymisation and released it — the rest of the case can still be decided from.</Notice>
      </Section>

      <Section title="Circumstance score">
        <Field label="Score" value="60" />
        <Field label="Status" value="Eligible for Panel" />
        <Field label="Review round" value="2" />
        <p style={{ color: 'var(--text-body)', fontSize: 'var(--text-sm)', marginTop: 'var(--space-3)' }}>Circumstance score: 60 out of 60 · Scored on 2026-08-21 11:32 UTC. Wellbeing subtotal 50 points, life-satisfaction 10 points inverted. Thresholds: knockout at or below 20, borderline 21–30, income ceiling £25,000.</p>
      </Section>

      <Section title="Holiday details">
        <Field label="Type of break" value="Holiday accommodation (hotel, cottage, caravan, holiday park)" />
        <Field label="Preferred dates" value="5 Oct 2026 to 12 Oct 2026" />
        <Field label="Break location" value="Seaside cottage, Northumberland" />
        <Field label="Total funding requested" value="£1,000.00" />
        <Field label="Total costs" value="£1,000.00" />
      </Section>

      <Section title="Care-support description">
        <Field label="Applicant type" value="A disabled person" />
        <Field label="Hours of support per week" value="10 - 19 hours" />
        <div style={{ marginTop: 'var(--space-3)' }}>
          <Notice tone="muted" title="Care-support description withheld">This description has not been released for trustee review yet — the rest of the case can still be decided from.</Notice>
        </div>
      </Section>

      <Section title="Staff recommendation">
        <Notice tone="muted" title="No staff recommendation recorded">No staff recommendation has been written against this application's review record.</Notice>
      </Section>

      <Section title="Your verdict">
        <p style={{ color: 'var(--text-body)', fontSize: 'var(--text-sm)' }}>You are recording the <strong>Trustee 1</strong> verdict for {id}.</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
          {['Approve', 'Defer', 'Reject'].map((v) => (
            <Radio key={v} name="verdict" label={v} checked={verdict === v} onChange={() => setVerdict(v)} />
          ))}
        </div>
        <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-sm)', color: 'var(--text-heading)', marginBottom: 'var(--space-4)' }}>
          Notes (optional)
          <textarea rows={3} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-default)' }}></textarea>
        </label>
        <Button variant="primary">Save verdict</Button>
      </Section>
    </div>
  );
}
window.ApplicationDetail = ApplicationDetail;
