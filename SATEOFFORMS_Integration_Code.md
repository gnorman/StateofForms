# State of Forms - QueryForge Integration Code

## 🚀 Quick Implementation Guide

Copy these exact code snippets to your stateofforms VM to integrate QueryForge API.

**🔥 IMPORTANT - API URL Configuration:**
- **From State of Forms VM (192.168.1.175)**: Use `http://192.168.1.156/api`
- **From QueryForge VM itself**: Use `http://localhost/api`
- **Production (with DNS)**: Use `https://queryforge.ai/api`

**✅ CORS Configuration Applied:**
- QueryForge backend allows requests from `http://localhost:4321`, `http://127.0.0.1:4321`, and `http://192.168.1.175:4321`
- Backend ALLOWED_HOSTS includes IP addresses `192.168.1.156` and `192.168.1.175` for direct IP access
- Nginx properly forwards CORS headers from the backend
- Both development and production configurations updated

**🎉 ALL ISSUES RESOLVED:**
- ✅ CORS headers working
- ✅ IP address access working (no more "Invalid host header" error)
- ✅ Both stock and crypto endpoints tested and working

**📡 Network Setup**:
- QueryForge VM: `192.168.1.156` (nginx on port 80, backend on port 8000)
- State of Forms VM: `192.168.1.175` (Astro dev server on port 4321)

---

## Step 1: Update StockTicker Component

**File**: `/home/gnorm/Documents/stateofforms/src/components/react/StockTicker.tsx`

Replace the entire file with:

