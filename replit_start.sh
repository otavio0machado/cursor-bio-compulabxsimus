#!/bin/bash

# Navigate to the app directory
cd biodiagnostico_app || exit 1

# Install dependencies if not already installed (checking a key package)
if ! pip show reflex > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Detect Replit environment and set API_URL
if [ -n "$REPL_ID" ]; then
    echo "Detected Replit environment."

    # Attempt to construct the backend URL.
    # Replit exposes ports at https://<slug>-<port>.<owner>.replit.dev (Newer)
    # or https://<slug>.<owner>.repl.co (Older)
    # The safest bet for Reflex in dev mode on Replit is often to let Reflex handle localhost
    # IF the client is proxying correctly.
    # However, for external access or strict cross-origin, we often need the public URL.

    # Reflex 0.4+ usually binds to 0.0.0.0 if we tell it to.
    # We will export the API_URL so rxconfig.py picks it up.

    # Try to construct the domain for port 8000
    if [ -n "$REPL_SLUG" ] && [ -n "$REPL_OWNER" ]; then
        # New Replit domains style
        export API_URL="https://${REPL_SLUG}-8000.${REPL_OWNER}.replit.dev"
        echo "Setting API_URL to $API_URL"
    fi
fi

# Initialize Reflex (safe to run if already initialized)
reflex init

# Run Reflex
# We run in dev mode by default for "Import from GitHub" experience.
# We bind backend to 0.0.0.0 to ensure it's accessible externally (via Replit proxy).
reflex run --backend-host 0.0.0.0
