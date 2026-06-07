import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Bot } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Home', href: '#home' },
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Config', href: '#config' },
  { label: 'Logs', href: '#logs' },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-[#222]' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#home" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#76b900] to-[#1ed44f] flex items-center justify-center group-hover:shadow-[0_0_20px_rgba(118,185,0,0.4)] transition-all">
            <Bot className="w-5 h-5 text-black" />
          </div>
          <span className="font-bold text-lg tracking-tight">MoneyAgent</span>
        </a>

        <div className="hidden md:flex items-center gap-8">
          {NAV_ITEMS.map(item => (
            <a key={item.label} href={item.href}
              className="text-sm text-[#a0a0a0] hover:text-white transition-colors">
              {item.label}
            </a>
          ))}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#111] border border-[#222]">
            <span className="w-2 h-2 rounded-full bg-[#1ed44f] animate-pulse" />
            <span className="text-xs text-[#a0a0a0]">Agent Online</span>
          </div>
        </div>

        <button className="md:hidden text-white" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X /> : <Menu />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-[#222]">
            {NAV_ITEMS.map(item => (
              <a key={item.label} href={item.href}
                className="block px-6 py-3 text-sm text-[#a0a0a0] hover:text-white hover:bg-[#111]">
                {item.label}
              </a>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
