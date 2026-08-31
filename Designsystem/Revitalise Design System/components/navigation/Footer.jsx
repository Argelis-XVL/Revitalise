import React from 'react';
import { NewsletterForm } from '../forms/NewsletterForm.jsx';

export function Footer() {
  return (
    <footer style={{ background: 'var(--surface-muted)', padding: 'var(--space-12) var(--space-6)', fontFamily: 'var(--font-body)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.4fr', gap: 'var(--space-8)', maxWidth: 'var(--container-max)', margin: '0 auto' }}>
        <div>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-3)' }}>Explore</h4>
          {['Home', 'About Us', 'What We Fund', 'Support Us', 'Case Studies', 'Contact Us', 'FAQs', 'Donate', 'Apply For Funding'].map((l) => (
            <div key={l} style={{ padding: 'var(--space-2) 0', borderBottom: '1px solid var(--border-default)' }}><a href="#">{l}</a></div>
          ))}
        </div>
        <div>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginBottom: 'var(--space-3)' }}>Legal</h4>
          {['Privacy Policy', 'Cookie Policy'].map((l) => (
            <div key={l} style={{ padding: 'var(--space-2) 0', borderBottom: '1px solid var(--border-default)' }}><a href="#">{l}</a></div>
          ))}
        </div>
        <NewsletterForm />
      </div>
      <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 'var(--text-xs)', marginTop: 'var(--space-10)' }}>© Copyright Revitalise Respite Holidays 2026. Registered charity number 295072. Company number 2044219.</p>
    </footer>
  );
}
