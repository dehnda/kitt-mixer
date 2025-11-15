#!/bin/bash

# Build script for Raspberry Pi deployment

echo "Building K.I.T.T. Cocktail Mixer Frontend..."

# Install dependencies
npm install

# Build for production
npm run build

echo "Build complete! Files are in ./build/"
echo ""
echo "To deploy to Raspberry Pi:"
echo "  scp -r build/* pi@YOUR_PI_IP:/home/pi/cocktail-mixer-ui/"
echo ""
echo "Then on the Pi, serve with:"
echo "  cd /home/pi/cocktail-mixer-ui && python3 -m http.server 3000"
