# Redis Caching Testing Guide for QueryForge

## Overview
This guide demonstrates how to test the Redis caching integration in QueryForge using Postman. You'll observe how repeated queries return cached results with significantly faster response times.

## Prerequisites
- Postman installed and running
- Docker containers running (`docker compose up`)
- Backend API available at `http://localhost:8000`

---

## Test 1: Stock Query with Cache Monitoring

### First Request (Cache Miss)
This request will hit the OpenBB API and store the response in Redis.

**Request Setup:**
```
Method: GET
URL: http://localhost:8000/api/stock/AAPL
Query Parameters:
  - start_date: 2024-01-01
  - end_date: 2024-12-31
  - limit: 50
```

**Expected Behavior:**
- Response time: ~2-5 seconds (first API call to OpenBB)
- Response includes stock data
- Check backend logs: Look for "Fetching stock data for AAPL"
- NO log entry for "Cache HIT"

**Example Full URL:**
```
http://localhost:8000/api/stock/AAPL?start_date=2024-01-01&end_date=2024-12-31&limit=50
```

---

### Second Request (Cache Hit)
Immediately repeat the same request without changes.

**Expected Behavior:**
- Response time: ~50-200ms (served from Redis cache)
- Identical response data
- Check backend logs: Look for "Cache HIT for stock:AAPL:2024-01-01:2024-12-31:50"
- Response is **10-50x faster** than the first request

**Performance Comparison:**
```
First Call:  ~3 seconds (Cache Miss)
Second Call: ~0.1 seconds (Cache Hit) ← 30x faster!
```

---

## Test 2: Crypto Query with Cache Monitoring

### First Request (Cache Miss)
```
Method: GET
URL: http://localhost:8000/api/crypto/BTC-USD
Query Parameters:
  - limit: 50
```

**Expected Behavior:**
- Response time: ~2-5 seconds
- Check logs: "Fetching crypto data for BTC-USD"

### Second Request (Cache Hit)
Repeat the same request.

**Expected Behavior:**
- Response time: ~50-200ms
- Check logs: "Cache HIT for crypto:BTC-USD:None:None:50"

---

## Test 3: POST Request with Caching

### First Request (Cache Miss)
```
Method: POST
URL: http://localhost:8000/api/stock/query
Headers:
  Content-Type: application/json

Body (JSON):
{
  "symbol": "GOOGL",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "limit": 100
}
```

**Expected Behavior:**
- Response time: ~2-5 seconds
- Data returned for GOOGL

### Second Request (Cache Hit)
Send the identical POST request again.

**Expected Behavior:**
- Response time: ~50-200ms (cached)
- Logs show "Cache HIT"

---

## Test 4: Cache Invalidation (Different Parameters)

### Test Cache Isolation
Make requests with slightly different parameters:

**Request A:**
```
http://localhost:8000/api/stock/AAPL?limit=50
```
- Cache Key: `stock:AAPL:None:None:50`

**Request B:**
```
http://localhost:8000/api/stock/AAPL?limit=100
```
- Cache Key: `stock:AAPL:None:None:100`

**Expected Behavior:**
- Both should be cache misses (different cache keys)
- Each will take ~2-5 seconds
- Future requests with matching parameters will use their own cache

**Key Insight:** Cache keys are built from all query parameters, so different parameters = different cache entries.

---

## Test 5: Monitor Cache in Real-Time

### Check Backend Logs
Run this in a terminal to watch logs:
```bash
docker compose logs queryforge_backend -f
```

### What to Look For:
```
Cache SET: stock:AAPL:2024-01-01:2024-12-31:50 (TTL: 3600s)  ← Cache write
Cache HIT for stock:AAPL:2024-01-01:2024-12-31:50             ← Cache read
```

---

## Test 6: Cache Expiration

### Test TTL (Time To Live)
1. Make a stock request → Cache stores result for 1 hour
2. Wait 10+ seconds and check:
   - Repeat request: Should still be cached (Cache HIT)
   - Logs show "Cache HIT" (not a new API call)

3. Optional: Simulate cache expiration
   - You can modify TTL in `cache.py` to a shorter value (e.g., 10 seconds)
   - Make request → Wait 11 seconds → Make request again
   - Second request will be a cache miss (new "Fetching" log)

---

## Test 7: Database Query Logging

### Get All Queries
```
Method: GET
URL: http://localhost:8000/api/queries/
```

**Expected Response:**
```json
{
  "crypto_queries": [...],
  "stock_queries": [...],
  "total_queries": 10,
  "crypto_count": 3,
  "stock_count": 7
}
```

**Note:** This endpoint also benefits from caching (query history is cached)

---

## Performance Comparison Summary

| Scenario | First Call | Repeated Call | Speedup |
|----------|-----------|---------------|---------|
| Stock GET | ~3s | ~0.1s | 30x |
| Crypto GET | ~3s | ~0.1s | 30x |
| Stock POST | ~3s | ~0.1s | 30x |
| Different params | ~3s | ~3s | 1x (new cache) |

---

## Troubleshooting

### Cache Not Working?
1. **Check Redis connection:**
   ```bash
   docker compose logs queryforge_backend | grep "Redis"
   ```
   Look for: `Redis connected successfully at redis://redis:6379`

2. **Verify Redis is running:**
   ```bash
   docker compose exec redis redis-cli ping
   ```
   Should return: `PONG`

3. **Check cache logs:**
   ```bash
   docker compose logs queryforge_backend | grep "Cache"
   ```

### No Cache Hits?
- Make sure you're sending identical requests (exact parameters)
- Check if Redis connection failed (see logs)
- Verify backend restarted successfully

---

## Tips for Best Results

1. **Use Postman Collections:** Save these requests as a collection for easy reuse
2. **Monitor Response Times:** Click "Timeline" in Postman to see detailed timing
3. **Check Network Tab:** Observe the difference between cached and uncached calls
4. **Use "Pre-request Script":** Set up environment variables for base URL
5. **Document Results:** Screenshot response times to show performance gains

---

## Next Steps

- Adjust TTL (time-to-live) values in `cache.py` if needed
- Add cache invalidation endpoints for specific symbols
- Monitor Redis memory usage as cache grows
- Consider cache warming strategies for frequently accessed symbols

