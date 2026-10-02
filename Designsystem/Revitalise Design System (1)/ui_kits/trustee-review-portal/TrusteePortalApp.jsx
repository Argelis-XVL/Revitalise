// Mirrors App.tsx view state: landing | list | groups | groupDetail | detail(fromGroup).
function TrusteePortalApp() {
  const [view, setView] = React.useState({ name: 'landing' });
  const go = (v) => { setView(v); window.scrollTo(0, 0); };
  return (
    <window.AppFrame view={view} setView={go}>
      {view.name === 'landing' && <window.RoundOverview onOpenList={() => go({ name: 'list' })} />}
      {view.name === 'list' && <window.ApplicationsList onOpenCase={(a) => go({ name: 'detail', application: a, fromGroup: null })} />}
      {view.name === 'groups' && <window.GroupsList onOpenGroup={(g) => go({ name: 'groupDetail', group: g })} />}
      {view.name === 'groupDetail' && <window.GroupDetail group={view.group} onOpenCase={(a) => go({ name: 'detail', application: a, fromGroup: view.group })} />}
      {view.name === 'detail' && <window.ApplicationDetail key={view.application.id} application={view.application} fromGroup={view.fromGroup} onBackToGroup={() => go({ name: 'groupDetail', group: view.fromGroup })} />}
    </window.AppFrame>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<TrusteePortalApp />);
