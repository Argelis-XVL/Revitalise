import React from 'react';
import { Button } from '../core/Button.jsx';
import { Input } from './Input.jsx';
import { Checkbox } from './Checkbox.jsx';

export function NewsletterForm() {
  return (
    <div style={{ background: '#fff', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: 'var(--space-8)', maxWidth: '420px', fontFamily: 'var(--font-body)' }}>
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>Sign Up For Revitalise E-News</h3>
      <p style={{ color: 'var(--text-body)', marginTop: 0, marginBottom: 'var(--space-6)' }}>Be the first to know all the latest from Revitalise! Join our online community today.</p>
      <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
        <Input label="First name" required />
        <Input label="Last name" required />
      </div>
      <div style={{ marginBottom: 'var(--space-4)' }}>
        <Input label="Your email" required type="email" />
      </div>
      <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-sm)', padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>I am interested in the following:</span>
        <Checkbox label="Grants" />
        <Checkbox label="Fundraising" />
      </div>
      <Button variant="primary">Sign me up!</Button>
    </div>
  );
}
