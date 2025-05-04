export interface NavigationMenuItem {
  label: string;
  icon?: string;
  to?: string;
  type?: 'link' | 'button' | 'label';
  active?: boolean;
  click?: () => void;
  children?: NavigationMenuItem[];
  defaultOpen?: boolean;
  disabled?: boolean;
  target?: string;
  badge?: string;
  description?: string;
}