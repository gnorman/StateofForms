#!/bin/bash

# State of Forms - Setup Script
echo "🚀 Setting up State of Forms website..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✓ npm found: $(npm --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Success message
echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Run 'npm run dev' to start the development server"
echo "   2. Open http://localhost:4321 in your browser"
echo "   3. Start customizing your site!"
echo ""
echo "📚 Useful commands:"
echo "   npm run dev      - Start development server"
echo "   npm run build    - Build for production"
echo "   npm run preview  - Preview production build"
echo ""
echo "🔗 QueryForge Integration:"
echo "   React components are in src/components/react/"
echo "   Update API endpoints in StockTicker.tsx and CryptoChart.tsx"
echo ""
