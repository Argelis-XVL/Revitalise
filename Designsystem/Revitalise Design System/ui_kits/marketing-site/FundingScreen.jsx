const { Button } = window.RevitaliseDesignSystem_a4dff3;
function FundingScreen() {
  return (
    <div>
      <div style={{ background: 'var(--surface-band)', textAlign: 'center', padding: 'var(--space-20) var(--space-6)', fontFamily: 'var(--font-body)' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-4)' }}>Receive Funding</h1>
        <p style={{ color: 'var(--text-body)', fontSize: 'var(--text-lg)', maxWidth: '560px', margin: '0 auto var(--space-8)' }}>Applications are open year-round and each month we have a maximum amount of grants we can distribute.</p>
        <Button variant="primary">Apply Now</Button>
      </div>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: 'var(--space-16) var(--space-6)', fontFamily: 'var(--font-body)' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', marginBottom: 'var(--space-6)' }}>How much we fund</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
          <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-8)' }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', color: 'var(--brand-primary)' }}>£500</div>
            <p style={{ color: 'var(--text-body)' }}>per person, for holidays and respite breaks</p>
          </div>
          <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-8)' }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', color: 'var(--brand-primary)' }}>£100</div>
            <p style={{ color: 'var(--text-body)' }}>per person, for day activities</p>
          </div>
        </div>
      </div>
    </div>
  );
}
window.FundingScreen = FundingScreen;
