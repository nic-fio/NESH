#!/usr/bin/env bash
# publish.sh - builds the site of NESH in site/public/ and publishes it to
# https://nesh.nicfio.it (the owner's VPS, user "progetti", /srv/www/nesh.nicfio.it).
#
#   site/publish.sh            build and publish
#   site/publish.sh --build    build only (look at site/public/ first)
#
# The site: the landing page (site/landing/index.html), the two manuals and
# their assets from docs/, the licence as a page, and the downloads of the
# current release (download/: nesh.efi, nesh-usb.img, SHA256SUMS, the licence).
# The downloads are taken from the GitHub release while the repository is
# public; after that, from build/ (make, make usb).
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=$ROOT/site/public
HOST=progetti@57.131.27.241
DEST=/srv/www/nesh.nicfio.it
VERSION=$(sed -n 's/^#define NESH_VERSION "\(.*\)"/\1/p' "$ROOT/src/core/shell.h")
URL=https://nesh.nicfio.it

rm -rf "$OUT"
mkdir -p "$OUT/download" "$OUT/assets/vendor"

cp "$ROOT/site/landing/index.html" "$OUT/index.html"
cp "$ROOT/docs/User Manual.html" "$ROOT/docs/Technical Manual.html" "$OUT/"
cp "$ROOT/docs/assets/vendor/"* "$OUT/assets/vendor/"
python3 "$ROOT/site/licence-page.py" "$ROOT/LICENSE" > "$OUT/licence.html"

# canonical URL, link preview and a search-friendly title for each page
SEO=$ROOT/site/seo-head.py
python3 "$SEO" "$OUT/User Manual.html" "$URL/User%20Manual.html" \
    "NESH User Manual — commands and BASIC scripting for the UEFI shell" \
    "Every command of NESH, the New EFI Shell, and its BASIC scripting language, with examples: files, disks, UEFI variables, boot entries, PCI, SMBIOS, ACPI, network."
python3 "$SEO" "$OUT/Technical Manual.html" "$URL/Technical%20Manual.html" \
    "NESH Technical Manual — architecture and internals of the UEFI shell" \
    "How NESH, the New EFI Shell, is built: architecture, the BASIC interpreter, the UEFI platform layer, testing in QEMU and OVMF."
python3 "$SEO" "$OUT/licence.html" "$URL/licence.html" \
    "NESH Freeware Licence" \
    "NESH is freeware: free to use, also at work, and to give away unchanged; not to sell, modify or include in commercial products."

# downloads of the current release
DL=$OUT/download
if [ -f "$ROOT/build/nesh.efi" ] && [ -f "$ROOT/build/nesh-usb.img" ] && [ "${NESH_FROM_BUILD:-}" = 1 ]; then
    cp "$ROOT/build/nesh.efi" "$ROOT/build/nesh-usb.img" "$DL/"
    (cd "$DL" && sha256sum nesh.efi nesh-usb.img > SHA256SUMS)
    sed 's/$/\r/' "$ROOT/LICENSE" > "$DL/LICENSE.txt"
    sed 's/$/\r/' "$ROOT/NOTICE.md" > "$DL/NOTICE.txt"
else
    CACHE=$ROOT/build/release-v$VERSION
    if [ ! -f "$CACHE/nesh-usb.img" ]; then
        mkdir -p "$CACHE"
        gh release download "v$VERSION" --repo nic-fio/NESH --dir "$CACHE" --clobber
    fi
    cp "$CACHE/nesh.efi" "$CACHE/nesh-usb.img" "$DL/"
    (cd "$DL" && sha256sum nesh.efi nesh-usb.img > SHA256SUMS)
    sed 's/$/\r/' "$CACHE/LICENSE" > "$DL/LICENSE.txt"
    sed 's/$/\r/' "$CACHE/NOTICE.md" > "$DL/NOTICE.txt"
fi

# search engines and link previews
cp "$ROOT/site/og.png" "$OUT/og.png"
cat > "$OUT/robots.txt" <<EOF
User-agent: *
Allow: /
Sitemap: $URL/sitemap.xml
EOF
TODAY=$(date +%F)
{
    echo '<?xml version="1.0" encoding="UTF-8"?>'
    echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for p in "" "User%20Manual.html" "Technical%20Manual.html" "licence.html"; do
        echo "  <url><loc>$URL/$p</loc><lastmod>$TODAY</lastmod></url>"
    done
    echo '</urlset>'
} > "$OUT/sitemap.xml"

echo "built $OUT (version $VERSION):"
(cd "$OUT" && find . -type f -printf '  %p  %s bytes\n' | sort)

[ "${1:-}" = --build ] && exit 0

# the server ends up identical to site/public (no rsync on either side)
tar -C "$OUT" -cf - --mode=u=rwX,go=rX . | ssh "$HOST" "find '$DEST' -mindepth 1 -delete && tar -C '$DEST' -xf - --no-same-owner"
echo "published to $URL"
