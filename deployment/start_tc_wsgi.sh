#!/bin/bash
# Start mod_wsgi-express sidecar for TileCache (/c and /cache).
#
# Mirrors the production iemwsgi_tc daemon:
#   WSGIDaemonProcess iemwsgi_tc processes=1 threads=15

PORT=${1:-9081}

# shellcheck source=/dev/null
source /opt/miniconda3/etc/profile.d/mamba.sh
mamba activate prod

# Force the conda-forge OpenSSL libs to load before the system ones.
# The system httpd that mod_wsgi-express spawns would otherwise resolve
# /lib64/libcrypto.so.3 first, which is too old for pyproj's bundled
# libssl.so.3 (built against OpenSSL 3.6.0).
export LD_PRELOAD="/opt/miniconda3/envs/prod/lib/libcrypto.so.3:/opt/miniconda3/envs/prod/lib/libssl.so.3${LD_PRELOAD:+ $LD_PRELOAD}"

# Directory of this script, used to locate the logging include file.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INCLUDE_FILE="$SCRIPT_DIR/mod_wsgi_logger.conf"

exec mod_wsgi-express start-server \
        /opt/iem/pylib/iemweb/tilecache_dispatch.py \
        --port "$PORT" \
        --processes 1 \
        --threads 15 \
        --server-name iem.local \
        --mount-point / \
        --include-file "$INCLUDE_FILE" \
        --allow-localhost
