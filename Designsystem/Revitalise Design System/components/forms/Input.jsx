import React from 'react';

export function Input({ label, placeholder, required, type = 'text', ...rest }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', color: 'var(--text-heading)' }}>
      {label && <span>{label}{required && '*'}</span>}
      <input
        type={type}
        placeholder={placeholder}
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-base)',
          padding: '12px 14px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-default)',
          color: 'var(--text-body)',
          outline: 'none',
        }}
        {...rest}
      />
    </label>
  );
}
