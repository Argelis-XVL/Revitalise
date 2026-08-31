import React from 'react';
import { Button } from '../core/Button.jsx';

export function CookieBanner() {
  return (
    <div style={{ background: '#fff', borderRadius: 'var(--radius-md)', boxShadow: 'var(--shadow-lg)', padding: 'var(--space-6)', maxWidth: '360px', fontFamily: 'var(--font-body)' }}>
      <h4 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-2)' }}>We value your privacy</h4>
      <p style={{ color: 'var(--text-body)', fontSize: 'var(--text-sm)', marginTop: 0 }}>We use cookies to enhance your browsing experience. By clicking "Accept All", you consent to our use of cookies.</p>
      <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
        <Button variant="secondary" size="sm">Customise</Button>
        <Button variant="secondary" size="sm">Reject All</Button>
        <Button variant="primary" size="sm">Accept All</Button>
      </div>
    </div>
  );
}
