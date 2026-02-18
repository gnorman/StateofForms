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
          `https://queryforge.ai/api/crypto/${symbol}?limit=30`,
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
          <span className="value">${latestPrice.high.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}</span>
        </div>
        <div className="range-item">
          <span className="label">Low</span>
          <span className="value">${latestPrice.low.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}</span>
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

      <div className="crypto-date">
        Last updated: {new Date(latestPrice.date).toLocaleString()}
      </div>

      <div className="chart-footer">
        <small>Powered by queryForge</small>
      </div>
    </div>
  );
}
