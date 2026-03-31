#!/bin/bash
# Start the dedicated Gunicorn backend for TileCache (/c and /cache).
#
# Mirrors the legacy iemwsgi_tc daemon sizing while moving the Python app
# server off Apache.

PORT=${1:-9081}
CONDA_PREFIX=/opt/miniconda3/envs/prod
MAX_REQUESTS=${MAX_REQUESTS:-10000000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-5000}

# Use the conda env's binaries directly rather than relying on interactive
# shell activation (systemd runs non-interactive shells).
export PATH="${CONDA_PREFIX}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"

# Attempt to get some logging when bad things happen
export PYTHONFAULTHANDLER=1
export PYTHONPATH="/opt/iem/pylib/:${PYTHONPATH:-}"

# Keep request-count recycling enabled to cap Python memory leaks. Gunicorn
# rotates individual workers instead of restarting an embedded Apache stack.
exec "${CONDA_PREFIX}/bin/gunicorn" \
        --bind "127.0.0.1:${PORT}" \
        --no-control-socket \
        --workers 3 \
        --worker-class gthread \
        --threads 15 \
        --backlog 2048 \
        --max-requests "$MAX_REQUESTS" \
        --max-requests-jitter "$MAX_REQUESTS_JITTER" \
        --timeout 60 \
        --graceful-timeout 60 \
        --keep-alive 5 \
        --error-logfile - \
        --capture-output \
        --log-level warn \
        iemweb.tilecache_dispatch:application
