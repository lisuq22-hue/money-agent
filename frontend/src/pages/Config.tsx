import { useState } from 'react';
import { motion } from 'framer-motion';
import { Key, Mail, Globe, Save, Play, Pause, RotateCw, Eye, EyeOff } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import Toggle from '../components/Toggle';
import { showToast } from '../components/Toast';

export default function Config() {
  const [showTokens, setShowTokens] = useState(false);
  const [channels, setChannels] = useState([
    { id: 'github_sponsors', name: 'GitHub Sponsors', enabled: true },
    { id: 'medium', name: 'Medium', enabled: false },
    { id: 'kofi', name: 'Ko-fi', enabled: false },
  ]);
  const [budget, setBudget] = useState({ tokenFund: 50, freedomLimit: 50 });

  const toggleChannel = (id: string) => {
    setChannels(prev => prev.map(c => c.id === id ? { ...c, enabled: !c.enabled } : c));
  };

  return (
    <section id="config" className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-20">
      <motion.h2 initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
        className="text-3xl font-bold mb-2">Configuration</motion.h2>
      <p className="text-[#a0a0a0] mb-8">Manage your agent settings</p>

      <div className="grid lg:grid-cols-2 gap-6">
        <GlassCard>
          <div className="flex items-center gap-3 mb-6">
            <Key size={20} className="text-[#76b900]" />
            <h3 className="font-semibold">API Tokens</h3>
          </div>
          {[
            { label: 'GitHub Token', value: 'ghp_••••••••••••••••', icon: <Globe size={16} /> },
            { label: 'QQ Email', value: '••••••@qq.com', icon: <Mail size={16} /> },
            { label: 'Anthropic API Key', value: 'sk-ant-••••••••••••', icon: <Key size={16} /> },
          ].map(field => (
            <div key={field.label} className="mb-4">
              <label className="text-sm text-[#a0a0a0] mb-1.5 block">{field.label}</label>
              <div className="flex items-center gap-2 bg-[#0a0a0a] border border-[#222] rounded-lg px-4 py-2.5 focus-within:border-[#76b900]/50 transition-colors">
                <span className="text-[#666]">{field.icon}</span>
                <input type={showTokens ? 'text' : 'password'} defaultValue={field.value}
                  className="bg-transparent flex-1 text-sm outline-none font-mono" />
                <button onClick={() => setShowTokens(!showTokens)} className="text-[#666] hover:text-white">
                  {showTokens ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          ))}
          <button className="text-sm text-[#76b900] hover:text-[#1ed44f] transition-colors mt-2">
            Test Connection →
          </button>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center gap-3 mb-6">
            <Globe size={20} className="text-[#76b900]" />
            <h3 className="font-semibold">Revenue Channels</h3>
          </div>
          {channels.map(ch => (
            <div key={ch.id} className="flex items-center justify-between py-3 border-b border-[#222] last:border-0">
              <span className="text-sm">{ch.name}</span>
              <Toggle enabled={ch.enabled} onChange={() => toggleChannel(ch.id)} />
            </div>
          ))}
          <div className="mt-6 pt-4 border-t border-[#222]">
            <h4 className="text-sm text-[#a0a0a0] mb-3">Budget Limits</h4>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Token Fund /month</span>
                  <span className="text-[#76b900]">${budget.tokenFund}</span>
                </div>
                <input type="range" min={10} max={200} value={budget.tokenFund}
                  onChange={e => setBudget({ ...budget, tokenFund: +e.target.value })}
                  className="w-full accent-[#76b900]" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Freedom Fund per-purchase limit</span>
                  <span className="text-[#76b900]">${budget.freedomLimit}</span>
                </div>
                <input type="range" min={10} max={200} value={budget.freedomLimit}
                  onChange={e => setBudget({ ...budget, freedomLimit: +e.target.value })}
                  className="w-full accent-[#76b900]" />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="mt-6">
        <h3 className="font-semibold mb-4">Agent Controls</h3>
        <div className="flex flex-wrap gap-3">
          <button onClick={() => showToast('success', 'Configuration saved successfully')}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#76b900] hover:bg-[#5a8f00] text-black rounded-lg font-medium text-sm transition-colors">
            <Save size={16} /> Save Config
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 bg-[#111] hover:bg-[#1a1a1a] border border-[#222] rounded-lg text-sm transition-colors">
            <Play size={16} /> Evolve Now
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 bg-[#111] hover:bg-[#1a1a1a] border border-[#222] rounded-lg text-sm transition-colors">
            <Pause size={16} /> Pause Agent
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 bg-[#111] hover:bg-[#1a1a1a] border border-red-500/30 text-red-400 rounded-lg text-sm transition-colors">
            <RotateCw size={16} /> Restart Agent
          </button>
        </div>
      </GlassCard>
    </section>
  );
}
