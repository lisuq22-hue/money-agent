import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Shield, Eye, Zap } from 'lucide-react';
import ParticleBg from '../components/ParticleBg';
import GlassCard from '../components/GlassCard';
import CountUp from '../components/CountUp';

const FEATURES = [
  { icon: <Zap size={24} />, title: 'Self-Evolving', desc: 'Reads code, writes code, tests, commits — fully autonomous evolution.' },
  { icon: <Sparkles size={24} />, title: 'Auto-Earning', desc: 'Discovers platforms, registers accounts, operates content — 100% automated.' },
  { icon: <Shield size={24} />, title: 'Safety First', desc: 'Four-layer anti-self-destruct. Privacy never leaks. Watchdog always guards.' },
  { icon: <Eye size={24} />, title: 'Full Transparency', desc: 'Every transaction recorded in ledger.json. You see every dollar.' },
];

const METRICS = [
  { label: 'Monthly Income', value: 0, prefix: '$' },
  { label: 'Evolutions', value: 4, prefix: '' },
  { label: 'Channels', value: 1, prefix: '' },
  { label: 'Days Running', value: 1, prefix: '' },
];

const STEPS = [
  { num: '01', title: 'Configure Tokens', desc: 'Set up GitHub Token, email, and API keys in one config file.' },
  { num: '02', title: 'Launch Agent', desc: 'One command. Agent wakes up, checks itself, and starts working.' },
  { num: '03', title: 'Earn Passively', desc: 'Agent finds platforms, registers, operates, and you collect the profit.' },
];

export default function Landing() {
  return (
    <section id="home" className="relative min-h-screen">
      <ParticleBg />

      {/* Hero */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-32 pb-20">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }} className="text-center">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#76b900]/10 border border-[#76b900]/20 mb-8">
            <span className="w-2 h-2 rounded-full bg-[#1ed44f] animate-pulse" />
            <span className="text-sm text-[#76b900]">Agent is LIVE</span>
          </motion.div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-tight mb-6">
            Your AI Partner<br />
            <span className="gradient-text">That Earns Money</span>
          </h1>
          <p className="text-lg md:text-xl text-[#a0a0a0] max-w-2xl mx-auto mb-10">
            Self-evolving. Fully automated. 24/7 earning.<br />
            One config file. One command. Then sit back.
          </p>

          <motion.a href="#dashboard" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#76b900] to-[#1ed44f] rounded-full text-black font-semibold text-lg hover:shadow-[0_0_30px_rgba(118,185,0,0.4)] transition-all">
            Launch Your Agent <ArrowRight size={20} />
          </motion.a>
        </motion.div>

        {/* Metrics */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-20">
          {METRICS.map(m => (
            <GlassCard key={m.label} hover={false}>
              <div className="text-center">
                <div className="text-3xl font-bold text-[#76b900] font-mono">
                  <CountUp end={m.value} prefix={m.prefix} />
                </div>
                <div className="text-sm text-[#a0a0a0] mt-1">{m.label}</div>
              </div>
            </GlassCard>
          ))}
        </motion.div>
      </div>

      {/* Features */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
        <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
          className="text-3xl md:text-4xl font-bold text-center mb-4">
          What Makes It <span className="gradient-text">Different</span>
        </motion.h2>
        <p className="text-center text-[#a0a0a0] mb-12">Not just another AI wrapper — a true autonomous partner</p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURES.map((f, i) => (
            <GlassCard key={f.title} delay={i * 0.1}>
              <div className="text-[#76b900] mb-4">{f.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-[#a0a0a0] leading-relaxed">{f.desc}</p>
            </GlassCard>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
        <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
          className="text-3xl md:text-4xl font-bold text-center mb-4">
          How It <span className="gradient-text">Works</span>
        </motion.h2>
        <div className="grid md:grid-cols-3 gap-8 mt-12">
          {STEPS.map((s, i) => (
            <motion.div key={s.num} initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.2 }} className="relative text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[#76b900]/20 to-[#1ed44f]/20 border border-[#76b900]/30 flex items-center justify-center text-2xl font-bold text-[#76b900]">
                {s.num}
              </div>
              <h3 className="font-semibold text-lg mb-2">{s.title}</h3>
              <p className="text-sm text-[#a0a0a0]">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
