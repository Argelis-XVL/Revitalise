import React from 'react';

export function StatTile({ label, value, sublabel }) {
  return (
    <div style={{ border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4) var(--space-5)', fontFamily: 'var(--font-body)', background: '#fff' }}>
      <div style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--weight-semibold)', color: 'var(--text-muted)', textTransform: 'none' }}>{label}{sublabel && <span style={{ display: 'block', fontWeight: 400 }}>{sublabel}</span>}</div>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--text-heading)', marginTop: 'var(--space-1)' }}>{value}</div>
    </div>
  );
}
