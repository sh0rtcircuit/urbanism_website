#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PHOTOS_DIR="$ROOT_DIR/static/images/photos"
OUT_FILE="$ROOT_DIR/static/data/gallery.json"

mkdir -p "$(dirname "$OUT_FILE")"

{
  echo "["
  first=1
  while IFS= read -r -d '' file; do
    name="$(basename "$file")"
    if [ $first -eq 0 ]; then
      echo ","
    fi
    first=0
    esc_name="${name//\\/\\\\}"
    esc_name="${esc_name//\"/\\\"}"
    echo -n "  {\"file\": \"$esc_name\"}"
  done < <(find "$PHOTOS_DIR" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 | sort -z)
  echo
  echo "]"
} > "$OUT_FILE"

echo "Wrote $OUT_FILE"
