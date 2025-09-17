#!/bin/bash

echo "Downloading Korean ARASAAC dataset..."

if ! command -v gdown &> /dev/null; then
    echo "Installing gdown..."
    pip install gdown
fi

mkdir -p dataset

echo "Downloading images.tar..."
gdown 13wFrhP7PbozGnBqIo9Uy4usiK8Ujq42q -O dataset/images.tar

echo "Extracting images..."
cd dataset
tar -xf images.tar

rm images.tar

echo "Download completed. Images are in dataset/images/"
echo "Total images: $(ls images/*.png | wc -l)"