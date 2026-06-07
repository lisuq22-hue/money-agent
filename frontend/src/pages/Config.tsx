import { useState } from 'react';
import { motion } from 'framer-motion';
import { Key, Globe, Save, Play, Pause, RotateCw, Eye, EyeOff } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import Toggle from '../components/Toggle';
import { showToast } from '../components/Toast';

export default function Config() {
  const [show, setShow] = useState(false);
  const [channels, setChannels] = useState([
    { id: 'github', name: 'GitHub Sponsors', enabled: true },
    { id: 'medium', name: 'Medium', enabled: false },
    { id: 'kofi', name: 'Ko-fi', enabled: false },
  ]);
  const [budget, setBudget] = useState({ token: 50, freedom: 50 });

  return (
    <section id="config" className="relative z-10 max-w-5xl mx-auto px-6 pt-24 pb-16">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-2xl font-bold mb-6">配置管理</motion.h2>

      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <GlassCard>
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"><Key size={16} className="text-[#76b900]" />密钥配置</h3>
          {[
            { label: 'GitHub Token', val: 'ghp_••••••••••••••••' },
            { label: 'QQ 邮箱', val: '••••••@qq.com' },
            { label: 'Anthropic API Key', val: 'sk-ant-••••••••••••' },
          ].map(f => (
            <div key={f.label} className="mb-3">
              <div className="text-xs text-[#666] mb-1">{f.label}</div>
              <div className="flex items-center gap-2 bg-[#0a0a0a] border border-[#222] rounded-lg px-3 py-2 focus-within:border-[#76b900]/40">
                <input type={show ? 'text' : 'password'} defaultValue={f.val} className="bg-transparent flex-1 text-sm outline-none font-mono" />
                <button onClick={() => setShow(!show)} className="text-[#555] hover:text-white">{show ? <EyeOff size={14} /> : <Eye size={14} />}</button>
              </div>
            </div>
          ))}
        </GlassCard>

        <GlassCard>
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"><Globe size={16} className="text-[#76b900]" />赚钱渠道</h3>
          {channels.map(c => (
            <div key={c.id} className="flex items-center justify-between py-2.5 border-b border-[#1a1a1a] last:border-0">
              <span className="text-sm">{c.name}</span>
              <Toggle enabled={c.enabled} onChange={() => setChannels(prev => prev.map(x => x.id === c.id ? {...x, enabled: !x.enabled} : x))} />
            </div>
          ))}
          <div className="mt-5 pt-4 border-t border-[#1a1a1a]">
            <div className="text-xs text-[#666] mb-3">预算上限</div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1"><span>Token 基金 / 月</span><span className="text-[#76b900]">${budget.token}</span></div>
                <input type="range" min={10} max={200} value={budget.token} onChange={e => setBudget({...budget, token:+e.target.value})} className="w-full accent-[#76b900]" />
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1"><span>自由基金单笔上限</span><span className="text-[#76b900]">${budget.freedom}</span></div>
                <input type="range" min={10} max={200} value={budget.freedom} onChange={e => setBudget({...budget, freedom:+e.target.value})} className="w-full accent-[#76b900]" />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard>
        <h3 className="text-sm font-semibold mb-3">操作</h3>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => showToast('success', '配置已保存')}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#76b900] hover:bg-[#5a8f00] text-black rounded-lg text-sm font-medium"><Save size={14} />保存配置</button>
          <button className="flex items-center gap-1.5 px-4 py-2 bg-[#111] hover:bg-[#1a1a1a] border border-[#222] rounded-lg text-sm"><Play size={14} />立即进化</button>
          <button className="flex items-center gap-1.5 px-4 py-2 bg-[#111] hover:bg-[#1a1a1a] border border-[#222] rounded-lg text-sm"><Pause size={14} />暂停</button>
          <button className="flex items-center gap-1.5 px-4 py-2 bg-[#111] hover:bg-[#1a1a1a] border border-red-500/20 text-red-400 rounded-lg text-sm"><RotateCw size={14} />重启</button>
        </div>
      </GlassCard>
    </section>
  );
}
