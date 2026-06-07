import { useEffect, useState, useRef } from 'react';

interface Props { end: number; duration?: number; prefix?: string; suffix?: string; decimals?: number; }

export default function CountUp({ end, duration = 1.5, prefix = '', suffix = '', decimals = 0 }: Props) {
  const [value, setValue] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || started.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          started.current = true;
          const startTime = performance.now();
          const tick = (now: number) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / (duration * 1000), 1);
            const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            setValue(end * eased);
            if (progress < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [end, duration]);

  return <span ref={ref} className="tabular-nums">{prefix}{value.toFixed(decimals)}{suffix}</span>;
}