```typescript
import { useState, useEffect } from 'react';

interface StockData {
  symbol: string;
  rows: number;
  data: {
    date: string;
    close: number;
    open: number;
    high: number;
    low: number;
    volume: number;
  }[];
}

interface Props {
  symbol?: string;
  refreshInterval?: number; // in milliseconds
}

export default function StockTicker({ symbol = 'AAPL', refreshInterval = 300000 }: Props) {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStockData = async () => {
    try {
      const response = await fetch(
        `http://192.168.1.156/api/stock/${symbol}?limit=30`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch stock data`);
      }

      const data: StockData = await response.json();
      setStockData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stock data');
      console.error('Stock data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchStockData();
    
    // Set up auto-refresh
    const interval = setInterval(fetchStockData, refreshInterval);

    return () => clearInterval(interval);
  }, [symbol, refreshInterval]);

  if (loading && !stockData) {
    return (
      <div className="stock-ticker loading">
        <div className="spinner"></div>
        <p>Loading stock data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-ticker error">
        <p>⚠️ {error}</p>
        <button onClick={fetchStockData}>Retry</button>
      </div>
    );
  }

  if (!stockData || stockData.data.length === 0) {
    return <div className="stock-ticker">No data available for {symbol}</div>;
  }

  // Calculate price change
  const latestPrice = stockData.data[stockData.data.length - 1];
  const priorPrice = stockData.data.length > 1 
    ? stockData.data[stockData.data.length - 2]
    : latestPrice;
  
  const change = latestPrice.close - priorPrice.close;
  const changePercent = priorPrice.close !== 0 
    ? ((change / priorPrice.close) * 100).toFixed(2)
    : '0.00';
  const isPositive = change >= 0;

  return (
    <div className="stock-ticker">
      <div className="stock-header">
        <h3 className="stock-symbol">{stockData.symbol}</h3>
        <span className="data-points">{stockData.rows} data points</span>
      </div>
      
      <div className="stock-price">
        <span className="current-price">${latestPrice.close.toFixed(2)}</span>
      </div>
      
      <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
        <span className="change-amount">
          {isPositive ? '▲' : '▼'} ${Math.abs(change).toFixed(2)}
        </span>
        <span className="change-percent">
          ({isPositive ? '+' : ''}{changePercent}%)
        </span>
      </div>
      
      <div className="stock-details">
        <div className="detail-row">
          <span className="label">Open:</span>
          <span className="value">${latestPrice.open.toFixed(2)}</span>
        </div>
        <div className="detail-row">
          <span className="label">High:</span>
          <span className="value">${latestPrice.high.toFixed(2)}</span>
        </div>
        <div className="detail-row">
          <span className="label">Low:</span>
          <span className="value">${latestPrice.low.toFixed(2)}</span>
        </div>
        <div className="detail-row">
          <span className="label">Volume:</span>
          <span className="value">{latestPrice.volume.toLocaleString()}</span>
        </div>
      </div>
      
      <div className="stock-date">
        Last updated: {new Date(latestPrice.date).toLocaleString()}
      </div>
    </div>
  );
}
```

### Add corresponding CSS

**File**: `/home/gnorm/Documents/stateofforms/src/styles/stock-ticker.css`

```css
.stock-ticker {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 2rem;
  color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.stock-ticker:hover {
  transform: translateY(-5px);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stock-symbol {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.data-points {
  font-size: 0.875rem;
  opacity: 0.8;
}

.stock-price {
  margin: 1.5rem 0;
}

.current-price {
  font-size: 3rem;
  font-weight: bold;
  display: block;
}

.stock-change {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.stock-change.positive {
  color: #4ade80;
}

.stock-change.negative {
  color: #f87171;
}

.stock-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin: 1.5rem 0;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
}

.detail-row .label {
  opacity: 0.8;
}

.detail-row .value {
  font-weight: 600;
}

.stock-date {
  text-align: center;
  font-size: 0.875rem;
  opacity: 0.7;
  margin-top: 1rem;
}

.stock-ticker.loading,
.stock-ticker.error {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stock-ticker.error button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}

.stock-ticker.error button:hover {
  transform: scale(1.05);
}
```

---

## Step 2: Update CryptoChart Component

**File**: `/home/gnorm/Documents/stateofforms/src/components/react/CryptoChart.tsx`

Replace the entire file with:

```typescript
import { useState, useEffect } from 'react';

interface CryptoData {
  symbol: string;
  rows: number;
  data: {
    date: string;
    close: number;
    high: number;
    low: number;
    volume: number;
  }[];
}

interface Props {
  symbol?: string;
}

export default function CryptoChart({ symbol = 'BTC' }: Props) {
  const [cryptoData, setCryptoData] = useState<CryptoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://192.168.1.156/api/crypto/${symbol}?limit=30`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: CryptoData = await response.json();
        setCryptoData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load crypto data');
        console.error('Crypto data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol]);

  if (loading) {
    return <div className="crypto-chart loading">Loading {symbol} data...</div>;
  }

  if (error) {
    return <div className="crypto-chart error">Error: {error}</div>;
  }

  if (!cryptoData || cryptoData.data.length === 0) {
    return <div className="crypto-chart">No data available</div>;
  }

  const latestPrice = cryptoData.data[cryptoData.data.length - 1];
  const oldestPrice = cryptoData.data[0];
  const priceChange = latestPrice.close - oldestPrice.close;
  const priceChangePercent = ((priceChange / oldestPrice.close) * 100).toFixed(2);
  const isPositive = priceChange >= 0;

  // Simple sparkline-style visualization
  const maxPrice = Math.max(...cryptoData.data.map(d => d.high));
  const minPrice = Math.min(...cryptoData.data.map(d => d.low));
  const priceRange = maxPrice - minPrice;

  return (
    <div className="crypto-chart">
      <div className="crypto-header">
        <h3>{cryptoData.symbol}</h3>
        <span className="badge">{cryptoData.rows} days</span>
      </div>

      <div className="crypto-price-display">
        <div className="current-price">
          ${latestPrice.close.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </div>
        <div className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '+' : ''}{priceChangePercent}%
        </div>
      </div>

      <div className="price-range">
        <div className="range-item">
          <span className="label">High</span>
          <span className="value">${latestPrice.high.toFixed(2)}</span>
        </div>
        <div className="range-item">
          <span className="label">Low</span>
          <span className="value">${latestPrice.low.toFixed(2)}</span>
        </div>
      </div>

      <div className="sparkline">
        {cryptoData.data.map((point, index) => {
          const height = priceRange > 0 
            ? ((point.close - minPrice) / priceRange) * 100 
            : 50;
          return (
            <div
              key={index}
              className="sparkline-bar"
              style={{
                height: `${height}%`,
                backgroundColor: isPositive ? '#10b981' : '#ef4444',
              }}
              title={`${point.date}: $${point.close.toFixed(2)}`}
            />
          );
        })}
      </div>

      <div className="chart-footer">
        <small>Powered by QueryForge</small>
      </div>
    </div>
  );
}
```

### Add corresponding CSS

**File**: `/home/gnorm/Documents/stateofforms/src/styles/crypto-chart.css`

```css
.crypto-chart {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 12px;
  padding: 2rem;
  color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.crypto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.crypto-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.crypto-price-display {
  margin-bottom: 1.5rem;
}

.current-price {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.price-change {
  font-size: 1.25rem;
  font-weight: 600;
}

.price-change.positive {
  color: #4ade80;
}

.price-change.negative {
  color: #fca5a5;
}

.price-range {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.range-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.range-item .label {
  font-size: 0.875rem;
  opacity: 0.8;
}

.range-item .value {
  font-size: 1.125rem;
  font-weight: 600;
}

.sparkline {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 80px;
  margin: 1.5rem 0;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.sparkline-bar {
  flex: 1;
  min-width: 2px;
  border-radius: 2px 2px 0 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.sparkline-bar:hover {
  opacity: 0.7;
}

.chart-footer {
  text-align: center;
  opacity: 0.7;
  font-size: 0.875rem;
  margin-top: 1rem;
}

.crypto-chart.loading,
.crypto-chart.error {
  text-align: center;
  padding: 3rem;
}
```

---

## Step 3: Import CSS in Global Styles

**File**: `/home/gnorm/Documents/stateofforms/src/styles/global.css`

Add these imports at the top:

```css
@import url('./stock-ticker.css');
@import url('./crypto-chart.css');
```

---

## Step 4: Update Home Page

**File**: `/home/gnorm/Documents/stateofforms/src/pages/index.astro`

Find the QueryForge showcase section and update it to use real components:

```astro
---
import Layout from '../layouts/Layout.astro';
import StockTicker from '../components/react/StockTicker';
import CryptoChart from '../components/react/CryptoChart';
---

<Layout title="State of Forms - Transform Data Into Decisions">
  <!-- ...existing hero section... -->

  <!-- QueryForge Showcase -->
  <section class="queryforge-showcase">
    <div class="container">
      <h2>Live Demo: Financial Data Powered by QueryForge</h2>
      <p>Real-time stock and cryptocurrency data visualization</p>
      
      <div class="demo-grid">
        <!-- Live Stock Ticker -->
        <div class="demo-widget">
          <StockTicker symbol="AAPL" client:load />
        </div>
        
        <!-- Live Crypto Chart -->
        <div class="demo-widget">
          <CryptoChart symbol="BTC" client:visible />
        </div>
      </div>
      
      <div class="cta-section">
        <a href="https://queryforge.ai" target="_blank" class="btn btn-primary">
          Explore QueryForge Platform →
        </a>
      </div>
    </div>
  </section>

  <!-- ...rest of page... -->
</Layout>

<style>
  .queryforge-showcase {
    padding: 4rem 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  }
  
  .demo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
  }
  
  .cta-section {
    text-align: center;
    margin-top: 3rem;
  }
</style>
```

---

## Step 5: Update Portfolio Page

**File**: `/home/gnorm/Documents/stateofforms/src/pages/portfolio.astro`

Add multiple stock/crypto widgets:

```astro
---
import Layout from '../layouts/Layout.astro';
import StockTicker from '../components/react/StockTicker';
import CryptoChart from '../components/react/CryptoChart';
---

<Layout title="Portfolio - State of Forms">
  <section class="portfolio-hero">
    <h1>Our Portfolio</h1>
    <p>Production-ready data solutions and platforms</p>
  </section>

  <!-- QueryForge Project -->
  <section class="project-showcase">
    <div class="container">
      <h2>QueryForge Platform</h2>
      <div class="project-description">
        <p>
          Full-stack financial data analytics platform powered by OpenBB.
          Features Django frontend, FastAPI backend, PostgreSQL database,
          and Redis caching for real-time stock and cryptocurrency data.
        </p>
      </div>

      <h3>Live Data Demonstration</h3>
      <div class="widgets-grid">
        <StockTicker symbol="AAPL" client:visible />
        <StockTicker symbol="TSLA" client:visible />
        <StockTicker symbol="GOOGL" client:visible />
        <CryptoChart symbol="BTC" client:visible />
        <CryptoChart symbol="ETH" client:visible />
        <CryptoChart symbol="SOL" client:visible />
      </div>

      <div class="tech-stack">
        <h4>Technology Stack</h4>
        <ul>
          <li>Frontend: Django Templates, Bootstrap 5, Chart.js</li>
          <li>Backend: FastAPI, Python 3.11</li>
          <li>Database: PostgreSQL, Redis</li>
          <li>Data: OpenBB Platform API</li>
          <li>Deployment: Docker, DigitalOcean, Nginx</li>
        </ul>
      </div>

      <a href="https://queryforge.ai" target="_blank" class="btn btn-primary">
        Visit QueryForge.ai →
      </a>
    </div>
  </section>

  <!-- ...other projects... -->
</Layout>

<style>
  .widgets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
  }
  
  .tech-stack {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 12px;
    margin: 2rem 0;
  }
  
  .tech-stack ul {
    list-style: none;
    padding: 0;
  }
  
  .tech-stack li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e9ecef;
  }
</style>
```

---

## Step 6: Test the Integration

On your stateofforms VM, run:

```bash
cd /home/gnorm/Documents/stateofforms
npm run dev
```

Visit: `http://localhost:4321`

You should see:
- ✅ Live AAPL stock data on home page
- ✅ Live BTC crypto data on home page
- ✅ Multiple stock/crypto widgets on portfolio page
- ✅ Auto-refresh every 5 minutes
- ✅ Error handling if API is unavailable

---

## 🔧 Troubleshooting

### ALL ISSUES FIXED! ✅
Both CORS and host validation issues have been resolved on QueryForge:
- ✅ Backend CORS_ORIGINS includes `http://localhost:4321`
- ✅ Backend ALLOWED_HOSTS includes `192.168.1.156` (fixes "Invalid host header" error)
- ✅ Nginx properly forwards CORS headers from FastAPI backend
- ✅ Both GET and OPTIONS (preflight) requests work correctly

**Verification**:
```bash
# Test from State of Forms VM:
curl "http://192.168.1.156/api/stock/AAPL?limit=2"
# Should return: HTTP 200 OK with stock data ✅

curl -v "http://192.168.1.156/api/stock/AAPL?limit=1" \
  -H "Origin: http://localhost:4321"
# Should include: Access-Control-Allow-Origin: http://localhost:4321 ✅
```

**If you still see errors:**
1. Make sure QueryForge backend is running:
   ```bash
   curl http://192.168.1.156/api/health
   # Should return: {"status":"healthy",...}
   ```

2. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

3. Clear browser cache and try again

4. Check browser console (F12) for the exact error message

### No Data / Empty Response
Check the QueryForge backend is running:
```bash
curl http://192.168.1.156/api/stock/AAPL?limit=5
```

If using production URL:
```bash
curl https://queryforge.ai/api/stock/AAPL?limit=5
```

### Components Not Rendering
Make sure React integration is installed:
```bash
npm install react react-dom
npm install @types/react @types/react-dom
```

---

## 📊 Customization Options

### Change Refresh Interval
```astro
<StockTicker symbol="AAPL" refreshInterval={60000} client:load />
<!-- Refreshes every 60 seconds instead of 5 minutes -->
```

### Different Symbols
```astro
<StockTicker symbol="MSFT" client:load />
<StockTicker symbol="NVDA" client:load />
<CryptoChart symbol="ETH" client:visible />
<CryptoChart symbol="DOGE" client:visible />
```

### Loading Strategy
- `client:load` - Load immediately on page load
- `client:visible` - Load when component scrolls into view
- `client:idle` - Load when browser is idle

---

## ✅ Verification Checklist

- [ ] StockTicker component updated and styled
- [ ] CryptoChart component updated and styled
- [ ] CSS files created and imported
- [ ] Home page uses live components
- [ ] Portfolio page shows multiple widgets
- [ ] Components load without errors
- [ ] Data displays correctly
- [ ] Auto-refresh works
- [ ] Error states display properly
- [ ] Mobile responsive layout

---

**Ready to deploy?** Run `npm run build` and deploy the `dist/` folder!
