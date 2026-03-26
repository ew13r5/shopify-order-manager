import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { queryClient } from './lib/queryClient';

function Dashboard() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Dashboard</h1></div>;
}

function Orders() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Orders</h1></div>;
}

function OrderDetail() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Order Detail</h1></div>;
}

function Payouts() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Payouts</h1></div>;
}

function Settings() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Settings</h1></div>;
}

function NotFound() {
  return <div className="p-6"><h1 className="text-2xl font-bold">404 - Page Not Found</h1></div>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/orders/:id" element={<OrderDetail />} />
            <Route path="/payouts" element={<Payouts />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
