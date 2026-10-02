const { useState } = React;
const { Navbar, Footer, CookieBanner } = window.RevitaliseDesignSystem_a4dff3;
const { HomeScreen, FaqScreen, FundingScreen } = window;

function MarketingSiteApp() {
  const [screen, setScreen] = useState('home');
  const [cookieVisible, setCookieVisible] = useState(true);
  const screens = { home: HomeScreen, faq: FaqScreen, funding: FundingScreen };
  const Screen = screens[screen];
  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      <div style={{ display: 'flex', gap: 'var(--space-2)', padding: 'var(--space-3) var(--space-6)', background: 'var(--ink-900)' }}>
        {Object.keys(screens).map((k) => (
          <button key={k} onClick={() => setScreen(k)} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', fontWeight: 700, padding: '6px 14px', borderRadius: 'var(--radius-pill)', border: 'none', cursor: 'pointer', background: screen === k ? 'var(--brand-primary)' : '#fff', color: screen === k ? '#fff' : 'var(--ink-900)' }}>
            {k === 'home' ? 'Home' : k === 'faq' ? 'FAQ' : 'Apply For Funding'}
          </button>
        ))}
      </div>
      <Navbar />
      <Screen />
      <Footer />
      {cookieVisible && (
        <div style={{ position: 'fixed', left: 'var(--space-6)', bottom: 'var(--space-6)' }}>
          <div onClick={() => setCookieVisible(false)} style={{ cursor: 'pointer' }}><CookieBanner /></div>
        </div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<MarketingSiteApp />);
