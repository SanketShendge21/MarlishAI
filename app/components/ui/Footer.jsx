export function Footer() {
  return (
    <footer className="fixed bottom-0 left-0 right-0 h-12 flex items-center justify-center text-xs md:text-sm text-[var(--color-text-secondary)] bg-[var(--color-background)]/80 backdrop-blur-sm z-40 border-t border-[var(--color-border)] md:static md:mt-8 md:border-none md:bg-transparent">
      <div className="flex gap-4">
        <span>Built with ❤️ for Indian languages</span>
        <span>•</span>
        <a href="#" className="hover:text-[var(--color-text-primary)] transition-colors">Privacy</a>
        <span>•</span>
        <a href="#" className="hover:text-[var(--color-text-primary)] transition-colors">GitHub</a>
      </div>
    </footer>
  );
}
