#!/bin/bash
# Network readiness check for Node-RED startup
# Ensures internet and local network are accessible before starting Node-RED

set -euo pipefail

MAX_WAIT=60  # Maximum wait time in seconds
SLEEP_INTERVAL=2

echo "🌐 Waiting for network connectivity before starting Node-RED..."

# Wait for internet connectivity (required for Alexa authentication)
echo "  Checking internet connectivity..."
elapsed=0
while ! ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; do
    if [ $elapsed -ge $MAX_WAIT ]; then
        echo "  ⚠️  Warning: Internet not reachable after ${MAX_WAIT}s, proceeding anyway"
        break
    fi
    sleep $SLEEP_INTERVAL
    elapsed=$((elapsed + SLEEP_INTERVAL))
done
echo "  ✅ Internet connectivity confirmed"

# Wait for DNS resolution (required for Alexa pitangui.amazon.com)
echo "  Checking DNS resolution..."
elapsed=0
while ! nslookup amazon.com >/dev/null 2>&1; do
    if [ $elapsed -ge $MAX_WAIT ]; then
        echo "  ⚠️  Warning: DNS not resolving after ${MAX_WAIT}s, proceeding anyway"
        break
    fi
    sleep $SLEEP_INTERVAL
    elapsed=$((elapsed + SLEEP_INTERVAL))
done
echo "  ✅ DNS resolution confirmed"

# Wait for local network (Hubitat hubs)
echo "  Checking local network (Hubitat hubs)..."
elapsed=0
while ! ping -c 1 -W 2 192.168.0.17 >/dev/null 2>&1 || ! ping -c 1 -W 2 192.168.0.18 >/dev/null 2>&1; do
    if [ $elapsed -ge $MAX_WAIT ]; then
        echo "  ⚠️  Warning: Hubitat hubs not reachable after ${MAX_WAIT}s, proceeding anyway"
        break
    fi
    sleep $SLEEP_INTERVAL
    elapsed=$((elapsed + SLEEP_INTERVAL))
done
echo "  ✅ Local network confirmed (Hubitat hubs reachable)"

# Additional settling time for network services
echo "  Waiting 5 seconds for network services to settle..."
sleep 5

echo "✅ Network ready - Node-RED can start safely"
exit 0
