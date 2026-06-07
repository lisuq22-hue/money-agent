export default function StatusBadge({ online }: { online: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs
      ${online ? 'bg-[#76b900]/10 text-[#76b900]' : 'bg-red-500/10 text-red-400'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${online ? 'bg-[#76b900] animate-pulse' : 'bg-red-400'}`} />
      {online ? 'Online' : 'Offline'}
    </span>
  );
}
