import React, { lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
const Dashboard = lazy(() => import('./pages/Dashboard').then(module => ({ default: module.Dashboard })));
const InvoiceManager = lazy(() => import('./pages/InvoiceManager').then(module => ({ default: module.InvoiceManager })));
const InvoiceUpload = lazy(() => import('./pages/InvoiceUpload').then(module => ({ default: module.InvoiceUpload })));
const AskAI = lazy(() => import('./pages/AskAI').then(module => ({ default: module.AskAI })));
const Analytics = lazy(() => import('./pages/Analytics').then(module => ({ default: module.Analytics })));
const Automation = lazy(() => import('./pages/Automation').then(module => ({ default: module.Automation })));
const Reports = lazy(() => import('./pages/Reports').then(module => ({ default: module.Reports })));
const Settings = lazy(() => import('./pages/Settings').then(module => ({ default: module.Settings })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="invoices" element={<InvoiceManager />} />
            <Route path="upload" element={<InvoiceUpload />} />
            <Route path="chat" element={<AskAI />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="automation" element={<Automation />} />
            <Route path="reports" element={<Reports />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
