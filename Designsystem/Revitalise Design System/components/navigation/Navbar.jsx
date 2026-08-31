import React from 'react';
import { Button } from '../core/Button.jsx';
import { Badge } from '../content/Badge.jsx';

const NAV = ['Home', 'About Us', 'What We Fund', 'Support Us', 'Case Studies', 'Contact Us'];

export function Navbar() {
  return (
    <div style={{ fontFamily: 'var(--font-body)', background: '#fff' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', padding: 'var(--space-2) var(--space-6)' }}>
        <Badge network="facebook" size={28} />
        <Badge network="instagram" size={28} />
        <Badge network="linkedin" size={28} />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-4) var(--space-6)', borderTop: '1px solid var(--border-default)', borderBottom: '1px solid var(--border-default)' }}>
        <img src="../../assets/logo/revitalise-logo.png" alt="Revitalise" style={{ height: '36px' }} />
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Button variant="primary" size="sm">Apply Now</Button>
          <Button variant="primary" size="sm">Donate Today</Button>
        </div>
      </div>
      <nav style={{ display: 'flex', gap: 'var(--space-6)', padding: 'var(--space-3) var(--space-6)', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-semibold)' }}>
        {NAV.map((item) => (
          <a key={item} href="#" style={{ color: 'var(--text-heading)', textDecoration: 'underline' }}>{item}</a>
        ))}
      </nav>
    </div>
  );
}
