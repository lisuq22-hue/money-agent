import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface Props { children: ReactNode; className?: string; hover?: boolean; delay?: number; }

export default function GlassCard({ children, className = '', hover = true, delay = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      whileHover={hover ? { y: -4 } : undefined}
      className={`relative bg-[#111]/80 backdrop-blur-xl border border-[#222] rounded-2xl p-6
        ${hover ? 'hover:border-[#76b900]/30 hover:bg-[#1a1a1a]/80 transition-all duration-300' : ''}
        ${className}`}
    >
      {children}
    </motion.div>
  );
}
