#! /bin/sh
set -x -e
cd "$(dirname "$0")/.."
COVER='img/cover.png'
AUTHOR='Mr. Zoat'
TITLE="With This Ring"
DST="ebooks/$(printf %s "$TITLE" | sed 's/[^A-Za-z0-9_-]/_/g')"
mkdir -p "$(dirname "$DST")"
ebook-convert 'eink/index.html' "$DST"_m.mobi --title  "${TITLE} (m)" --authors "$AUTHOR" --cover "$COVER" --max-levels 1 --mobi-keep-original-images
ebook-convert 'eink/index.html' "$DST"_m.epub --title  "${TITLE} (m)" --authors "$AUTHOR" --cover "$COVER" --max-levels 1
ebook-convert 'book/index.html' "$DST".mobi   --title  "${TITLE}"     --authors "$AUTHOR" --cover "$COVER" --max-levels 1 --mobi-keep-original-images
ebook-convert 'book/index.html' "$DST".epub   --title  "${TITLE}"     --authors "$AUTHOR" --cover "$COVER" --max-levels 1
