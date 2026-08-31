import React from 'react';
export interface CardProps {
  image?: string;
  title?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
}
