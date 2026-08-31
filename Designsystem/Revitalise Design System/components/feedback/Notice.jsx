import React from 'react';

const TONES = {
  muted: { bg: 'var(--surface-muted)', fg: 'var(--text-body)', title: 'var(--text-heading)' },
  info: { bg: 'var(--pink-50)', fg: 'var(--ink-700)', title: 'var(--pink-700)' },
  warning: { bg: '#fdf5e6', fg: 'var(--ink-700)', title: 'var(--warning)' },
};

export function Notice({ tone = 'muted', title, children }) {
  const t = TONES[tone] || TONES.muted;
  return (
    <div style={{ background: t.bg, borderRadius: 'var(--radius-md)', padding: 'var(--space-5) var(--space-6)', fontFamily: 'var(--font-body)' }}>
      {title && <div style={{ fontWeight: 'var(--weight-bold)', color: t.title, marginBottom: 'var(--space-2)', fontSize: 'var(--text-base)' }}>{title}</div>}
      <div style={{ color: t.fg, fontSize: 'var(--text-sm)', lineHeight: 'var(--leading-normal)' }}>{children}</div>
    </div>
  );
}
