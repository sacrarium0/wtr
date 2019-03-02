#! /bin/sh
set -x -e
cd "$(dirname "$0")/.."
python scripts/with_this_ring.py 
sh scripts/to_epub_mobi.sh 
git add book/* ebooks/* eink/* img/* scripts/* index.html 
git config user.name sacrarium0
git config user.email sacrarium0@sacrarium0
git commit --amend -C @
git push -f origin @:gh-pages 
