import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Suspense, lazy } from 'react';

const CustomerPortal = lazy(() => import('./pages/CustomerPortal'));
const EmployeeDashboard = lazy(() => import('./pages/EmployeeDashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <nav className="bg-indigo-600 text-white shadow-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight">SmartBank AI</span>
              </div>
              <div className="flex space-x-4">
                <Link to="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-500 transition-colors">
                  Customer Portal
                </Link>
                <Link to="/employee" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-500 transition-colors">
                  Employee Dashboard
                </Link>
                <Link to="/analytics" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-500 transition-colors">
                  Analytics
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Suspense fallback={<div className="p-8 text-center text-slate-500">Loading component...</div>}>
            <Routes>
              <Route path="/" element={<CustomerPortal />} />
              <Route path="/employee" element={<EmployeeDashboard />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
