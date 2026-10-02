import React from 'react';

export function Card({ image, title, children, footer }) {
  return (
    <div style={{ background: 'var(--surface-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-card)', overflow: 'hidden', fontFamily: 'var(--font-body)' }}>
      {image && <img src={image} alt="" style={{ width: '100%', height: '160px', objectFit: 'cover' }} />}
      <div style={{ padding: 'var(--space-6)' }}>
        {title && <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>{title}</h3>}
        <div style={{ color: 'var(--text-body)' }}>{children}</div>
        {footer && <div style={{ marginTop: 'var(--space-4)' }}>{footer}</div>}
      </div>
    </div>
  );
}
