// Mirrors App.tsx: skip link, header (logo + signed-in sentence), persistent "Screen navigation" bar.
function NavButton({ selected, onClick, children }) {
  return (
    <button type="button" aria-current={selected ? 'page' : undefined} onClick={onClick} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', fontWeight: 700, minHeight: '44px', padding: '0 18px', borderRadius: 'var(--radius-pill)', border: 'none', cursor: 'pointer', background: selected ? 'var(--brand-primary)' : 'transparent', color: selected ? '#fff' : 'var(--ink-900)', transition: 'background var(--duration-fast) var(--ease-standard)' }}>{children}</button>
  );
}

function AppFrame({ view, setView, children }) {
  const onGroups = view.name === 'groups' || view.name === 'groupDetail';
  return (
    <div style={{ fontFamily: 'var(--font-body)', minHeight: '100vh', background: 'var(--grey-50)' }}>
      <header style={{ position: 'sticky', top: 0, zIndex: 5, display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-4) clamp(16px, 4vw, 48px)', background: 'var(--white)', boxShadow: '0 1px 0 rgba(43,43,43,.05), 0 4px 16px rgba(43,43,43,.06)' }}>
        <img src="../../assets/logo/revitalise-logo.png" alt="Revitalise Respite Holidays" style={{ height: '44px', width: 'auto' }} />
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>Signed in as <strong style={{ color: 'var(--text-heading)' }}>Emily Sheardown</strong>.</p>
      </header>
      <main id="main" style={{ padding: 'var(--space-8) clamp(16px, 4vw, 48px)', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        <nav aria-label="Screen navigation" className="rv-nav rv-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', padding: '6px', borderRadius: 'var(--radius-pill)', alignSelf: 'flex-start', maxWidth: '100%' }}>
          <NavButton selected={view.name === 'landing'} onClick={() => setView({ name: 'landing' })}>Round overview</NavButton>
          <NavButton selected={onGroups} onClick={() => setView({ name: 'groups' })}>Group applications</NavButton>
          <NavButton selected={view.name === 'list'} onClick={() => setView({ name: 'list' })}>Individual applications</NavButton>
          {view.name === 'detail' && <NavButton selected onClick={() => {}}>Application detail</NavButton>}
        </nav>
        {children}
      </main>
    </div>
  );
}
window.AppFrame = AppFrame;
