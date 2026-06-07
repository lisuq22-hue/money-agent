import { motion } from 'framer-motion';
import ParticleBg from '../components/ParticleBg';
import GlassCard from '../components/GlassCard';
import CountUp from '../components/CountUp';

export default function Landing() {
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center">
      <ParticleBg />
      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center py-20">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: 'spring' }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#76b900]/10 border border-[#76b900]/20 mb-8 text-sm text-[#76b900]">
            <span className="w-2 h-2 rounded-full bg-[#76b900] animate-pulse" />
            已连续运行 1 天
          </motion.div>

          <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight mb-4">
            会自己赚钱的
            <br />
            <span className="gradient-text">AI 合伙人</span>
          </h1>
          <p className="text-lg text-[#888] max-w-lg mx-auto mb-10">
            自动发现平台 · 自主注册运营 · 24小时赚钱 · 收入三分天下
          </p>

          <motion.a href="#dashboard" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-[#76b900] to-[#1ed44f] rounded-full text-black font-semibold hover:shadow-[0_0_30px_rgba(118,185,0,0.4)] transition-all">
            查看实时数据 →
          </motion.a>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
          className="grid grid-cols-2 gap-4 mt-16">
          {[
            { label: '本月收入', value: 0, prefix: '$' },
            { label: '进化次数', value: 4 },
            { label: '赚钱渠道', value: 1 },
            { label: '运行天数', value: 1 },
          ].map(m => (
            <GlassCard key={m.label}>
              <div className="text-2xl font-bold text-[#76b900] font-mono">
                <CountUp end={m.value} prefix={m.prefix || ''} />
              </div>
              <div className="text-xs text-[#666] mt-1">{m.label}</div>
            </GlassCard>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
