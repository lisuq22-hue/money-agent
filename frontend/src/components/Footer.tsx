export default function Footer() {
  return (
    <footer className="border-t border-[#222] bg-[#0a0a0a] py-8 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-[#666]">
        <div className="flex items-center gap-2">
          <span className="text-[#76b900] font-semibold">MoneyAgent</span>
          <span>v0.1.0</span>
        </div>
        <div className="flex items-center gap-6">
          <span>Powered by Claude Opus 4.8</span>
          <span>|</span>
          <span>MIT License</span>
        </div>
        <span>© 2026 MoneyAgent. All rights reserved.</span>
      </div>
    </footer>
  );
}
