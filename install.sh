#!/bin/bash

echo "🔧 Installing necessary packages..."
sudo apt-get update
sudo apt-get install -y curl npm


echo "📦 Cloning Mobius repository..."
git clone https://github.com/IoTKETI/Mobius.git
cd Mobius

echo "📌 Installing npm dependencies..."
sudo npm install
sudo npm audit fix --force
cd ..

echo "🚢 Starting Mobius Docker containers..."
docker compose up --no-start

echo -e "\n===========Result of Mobius Docker install==============\n"
docker compose ps
echo -e "\n========================================================\n"
