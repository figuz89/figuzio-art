# SpeedMonster image hosting

Versioned, immutable artwork for Nuvio SpeedMonster.

- Publish new artwork under art/speedmonster/vNN/<collection>/<folder>/.
- Reuse the original version path for unchanged artwork. Dystopian Worlds originates in v51; the remaining Moods & Vibes artwork originates in v52.
- Keep published version paths and Git history intact. Changed artwork gets a new version path.
- Configuration JSON must reference direct, public HTTPS image URLs pinned to the full publishing commit SHA. Do not embed data/base64 images or use temporary, authenticated, signed or GitHub blob-page URLs.
- Preserve approved bytes, formats, color and alpha. WebP for photographic artwork; PNG for lossless transparent wordmarks.
- Verify every URL with GET, MIME type, full image decoding and SHA-256 before replacing any JSON field.
- Keep a manifest with image paths, dimensions, format, byte count and SHA-256.
- Never publish API tokens, private configuration or credentials to this artwork repository.

This publication adds images and documentation only. It does not enable Pages, change repository access, or change a Nuvio or Oracle server.
