import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Bot } from 'lucide-react';

const NAV = [
  { label: '首页', href: '#home' },
  { label: '仪表盘', href: '#dashboard' },
  { label: '配置', href: '#config' },
  { label: '日志', href: '#logs' },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <motion.nav initial={{ y: -80 }} animate={{ y: 0 }}
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-[#222]' : 'bg-transparent'
      }`}>
      <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#home" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#76b900] to-[#1ed44f] flex items-center justify-center group-hover:shadow-[0_0_20px_rgba(118,185,0,0.4)] transition-all">
            <Bot className="w-4 h-4 text-black" />
          </div>
          <span className="font-bold text-base">赚钱Agent</span>
        </a>
        <div className="hidden md:flex items-center gap-6">
          {NAV.map(item => (
            <a key={item.href} href={item.href} className="text-sm text-[#888] hover:text-white transition-colors">{item.label}</a>
          ))}
          <span className="flex items-center gap-1.5 text-xs text-[#76b900]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#76b900] animate-pulse" />运行中
          </span>
        </div>
        <button className="md:hidden text-white" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-[#222]">
            {NAV.map(item => (
              <a key={item.href} href={item.href} className="block px-6 py-3 text-sm text-[#888] hover:text-white">{item.label}</a>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
