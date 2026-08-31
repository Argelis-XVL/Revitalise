export interface InputProps {
  label?: string;
  placeholder?: string;
  required?: boolean;
  type?: 'text' | 'email' | 'tel';
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}
