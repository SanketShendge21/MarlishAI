// PostHog analytics wrapper
// Optional — only active if NEXT_PUBLIC_POSTHOG_KEY is set

const POSTHOG_KEY = typeof window !== 'undefined' 
  ? process.env.NEXT_PUBLIC_POSTHOG_KEY 
  : null;

let posthog = null;

export function initAnalytics() {
  if (!POSTHOG_KEY || typeof window === 'undefined') return;
  
  // Lazy-load PostHog only if key is configured
  import('posthog-js').then((mod) => {
    posthog = mod.default;
    posthog.init(POSTHOG_KEY, {
      api_host: 'https://app.posthog.com',
      autocapture: false,
      capture_pageview: true,
    });
  }).catch(() => {
    // PostHog not installed — analytics disabled silently
  });
}

export function trackEvent(event, properties = {}) {
  if (posthog) {
    posthog.capture(event, properties);
  }
}

export function trackTranslation(source, target, tier, latencyMs) {
  trackEvent('translation', { source, target, tier, latencyMs });
}
