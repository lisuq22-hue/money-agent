import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import GlassCard from '../components/GlassCard';
import CountUp from '../components/CountUp';
import { apiGet } from '../lib/api';

export default function Dashboard() {
  const [ledger, setLedger] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    apiGet('/api/ledger').then(setLedger);
    apiGet('/api/ledger/history').then(setHistory);
    const t = setInterval(() => apiGet('/api/ledger').then(setLedger), 10000);
    return () => clearInterval(t);
  }, []);

  const income = ledger?.total_income ?? 0;
  const expense = ledger?.total_expense ?? 0;
  const profit = income - expense;
  const share = profit > 0 ? profit / 3 : 0;

  return (
    <section id="dashboard" className="relative z-10 max-w-5xl mx-auto px-6 pt-24 pb-16">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-2xl font-bold mb-6">数据仪表盘</motion.h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        {[
          { label: '本月收入', value: income, prefix: '$' },
          { label: '净利润', value: profit, prefix: '$' },
          { label: '赞助者', value: 0 },
          { label: 'ROI', value: expense > 0 ? (profit / expense * 100) : 0, suffix: '%', decimals: 0 },
        ].map((c, i) => (
          <GlassCard key={c.label} delay={i * 0.1}>
            <div className="text-xs text-[#666] mb-1">{c.label}</div>
            <div className="text-2xl font-bold font-mono">
              <CountUp end={c.value} prefix={c.prefix || ''} suffix={c.suffix || ''} decimals={c.decimals ?? 2} />
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <GlassCard>
          <h3 className="text-sm font-semibold mb-3">收支趋势</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={history.length > 0 ? history : [{ month: '6月', income, expense }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
              <XAxis dataKey="month" stroke="#555" fontSize={12} />
              <YAxis stroke="#555" fontSize={12} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #222', borderRadius: '8px', color: '#fff' }} />
              <Line type="monotone" dataKey="income" stroke="#76b900" strokeWidth={2} dot={false} name="收入" />
              <Line type="monotone" dataKey="expense" stroke="#ef4444" strokeWidth={2} dot={false} name="支出" />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard>
          <h3 className="text-sm font-semibold mb-3">三分天下</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={[
                { name: '你的分红', value: share, color: '#76b900' },
                { name: 'Token基金', value: share, color: '#1ed44f' },
                { name: '自由基金', value: share, color: '#5a8f00' },
              ]} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value"
                label={({ name, value }) => `${name} $${value.toFixed(0)}`}>
                {[0, 1, 2].map(i => <Cell key={i} fill={['#76b900', '#1ed44f', '#5a8f00'][i]} />)}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>

      <GlassCard>
        <h3 className="text-sm font-semibold mb-3">运行状态</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div><span className="text-[#555]">当前进度</span><div className="font-mono text-sm mt-0.5">0 / 16 步</div></div>
          <div><span className="text-[#555]">最近提交</span><div className="font-mono text-sm mt-0.5">--</div></div>
          <div><span className="text-[#555]">下次苏醒</span><div className="font-mono text-sm mt-0.5">8 小时后</div></div>
          <div><span className="text-[#555]">服务器</span><div className="font-mono text-sm mt-0.5">--% / --MB</div></div>
        </div>
      </GlassCard>
    </section>
  );
}
