import React, { useState } from 'react';

export function Accordion({ items = [] }) {
  const [open, setOpen] = useState(null);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', fontFamily: 'var(--font-body)', maxWidth: '720px' }}>
      {items.map((item, i) => (
        <div key={i}>
          <button
            onClick={() => setOpen(open === i ? null : i)}
            style={{
              width: '100%', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'var(--surface-muted)', border: 'none', borderRadius: 'var(--radius-sm)',
              padding: 'var(--space-4) var(--space-5)', fontSize: 'var(--text-base)', color: 'var(--text-heading)',
              cursor: 'pointer', fontFamily: 'inherit', fontWeight: 'var(--weight-regular)',
            }}
          >
            {item.question}
            <span style={{ color: 'var(--brand-primary)', fontSize: '18px', transform: open === i ? 'rotate(90deg)' : 'none', transition: 'transform var(--duration-base) var(--ease-standard)' }}>›</span>
          </button>
          {open === i && (
            <div style={{ padding: 'var(--space-4) var(--space-5)', color: 'var(--text-body)' }}>{item.answer}</div>
          )}
        </div>
      ))}
    </div>
  );
}
