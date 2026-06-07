import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Logs from './pages/Logs';
import Footer from './components/Footer';
import { ToastContainer } from './components/Toast';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <Navbar />
      <Landing />
      <Dashboard />
      <Config />
      <Logs />
      <Footer />
      <ToastContainer />
    </div>
  );
}
