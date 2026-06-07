import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitCommit, DollarSign, Bell, Search, ChevronDown } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { apiGet } from '../lib/api';

const TABS = [
  { id: 'evolution', label: 'Evolution', icon: <GitCommit size={16} /> },
  { id: 'transactions', label: 'Transactions', icon: <DollarSign size={16} /> },
  { id: 'notifications', label: 'Notifications', icon: <Bell size={16} /> },
] as const;

export default function Logs() {
  const [tab, setTab] = useState<'evolution' | 'transactions' | 'notifications'>('evolution');
  const [evolution, setEvolution] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    apiGet('/api/evolution').then(setEvolution);
  }, []);

  return (
    <section id="logs" className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-20">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-3xl font-bold mb-2">History & Logs</motion.h2>
      <p className="text-[#a0a0a0] mb-8">Every evolution, every dollar, every notification</p>

      <div className="flex items-center gap-1 mb-6 bg-[#111] rounded-xl p-1 w-fit">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${
              tab === t.id ? 'bg-[#76b900] text-black font-medium' : 'text-[#a0a0a0] hover:text-white'
            }`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2 bg-[#111] border border-[#222] rounded-lg px-4 py-2.5 mb-6 max-w-md focus-within:border-[#76b900]/50 transition-colors">
        <Search size={16} className="text-[#666]" />
        <input placeholder="Search history..." className="bg-transparent flex-1 text-sm outline-none" />
      </div>

      {tab === 'evolution' && (
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-px bg-gradient-to-b from-[#76b900]/30 via-[#222] to-transparent" />
          {evolution.map((commit, i) => (
            <motion.div key={commit.hash} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }} className="relative pl-10 pb-6">
              <div className="absolute left-2.5 top-1 w-3 h-3 rounded-full bg-[#76b900]/20 border-2 border-[#76b900]" />
              <GlassCard hover={true}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <code className="text-sm text-[#76b900] font-mono">{commit.hash}</code>
                    <span className="text-sm">{commit.message}</span>
                  </div>
                  <span className="text-xs text-[#666]">{commit.date}</span>
                </div>
                <button onClick={() => setExpanded(expanded === commit.hash ? null : commit.hash)}
                  className="text-xs text-[#666] hover:text-[#a0a0a0] flex items-center gap-1">
                  <ChevronDown size={12} className={`transition-transform ${expanded === commit.hash ? 'rotate-180' : ''}`} />
                  Details
                </button>
                <AnimatePresence>
                  {expanded === commit.hash && (
                    <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
                      className="overflow-hidden mt-3 pt-3 border-t border-[#222]">
                      <p className="text-xs text-[#666]">Author: {commit.author}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </GlassCard>
            </motion.div>
          ))}
          {evolution.length === 0 && (
            <div className="text-center text-[#666] py-12">No evolution history yet.</div>
          )}
        </div>
      )}

      {tab !== 'evolution' && (
        <GlassCard>
          <div className="text-center text-[#666] py-12">
            {tab === 'transactions' ? 'Transaction history will appear here.' : 'No notifications yet.'}
          </div>
        </GlassCard>
      )}
    </section>
  );
}
