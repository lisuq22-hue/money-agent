import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, DollarSign, Activity } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import CountUp from '../components/CountUp';
import { apiGet } from '../lib/api';

export default function Dashboard() {
  const [ledger, setLedger] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    apiGet('/api/ledger').then(setLedger);
    apiGet('/api/ledger/history').then(setHistory);
    const interval = setInterval(() => { apiGet('/api/ledger').then(setLedger); }, 10000);
    return () => clearInterval(interval);
  }, []);

  const income = ledger?.total_income ?? 0;
  const expense = ledger?.total_expense ?? 0;
  const profit = income - expense;
  const share = profit > 0 ? profit / 3 : 0;

  const pieData = [
    { name: 'Your Share', value: share, color: '#76b900' },
    { name: 'Token Fund', value: share, color: '#1ed44f' },
    { name: 'Freedom Fund', value: share, color: '#5a8f00' },
  ];

  return (
    <section id="dashboard" className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-20">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-3xl font-bold mb-2">Dashboard</motion.h2>
      <p className="text-[#a0a0a0] mb-8">Real-time agent performance metrics</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Monthly Income', value: income, prefix: '$', icon: <DollarSign size={20} /> },
          { label: 'Net Profit', value: profit, prefix: '$', icon: <TrendingUp size={20} /> },
          { label: 'Sponsors', value: 0, prefix: '', icon: <Users size={20} /> },
          { label: 'ROI', value: expense > 0 ? (profit / expense * 100) : 0, prefix: '', suffix: '%', icon: <Activity size={20} />, decimals: 0 },
        ].map((card, i) => (
          <GlassCard key={card.label} delay={i * 0.1}>
            <div className="flex items-center gap-3 mb-3">
              <div className="text-[#76b900]">{card.icon}</div>
              <span className="text-sm text-[#a0a0a0]">{card.label}</span>
            </div>
            <div className="text-3xl font-bold font-mono">
              <CountUp end={card.value} prefix={card.prefix} suffix={card.suffix || ''} decimals={card.decimals ?? 2} />
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        <GlassCard hover={false}>
          <h3 className="font-semibold mb-4">Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history.length > 0 ? history : [{ month: 'Jun', income, expense, profit }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis dataKey="month" stroke="#666" fontSize={12} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #222', borderRadius: '8px' }} labelStyle={{ color: '#fff' }} />
              <Line type="monotone" dataKey="income" stroke="#76b900" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="expense" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard hover={false}>
          <h3 className="font-semibold mb-4">Profit Split (1/3 Rule)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} dataKey="value"
                label={({ name, value }) => `${name}: $${value.toFixed(0)}`}>
                {pieData.map((d) => <Cell key={d.name} fill={d.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #222', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>

      <GlassCard hover={false}>
        <h3 className="font-semibold mb-4">Evolution Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Pipeline Step', value: '0/16' },
            { label: 'Last Commit', value: 'N/A' },
            { label: 'Next Wake', value: '8h later' },
            { label: 'CPU / RAM', value: '--% / --MB' },
          ].map(s => (
            <div key={s.label}>
              <div className="text-xs text-[#666] mb-1">{s.label}</div>
              <div className="font-mono text-sm">{s.value}</div>
            </div>
          ))}
        </div>
      </GlassCard>
    </section>
  );
}
