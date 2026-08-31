import React from 'react';

export function Radio({ label, checked, onChange, name }) {
  return (
    <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', color: 'var(--text-body)', cursor: 'pointer' }}>
      <input type="radio" name={name} checked={checked} onChange={onChange} style={{ width: '18px', height: '18px', accentColor: 'var(--brand-primary)' }} />
      {label}
    </label>
  );
}
