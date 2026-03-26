import { NavLink } from 'react-router-dom';
import { Home, ShoppingCart, DollarSign, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', label: 'Dashboard', icon: Home },
  { to: '/orders', label: 'Orders', icon: ShoppingCart },
  { to: '/payouts', label: 'Payouts', icon: DollarSign },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export function AppSidebar() {
  return (
    <aside className="hidden md:flex md:w-64 flex-col border-r border-sidebar-border bg-sidebar-background">
      <div className="flex h-14 items-center border-b border-sidebar-border px-4">
        <span className="text-lg font-semibold text-sidebar-foreground">
          Shopify Manager
        </span>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
