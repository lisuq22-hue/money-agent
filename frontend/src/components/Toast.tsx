import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, X } from 'lucide-react';

interface ToastData { id: number; type: 'success' | 'error' | 'warning'; message: string; }
let addToastFn: ((t: Omit<ToastData, 'id'>) => void) | null = null;

export function showToast(type: ToastData['type'], message: string) {
  addToastFn?.({ type, message });
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastData[]>([]);
  useEffect(() => {
    addToastFn = (t) => {
      const id = Date.now();
      setToasts(prev => [...prev, { ...t, id }]);
      setTimeout(() => setToasts(prev => prev.filter(x => x.id !== id)), 3000);
    };
  }, []);

  const icons = { success: <CheckCircle size={18} />, error: <XCircle size={18} />, warning: <AlertTriangle size={18} /> };
  const colors = { success: 'border-[#76b900]', error: 'border-red-500', warning: 'border-yellow-500' };

  return (
    <div className="fixed top-20 right-4 z-[100] flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map(t => (
          <motion.div key={t.id} initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 100 }}
            className={`bg-[#111] border ${colors[t.type]} rounded-lg px-4 py-3 flex items-center gap-3 text-sm min-w-[280px]`}>
            <span className={t.type === 'success' ? 'text-[#76b900]' : t.type === 'error' ? 'text-red-400' : 'text-yellow-400'}>
              {icons[t.type]}
            </span>
            {t.message}
            <button className="ml-auto text-[#666] hover:text-white"
              onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}>
              <X size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
