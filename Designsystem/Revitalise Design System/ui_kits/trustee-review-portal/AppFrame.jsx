const { Button } = window.RevitaliseDesignSystem_a4dff3;

function AppFrame({ children }) {
  return (
    <div style={{ fontFamily: 'var(--font-body)', minHeight: '100vh', background: '#fff' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-5) var(--space-8)', borderBottom: '1px solid var(--border-default)' }}>
        <img src="../../assets/logo/revitalise-logo-tagline-sans.png" alt="Revitalise" style={{ height: '44px' }} />
        <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>Signed in as <strong style={{ color: 'var(--text-heading)' }}>svc_grantapplications</strong></div>
      </div>
      <div style={{ padding: 'var(--space-8)', maxWidth: '1200px', margin: '0 auto' }}>{children}</div>
    </div>
  );
}
window.AppFrame = AppFrame;
