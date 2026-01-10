#!/bin/bash

# Trading System Frontend Deployment Script

set -e

echo "🚀 Starting deployment process..."

# Check if required environment variables are set
if [ -z "$NODE_ENV" ]; then
    export NODE_ENV=production
fi

echo "📦 Environment: $NODE_ENV"

# Install dependencies
echo "📥 Installing dependencies..."
npm ci --only=production

# Run linting
echo "🔍 Running linting..."
npm run lint

# Run type checking
echo "🔧 Running type checking..."
npx tsc --noEmit

# Build the application
echo "🏗️  Building application..."
npm run build

# Run tests if available
if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
    echo "🧪 Running tests..."
    npm test -- --watchAll=false
fi

# Deploy to staging/production
if [ "$NODE_ENV" = "production" ]; then
    echo "🌐 Deploying to production..."
    
    # Add your production deployment commands here
    # Examples:
    # - Push to container registry
    # - Deploy to Kubernetes
    # - Deploy to cloud platform
    
    echo "✅ Production deployment completed!"
else
    echo "🧪 Deploying to staging..."
    
    # Add your staging deployment commands here
    
    echo "✅ Staging deployment completed!"
fi

echo "🎉 Deployment process completed successfully!"