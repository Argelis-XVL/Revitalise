import React from 'react';

const GLYPHS = {
  facebook: 'M13.5 9H15V6h-1.5C11.6 6 10.5 7.1 10.5 8.6V10H9v2.5h1.5V18h2.5v-5.5H15L15.5 10h-2v-1c0-.55.05-1 1-1z',
  instagram: 'M12 8.5A3.5 3.5 0 1 0 12 15.5 3.5 3.5 0 1 0 12 8.5zM12 10a2 2 0 1 1 0 4 2 2 0 1 1 0-4zM16.5 6.5a1 1 0 1 1 0 2 1 1 0 1 1 0-2zM8 6h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z',
  linkedin: 'M7 9h2.2v8H7V9zm1.1-3.4A1.3 1.3 0 1 1 8.1 8.2 1.3 1.3 0 1 1 8.1 5.6zM11 9h2.1v1.1h.03c.29-.55 1-1.13 2.07-1.13 2.22 0 2.63 1.46 2.63 3.36V17h-2.2v-3.36c0-.8-.02-1.84-1.12-1.84-1.12 0-1.3.88-1.3 1.78V17H11V9z',
};

export function Badge({ network = 'facebook', size = 40 }) {
  return (
    <div style={{ width: size, height: size, borderRadius: 'var(--radius-circle)', background: 'var(--brand-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24" fill="#fff"><path d={GLYPHS[network]} /></svg>
    </div>
  );
}
