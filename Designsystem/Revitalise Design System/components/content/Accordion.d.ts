import React from 'react';
/**
 * @startingPoint section="Components" subtitle="FAQ-style expanding rows" viewport="700x260"
 */
export interface AccordionItem {
  question: string;
  answer: React.ReactNode;
}
export interface AccordionProps {
  items: AccordionItem[];
}
