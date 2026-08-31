const { useState } = React;

function TrusteePortalApp() {
  const [screen, setScreen] = useState('overview');
  const [caseId, setCaseId] = useState(null);
  return (
    <window.AppFrame>
      <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-6)' }}>
        {['overview', 'list', 'detail'].map((s) => (
          <button key={s} onClick={() => setScreen(s)} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', fontWeight: 700, padding: '6px 14px', borderRadius: 'var(--radius-pill)', border: 'none', cursor: 'pointer', background: screen === s ? 'var(--brand-primary)' : 'var(--grey-100)', color: screen === s ? '#fff' : 'var(--ink-900)' }}>
            {s === 'overview' ? 'Round overview' : s === 'list' ? 'Applications list' : 'Application detail'}
          </button>
        ))}
      </div>
      {screen === 'overview' && <window.RoundOverview onOpenList={() => setScreen('list')} />}
      {screen === 'list' && <window.ApplicationsList onBack={() => setScreen('overview')} onOpenCase={(id) => { setCaseId(id); setScreen('detail'); }} />}
      {screen === 'detail' && <window.ApplicationDetail id={caseId || 'REV-2026-1057'} onBack={() => setScreen('list')} />}
    </window.AppFrame>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<TrusteePortalApp />);
