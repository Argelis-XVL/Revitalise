import React from 'react';

export function Button({ variant = 'primary', size = 'md', children, disabled, icon, ...rest }) {
  const pad = size === 'sm' ? '10px 20px' : size === 'lg' ? '16px 36px' : '13px 28px';
  const fontSize = size === 'sm' ? 'var(--text-sm)' : 'var(--text-base)';
  const base = {
    fontFamily: 'var(--font-body)',
    fontWeight: 'var(--weight-bold)',
    fontSize,
    padding: pad,
    borderRadius: 'var(--radius-pill)',
    border: '2px solid transparent',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'background var(--duration-base) var(--ease-standard), color var(--duration-base) var(--ease-standard)',
  };
  const styles = {
    primary: { background: 'var(--brand-primary)', color: 'var(--text-on-brand)' },
    secondary: { background: 'transparent', color: 'var(--brand-primary)', border: '2px solid var(--brand-primary)' },
    ghost: { background: 'transparent', color: 'var(--brand-primary)', textDecoration: 'underline', padding: '4px 2px', borderRadius: 0 },
  };
  return (
    <button style={{ ...base, ...styles[variant] }} disabled={disabled} {...rest}>
      {icon}{children}
    </button>
  );
}
