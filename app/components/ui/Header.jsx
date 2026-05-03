import { ThemeToggle } from './ThemeToggle';

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 md:h-16 glass-panel border-x-0 border-t-0 flex items-center justify-between px-4 md:px-6">
      <div className="flex items-center gap-2">
        <div className="font-bold text-xl md:text-2xl tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-violet-500">
          Marlish.AI
        </div>
      </div>
      <div>
        <ThemeToggle />
      </div>
    </header>
  );
}
