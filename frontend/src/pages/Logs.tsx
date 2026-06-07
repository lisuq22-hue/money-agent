import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, ChevronDown } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { apiGet } from '../lib/api';

const TABS = ['进化记录', '交易流水', '通知中心'] as const;

export default function Logs() {
  const [tab, setTab] = useState<string>('进化记录');
  const [logs, setLogs] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    apiGet('/api/evolution').then(setLogs);
  }, []);

  return (
    <section id="logs" className="relative z-10 max-w-5xl mx-auto px-6 pt-24 pb-16">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-2xl font-bold mb-6">历史日志</motion.h2>

      <div className="flex items-center gap-1 mb-4 bg-[#111] rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-xs transition-all ${
              tab === t ? 'bg-[#76b900] text-black font-medium' : 'text-[#888] hover:text-white'
            }`}>{t}</button>
        ))}
      </div>

      <div className="flex items-center gap-2 bg-[#111] border border-[#222] rounded-lg px-3 py-2 mb-6 max-w-sm focus-within:border-[#76b900]/40">
        <Search size={14} className="text-[#555]" />
        <input placeholder="搜索..." className="bg-transparent flex-1 text-sm outline-none" />
      </div>

      {tab === '进化记录' && (
        <div className="relative">
          <div className="absolute left-3.5 top-0 bottom-0 w-px bg-gradient-to-b from-[#76b900]/30 via-[#1a1a1a] to-transparent" />
          {logs.map((c, i) => (
            <motion.div key={c.hash} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }} className="relative pl-8 pb-4">
              <div className="absolute left-2 top-1.5 w-3 h-3 rounded-full bg-[#0a0a0a] border-2 border-[#76b900]" />
              <GlassCard>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <code className="text-xs text-[#76b900] font-mono shrink-0">{c.hash}</code>
                    <span className="text-sm truncate">{c.message}</span>
                  </div>
                  <span className="text-xs text-[#555] shrink-0 ml-4">{c.date?.slice(0, 10)}</span>
                </div>
                <button onClick={() => setExpanded(expanded === c.hash ? null : c.hash)}
                  className="text-xs text-[#555] hover:text-[#888] mt-2 flex items-center gap-1">
                  <ChevronDown size={10} className={`transition ${expanded === c.hash ? 'rotate-180' : ''}`} />详情
                </button>
                {expanded === c.hash && (
                  <div className="mt-2 pt-2 border-t border-[#1a1a1a] text-xs text-[#555]">
                    作者: {c.author}
                  </div>
                )}
              </GlassCard>
            </motion.div>
          ))}
          {logs.length === 0 && <div className="text-center text-[#555] py-12 text-sm">暂无进化记录</div>}
        </div>
      )}

      {tab !== '进化记录' && (
        <GlassCard><div className="text-center text-[#555] py-12 text-sm">暂无数据</div></GlassCard>
      )}
    </section>
  );
}
