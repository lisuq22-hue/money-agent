import { motion } from 'framer-motion';

interface Props { enabled: boolean; onChange: (v: boolean) => void; label?: string; }

export default function Toggle({ enabled, onChange, label }: Props) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
        enabled ? 'bg-[#76b900]' : 'bg-[#333]'
      }`}
    >
      <motion.div
        animate={{ x: enabled ? 20 : 2 }}
        className="absolute top-1 w-4 h-4 bg-white rounded-full"
      />
      {label && <span className="ml-14 text-sm text-[#a0a0a0] whitespace-nowrap">{label}</span>}
    </button>
  );
}
