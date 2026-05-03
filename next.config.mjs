/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {},
  
  // Allow all local network origins for dev HMR (fixes CORS errors)
  allowedDevOrigins: ['*'],
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },
};

export default nextConfig;
