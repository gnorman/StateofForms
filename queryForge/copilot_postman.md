
I'll explain how to use Postman with your QueryForge app to test the GET and POST endpoints.

Setting up Postman
    1. Download Postman from postman.com
    2.Create a free account and sign in
    3. Create a new workspace or use the default

Testing Stock GET Request
    1. Click + New → Request
    2. Set up as follows:
        Method: GET
        URL: http://localhost:8000/api/stock/AAPL
        Query Params (optional):
            start_date: 2024-01-01
            end_date: 2024-12-31
            limit: 50
    3. Click Send
    4. View the response in the Body tab
Example with all params:
http://localhost:8000/api/stock/AAPL?start_date=2024-01-01&end_date=2024-12-31&limit=50

Testing Stock POST Request
    1.Click + New → Request
    2. Set up as follows:
        Method: POST
        URL: http://localhost:8000/api/stock/query
    3. Click Body tab → select raw → select JSON
    4. Paste this:
        {
      "symbol": "GOOGL",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "limit": 100
    }
    5. Click Send

Testing Crypto Endpoints (Same Pattern)
Crypto GET:
        GET http://localhost:8000/api/crypto/BTC-USD?limit=50
Crypto POST:
        POST http://localhost:8000/api/crypto/query
    
    {
      "symbol": "ETH-USD",
      "start_date": "2024-01-01",
      "limit": 50
    }
Pro Tips
    Save requests: Right-click → Save as to build a collection for reuse
    Environment variables: Use {{base_url}} for http://localhost:8000 (set in Environments)
    View headers: Check the Headers tab to see auto-generated Content-Type: application/json
    Check status codes:
        200 = Success
        400 = Bad request (invalid dates/params)
        502 = OpenBB API error
                # Extract the tar.gz file (adjust filename if needed)
        tar -xzf Postman-linux-x64-*.tar.gz
        
        # Move to /opt for system-wide access
        sudo mv Postman /opt/
        
        # Create a desktop shortcut (optional but recommended)
        sudo tee /usr/share/applications/postman.desktop > /dev/null <<EOF
        [Desktop Entry]
        Version=1.0
        Type=Application
        Name=Postman
        Exec=/opt/Postman/Postman
        Icon=/opt/Postman/app/resources/icons/icon.png
        Terminal=false
        Categories=Development;
        EOF
        
        # Launch Postman
        /opt/Postman/Postman &500 = Server error

What this does:

Extracts the downloaded file
Moves it to opt so it's accessible system-wide
Creates a desktop application entry (so it shows in your app menu)
Launches Postman in the background
Next steps:

Create a free account or sign in
Create a new workspace
Start testing your API endpoints!
Claude Haiku 4.5 • 0.33x

help me create a new endpoint and test

I'd be happy to help! To create a new endpoint, I need to know what you want it to do. Can you provide:

    1. What should the endpoint do? (e.g., get all queries, delete a query, search by date, etc.)
    2. HTTP method: GET, POST, PUT, DELETE?
    3. URL path: e.g., /api/stock/history or /api/queries
    4. Request parameters: What inputs should it take?
    5. Response: What data should it return?

For example, are you thinking:

    Get all stock queries from the database?
    Compare two symbols?
    Export query history?
    Something else?
    Let me know and I'll help you build and test it in Postman!

It should get all queries HTTP GET URL /api/queries/

Perfect! I'll create a GET endpoint to retrieve all queries from both crypto and stock tables. Let me set this up.

    Created 2 todos

Let me check the main.py to add the new endpoint:

    Read main.py

Now I'll add the new /api/queries/ endpoint to main.py:

main.py+31-0
Perfect! Now restart Docker and test it:
docker compose down
docker compose up --build

Once it's running, here's how to test in Postman:

Testing in Postman:
    1. Create new request
        Method: GET
        URL: http://localhost:8000/api/queries/
    2. Click Send
    3. Expected response:
        {
      "crypto_queries": [
        {
          "id": 1,
          "symbol": "BTC-USD",
          "start_date": "2024-01-01",
          "end_date": "2024-12-31",
          "created_at": "2025-11-13T10:30:45.123456"
        }
      ],
      "stock_queries": [
        {
          "id": 1,
          "symbol": "AAPL",
          "start_date": "2024-01-01",
          "end_date": null,
          "created_at": "2025-11-13T10:25:12.987654"
        }
      ],
      "total_queries": 2,
      "crypto_count": 1,
      "stock_count": 1
    }
In Postman:

    Paste the URL in the URL bar
    Select GET method
    Click Send
    View results in the Body tab

Done! The endpoint now returns all your queries from both tables.
Claude Haiku 4.5 • 0.33x

Should I create a rest API basic collection in Postman?
Yes, absolutely! Creating a Postman collection is a great idea. It will:

✅ Organize all your endpoints in one place
✅ Make testing easier and faster
✅ Let you reuse requests
✅ Allow you to share with teammates
✅ Set up environment variables (like base URL)
Quick steps to create a collection:
Open Postman
Click Collections (left sidebar)
Click + Create New → Collection
Name it: QueryForge API
Click Create
Add your endpoints to the collection:
For each request, after you create it:

Click Save (top right)
Select QueryForge API collection
Give it a folder name like "Stock Endpoints" or just save directly
Recommended structure:
QueryForge API/
├── Health
│   └── GET /ping-db
├── Queries
│   └── GET /api/queries/
├── Stock Endpoints
│   ├── GET /api/stock/{symbol}
│   └── POST /api/stock/query
└── Crypto Endpoints
    ├── GET /api/crypto/{symbol}
    └── POST /api/crypto/query

Bonus: Set up environment variables
    1. Click Environments (left sidebar)
    2. Click + Create
    3. Name it: Local Development
    4. Add variable:
        Variable: base_url
        Initial Value: http://localhost:8000
    5. Save

Then use {{base_url}}/api/stock/AAPL in all requests instead of typing the full URL.

Want me to help you set this up step-by-step, or are you good to go?
Claude Haiku 4.5 • 0.33x