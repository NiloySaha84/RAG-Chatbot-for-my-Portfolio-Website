#!/usr/bin/env bash
# Deploy the portfolio chatbot on a GCP VM (Debian/Ubuntu).
# Run this ON the VM from anywhere: it clones/updates the repo, builds the
# Docker image, starts the container, and verifies health + memory usage.
set -euo pipefail

REPO_URL="https://github.com/NiloySaha84/RAG-Chatbot-for-my-Portfolio-Website.git"
APP_DIR="$HOME/portfolioBot"
IMAGE_NAME="portfolio-bot"
CONTAINER_NAME="portfolio-bot"
PORT=8000

log() { echo -e "\n==> $*"; }

# --- 1. Docker ---------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    log "Docker installed. You may need to log out/in for group changes; using sudo for now."
fi

DOCKER="docker"
if ! docker info >/dev/null 2>&1; then
    DOCKER="sudo docker"
fi

# --- 2. Swap (protects 4GB VM from OOM during build/startup) -----------------
if [ "$(swapon --show --noheadings | wc -l)" -eq 0 ]; then
    log "No swap detected. Creating 2G swapfile to prevent OOM..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
else
    log "Swap already configured."
fi

# --- 3. Get / update the code ------------------------------------------------
if [ -d "$APP_DIR/.git" ]; then
    log "Updating existing repo..."
    git -C "$APP_DIR" pull --ff-only
else
    log "Cloning repo..."
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

# --- 4. Environment file -----------------------------------------------------
if [ ! -f .env ]; then
    cat <<'EOF'
ERROR: .env file not found in the repo directory.

Create it first:
    nano ~/portfolioBot/.env

With contents:
    NVIDIA_API_KEY=your_nvidia_api_key
    REBUILD_VECTOR_DB=false

Then re-run this script.
EOF
    exit 1
fi

if ! grep -q "NVIDIA_API_KEY=" .env; then
    echo "ERROR: NVIDIA_API_KEY missing from .env"
    exit 1
fi

# --- 5. Build ----------------------------------------------------------------
log "Building Docker image (first build can take ~10 min)..."
$DOCKER build -t "$IMAGE_NAME" .

# --- 6. Run ------------------------------------------------------------------
log "Starting container..."
$DOCKER rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
$DOCKER run -d \
    --name "$CONTAINER_NAME" \
    --env-file .env \
    -p "$PORT":8000 \
    --restart unless-stopped \
    --memory=2g \
    --memory-swap=3g \
    "$IMAGE_NAME"

# --- 7. Health check ---------------------------------------------------------
log "Waiting for app to become healthy..."
for i in $(seq 1 30); do
    if curl -fsS "http://localhost:$PORT/health" >/dev/null 2>&1; then
        log "Health check PASSED: http://localhost:$PORT/health"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "Health check FAILED after 150s. Recent logs:"
        $DOCKER logs --tail 50 "$CONTAINER_NAME"
        exit 1
    fi
    sleep 5
done

# --- 8. Memory report --------------------------------------------------------
log "Container resource usage:"
$DOCKER stats --no-stream "$CONTAINER_NAME"

log "Host memory:"
free -h

EXTERNAL_IP=$(curl -fsS -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip" 2>/dev/null || echo "<VM_EXTERNAL_IP>")

log "Deployed. Open: http://$EXTERNAL_IP:$PORT/gradio"
echo "(Make sure a GCP firewall rule allows TCP:$PORT)"
