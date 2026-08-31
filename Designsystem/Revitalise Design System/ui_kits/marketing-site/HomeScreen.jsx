const { Button } = window.RevitaliseDesignSystem_a4dff3;
function HomeScreen() {
  return (
    <div>
      <div style={{ position: 'relative' }}>
        <img src="../../assets/photography/guests-group-garden.jpeg" style={{ width: '100%', height: '440px', objectFit: 'cover', display: 'block' }} />
        <div style={{ position: 'absolute', left: 0, bottom: '48px', background: 'var(--brand-primary)', padding: 'var(--space-10)', maxWidth: '520px' }}>
          <h1 style={{ fontFamily: 'var(--font-display)', color: '#fff', fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-3)' }}>Revitalise</h1>
          <p style={{ color: '#fff', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-6)' }}>Funding vital respite for disabled people & carers.</p>
          <Button variant="primary" style={{ background: '#fff', color: 'var(--brand-primary)' }}>Apply Now</Button>
        </div>
      </div>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: 'var(--space-16) var(--space-6)', fontFamily: 'var(--font-body)' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', marginBottom: 'var(--space-5)' }}>Revitalise Is A National Charity Providing Respite Grants To Disabled Adults And Their Family Carers</h2>
        <p style={{ color: 'var(--text-body)', lineHeight: 'var(--leading-normal)', fontSize: 'var(--text-lg)' }}>
          For over 60 years, we provided our own respite holidays via specialist respite centres. In 2024, we took the difficult decision to close our centres due to the severe impact of the cost-of-living crisis.
        </p>
        <p style={{ color: 'var(--text-body)', lineHeight: 'var(--leading-normal)', fontSize: 'var(--text-lg)' }}>
          Today, we continue the legacy of our founder, Joan Brander MBE, by ensuring that disabled people and their carers can have the respite breaks, holidays and life experiences they need.
        </p>
      </div>
    </div>
  );
}
window.HomeScreen = HomeScreen;
