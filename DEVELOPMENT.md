# State of Forms - Development Guide

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Git (for version control)

### Initial Setup

1. **Install dependencies:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually:
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   Navigate to `http://localhost:4321`

## 📁 Project Structure

```
src/
├── components/
│   ├── Header.astro         # Navigation header
│   ├── Footer.astro         # Site footer
│   └── react/              # React components
│       ├── StockTicker.tsx  # Live stock ticker
│       └── CryptoChart.tsx  # Crypto price chart
├── layouts/
│   └── Layout.astro         # Main page layout
├── pages/                   # Page routes
│   ├── index.astro         # Home page (/)
│   ├── services.astro      # Services page (/services)
│   ├── solutions.astro     # Solutions page (/solutions)
│   ├── portfolio.astro     # Portfolio page (/portfolio)
│   ├── about.astro         # About page (/about)
│   └── contact.astro       # Contact page (/contact)
└── styles/
    └── global.css          # Global styles
```

## 🔧 Integrating React Components

### Using React Components in Astro Pages

Astro components are rendered at build time, while React components can be interactive. Use the `client:*` directives to control when React components load:

```astro
---
import StockTicker from '../components/react/StockTicker';
import CryptoChart from '../components/react/CryptoChart';
---

<!-- Load immediately -->
<StockTicker client:load />

<!-- Load when visible -->
<CryptoChart client:visible symbol="BTC" />

<!-- Load when browser is idle -->
<StockTicker client:idle />
```

### Client Directives:
- `client:load` - Load immediately on page load
- `client:idle` - Load when browser is idle
- `client:visible` - Load when component enters viewport
- `client:media` - Load at specific breakpoint

## 🔗 QueryForge API Integration

### Updating React Components

1. **StockTicker Component** (`src/components/react/StockTicker.tsx`):
   ```typescript
   const fetchStockData = async () => {
     const response = await fetch('https://queryforge.ai/api/stocks');
     const data = await response.json();
     setStocks(data);
   };
   ```

2. **CryptoChart Component** (`src/components/react/CryptoChart.tsx`):
   ```typescript
   const fetchChartData = async (symbol: string, range: string) => {
     const response = await fetch(
       `https://queryforge.ai/api/crypto/${symbol}?range=${range}`
     );
     const data = await response.json();
     setData(data.prices);
   };
   ```

### API Endpoints to Implement

Based on your QueryForge setup, implement these endpoints:

- `GET /api/stocks` - Real-time stock quotes
- `GET /api/crypto/:symbol` - Crypto price data
- `GET /api/charts/:symbol` - Historical chart data

## 🎨 Customization

### Colors & Branding

Edit `src/styles/global.css`:
```css
:root {
  --color-primary: #2563eb;      /* Your brand color */
  --color-secondary: #10b981;    /* Accent color */
  /* ... other variables */
}
```

### Navigation

Edit `src/components/Header.astro` to add/remove menu items:
```javascript
const navItems = [
  { name: 'Home', href: '/' },
  // Add your custom pages here
];
```

### Footer Information

Edit `src/components/Footer.astro` to update:
- Company information
- Social media links
- Contact details

## 📝 Content Updates

### Home Page
Edit `src/pages/index.astro` to update:
- Hero section headline
- Service cards
- QueryForge showcase
- Call-to-action sections

### Adding New Pages

1. Create new file in `src/pages/`:
   ```astro
   ---
   import Layout from '../layouts/Layout.astro';
   ---

   <Layout title="New Page">
     <section class="section">
       <div class="container">
         <h1>New Page</h1>
         <p>Content goes here</p>
       </div>
     </section>
   </Layout>
   ```

2. Add to navigation in `Header.astro`

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` folder with your production-ready site.

### Deploy to DigitalOcean

1. **Create a new Droplet** (Ubuntu recommended)

2. **Install Node.js on the droplet:**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **Install a web server** (nginx or Apache)

4. **Copy the `dist/` folder** to your droplet

5. **Configure web server** to serve the `dist/` folder

6. **Set up GoDaddy DNS:**
   - Add an A record pointing to your droplet's IP
   - Add CNAME for www subdomain

### Alternative: Static Hosting

Since this is a static site, you can also deploy to:
- **Netlify** - `npm run build` then drag & drop `dist/`
- **Vercel** - Connect GitHub repo for automatic deployment
- **GitHub Pages** - Push `dist/` to gh-pages branch

## 🧪 Testing

### Development Testing
```bash
npm run dev
```

### Production Preview
```bash
npm run build
npm run preview
```

## 📊 Environment Variables

For API keys and secrets, create a `.env` file:

```env
PUBLIC_QUERYFORGE_API_URL=https://queryforge.ai/api
PUBLIC_QUERYFORGE_API_KEY=your_api_key_here
```

Access in components:
```javascript
const apiUrl = import.meta.env.PUBLIC_QUERYFORGE_API_URL;
```

## 🐛 Troubleshooting

### React Components Not Loading

Check that you're using the correct client directive:
```astro
<StockTicker client:load />  ✓
<StockTicker />              ✗ (won't be interactive)
```

### Styling Issues

Make sure `global.css` is imported in `Layout.astro`:
```astro
import '../styles/global.css';
```

### Build Errors

Clear cache and reinstall:
```bash
rm -rf node_modules dist .astro
npm install
npm run build
```

## 📚 Additional Resources

- [Astro Documentation](https://docs.astro.build)
- [React Documentation](https://react.dev)
- [QueryForge.ai](https://queryforge.ai) - Your flagship product

## 🆘 Need Help?

- Check the [Astro Discord](https://astro.build/chat)
- Review component examples in this project
- Test QueryForge API endpoints with Postman

---

**Ready to launch!** 🚀
