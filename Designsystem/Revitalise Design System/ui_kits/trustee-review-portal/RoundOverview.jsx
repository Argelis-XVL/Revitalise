const { Button, Notice, StatTile } = window.RevitaliseDesignSystem_a4dff3;

function RoundOverview({ onOpenList }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-3xl)', color: 'var(--text-heading)', marginBottom: 'var(--space-2)' }}>Round overview — 2</h1>
        <p style={{ color: 'var(--text-body)', fontSize: 'var(--text-base)', margin: 0 }}>This portal shows the one grant round currently open for review. There is no round to choose.</p>
      </div>
      <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
        <Button variant="primary" onClick={onOpenList}>Open the applications list</Button>
        <Button variant="secondary">Refresh figures</Button>
      </div>
      <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: 'var(--space-6)' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-4)' }}>This round</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', fontSize: 'var(--text-base)' }}>
          <div><strong style={{ color: 'var(--text-heading)' }}>Round</strong> &nbsp; 2</div>
          <div><strong style={{ color: 'var(--text-heading)' }}>Opened</strong> &nbsp; 2 Aug 2026</div>
          <div><strong style={{ color: 'var(--text-heading)' }}>Closed</strong> &nbsp; 31 Aug 2026</div>
        </div>
      </div>
      <Notice tone="muted" title="Round figures are unavailable">
        The round-statistics flow is not bound to this app. <code>pa app add flow --flow-id &lt;id&gt;</code> has not been run, so there is no generated service to call. The flow must exist and be on in the environment first. No figures are shown rather than a partial set. Use Refresh figures to try again — the applications list is unaffected.
      </Notice>
      <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: 'var(--space-6)' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-1)' }}>The round's financial position</h3>
        <p style={{ fontStyle: 'italic', color: 'var(--text-muted)', fontSize: 'var(--text-sm)', marginTop: 0, marginBottom: 'var(--space-5)' }}>These figures are entered by hand and are as at 26 Aug 2026.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-4)' }}>
          <StatTile label="Committed or spent to date" value="£50,000.00" />
          <StatTile label="People supported" value="1,000" />
          <StatTile label="Individuals supported" value="Not recorded" />
          <StatTile label="People reached by group grants" value="200" />
          <StatTile label="Suggested maximum spend for this round" value="£550,000.00" />
          <StatTile label="Monthly disbursement" value="Not recorded" />
          <StatTile label="Grant-giving capacity (charity-wide)" value="£70,000.00" />
          <StatTile label="Remaining legacy fund (charity-wide)" value="£100,000.00" />
        </div>
      </div>
    </div>
  );
}
window.RoundOverview = RoundOverview;
