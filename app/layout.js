import { Inter, Noto_Sans_Devanagari } from 'next/font/google';
import './globals.css';
import { ToastContainer } from '@/app/components/ui/Toast';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  weight: ['400', '500', '600', '700'],
});

const notoSansDevanagari = Noto_Sans_Devanagari({
  subsets: ['devanagari'],
  display: 'swap',
  variable: '--font-noto-sans-devanagari',
  weight: ['400', '500', '600'],
});

export const metadata = {
  title: 'Marlish.AI — Real-Time Indian Language Translator',
  description: 'Free, offline-capable translator for Hinglish, Marlish, English, Hindi, and Marathi. Translate as you type. No sign-up required.',
  keywords: 'Hinglish translator, Marlish translator, Hindi English translator, Marathi translator, Indian language translator, real-time translation, offline translator',
  authors: [{ name: 'Marlish.AI' }],
  creator: 'Marlish.AI',
  metadataBase: new URL('https://marlishai.vercel.app'),
  openGraph: {
    title: 'Marlish.AI — Real-Time Indian Language Translator',
    description: 'Translate Hinglish, Marlish, English, Hindi, Marathi instantly. Free & offline.',
    url: 'https://marlishai.vercel.app',
    siteName: 'Marlish.AI',
    images: [{ url: '/og-image.png', width: 1200, height: 630 }],
    locale: 'en_IN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Marlish.AI — Real-Time Indian Language Translator',
    description: 'Translate Hinglish, Marlish, English, Hindi, Marathi instantly. Free & offline.',
    images: ['/og-image.png'],
  },
  robots: { index: true, follow: true },
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Marlish.AI'
  },
};

export const viewport = {
  themeColor: '#6366f1',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" data-theme="dark" className={`${inter.variable} ${notoSansDevanagari.variable}`}>
      <body className="antialiased min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)]">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "Marlish.AI",
          "description": "Free real-time Indian language translator",
          "applicationCategory": "UtilityApplication",
          "operatingSystem": "Any",
          "offers": { "@type": "Offer", "price": "0", "priceCurrency": "INR" },
          "inLanguage": ["en", "hi", "mr"],
        }) }} />
        {children}
        <ToastContainer />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(
                    function(registration) {
                      console.log('Service Worker registration successful');
                    },
                    function(err) {
                      console.log('Service Worker registration failed: ', err);
                    }
                  );
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
