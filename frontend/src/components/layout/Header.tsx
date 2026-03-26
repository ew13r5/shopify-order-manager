import { StoreSelector } from './StoreSelector';
import { ModeSwitch } from './ModeSwitch';
import { MobileNav } from './MobileNav';

export function Header() {
  return (
    <header className="flex h-14 items-center gap-4 border-b border-border bg-background px-4">
      <MobileNav />
      <div className="flex-1" />
      <StoreSelector />
      <ModeSwitch />
    </header>
  );
}
