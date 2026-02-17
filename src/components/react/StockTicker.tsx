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
        `https://queryforge.ai/api/stock/${symbol}?limit=30`,
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
