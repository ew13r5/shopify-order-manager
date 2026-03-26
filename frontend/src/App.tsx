import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { queryClient } from './lib/queryClient';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { OrdersPage } from './features/orders/OrdersPage';
import { OrderDetailPage } from './features/orders/OrderDetailPage';
import { PayoutsPage } from './features/payouts/PayoutsPage';
import { SettingsPage } from './features/settings/SettingsPage';

function NotFound() {
  return <div className="p-6"><h1 className="text-2xl font-bold">404 - Page Not Found</h1></div>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/orders/:id" element={<OrderDetailPage />} />
            <Route path="/payouts" element={<PayoutsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
        <Toaster theme="dark" />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
