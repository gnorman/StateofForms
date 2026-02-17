import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  site: 'https://stateofforms.com',
  // No base path needed for custom domain
  // Enable server-side rendering if needed for API calls
  output: 'static', // Change to 'server' if you need SSR
});
