import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center p-4">
      <h2 className="text-4xl md:text-6xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-violet-500">
        Oops!
      </h2>
      <p className="text-xl text-[var(--color-text-secondary)] mb-8">
        This page doesn&apos;t exist.
      </p>
      <Link 
        href="/"
        className="px-6 py-3 rounded-full bg-[var(--color-primary)] text-white font-medium hover:bg-[var(--color-primary-hover)] transition-colors"
      >
        ← Back to Marlish.AI
      </Link>
    </div>
  );
}
