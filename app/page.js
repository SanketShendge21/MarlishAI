import { Header } from './components/ui/Header';
import { Footer } from './components/ui/Footer';
import { TranslatorPanel } from './components/translator/TranslatorPanel';
import { OfflineIndicator } from './components/ui/OfflineIndicator';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen relative overflow-hidden">
      {/* Decorative background blur element */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/20 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-500/20 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none" />

      <Header />
      
      <OfflineIndicator />

      <main className="flex-1 flex flex-col items-center justify-center pt-8 pb-16 relative z-10">
        <TranslatorPanel />
      </main>

      <Footer />
    </div>
  );
}
