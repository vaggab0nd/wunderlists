#!/bin/bash

# Wunderlists Startup Script

echo "🚀 Starting Wunderlists..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OpenWeather API key!"
    echo "    Get your free API key at: https://openweathermap.org/api"
fi

# Start with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting services with Docker Compose..."
    docker-compose up --build
else
    echo "❌ Docker Compose not found. Please install Docker and Docker Compose."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
