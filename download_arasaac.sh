#!/bin/bash

# Korean ARASAAC Dataset Download Script

echo "Downloading Korean ARASAAC dataset..."

# Install gdown if not available
if ! command -v gdown &> /dev/null; then
    echo "Installing gdown..."
    pip install gdown
fi

# Create dataset directory
mkdir -p dataset

# Download tar file
echo "Downloading images.tar..."
gdown 13wFrhP7PbozGnBqIo9Uy4usiK8Ujq42q -O dataset/images.tar

# Extract tar file
echo "Extracting images..."
cd dataset
tar -xf images.tar

# Clean up
rm images.tar

echo "Download completed. Images are in dataset/images/"
echo "Total images: $(ls images/*.png | wc -l)"