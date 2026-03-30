#!/bin/bash

echo "Fixing permissions..."
sudo chown -R $USER:$USER data 2>/dev/null || true

echo "Creating pipeline directories..."
mkdir -p data/raw/tweets
mkdir -p data/raw/github
mkdir -p data/raw/hn
mkdir -p data/features
mkdir -p data/results

echo "Patching python scripts..."

for file in scripts/**/*.py scripts/*.py; do
  [ -f "$file" ] || continue

  # Replace ../../data with dynamic root path
  sed -i 's#"\.\./\.\./data#str(PROJECT_ROOT / "data#g' "$file"
  sed -i "s#'\.\./\.\./data#str(PROJECT_ROOT / 'data#g" "$file"

  # Inject PROJECT_ROOT block if not present
  if ! grep -q "PROJECT_ROOT" "$file"; then
    sed -i '1i\
from pathlib import Path\
PROJECT_ROOT = Path(__file__).resolve().parents[2]\
' "$file"
  fi

done

echo "Patch complete."
