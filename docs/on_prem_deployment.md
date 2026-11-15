# Sketch2STEP Enterprise — On-Premise Deployment Runbook

## 1. Prerequisites & Hardware Sizing

For on-premise air-gapped deployments in enterprise machining and manufacturing plants:

| Component | Minimum Spec | Recommended Enterprise Spec |
| :--- | :--- | :--- |
| **CPU** | 8 Cores (x86_64) | 16+ Cores |
| **RAM** | 16 GB | 32 GB – 64 GB |
| **Disk Storage** | 250 GB NVMe SSD | 1 TB NVMe SSD (RAID-1/10) |
| **OS** | Ubuntu 22.04 LTS / RHEL 9 | Ubuntu 24.04 LTS / Rocky Linux 9 |
| **Container Engine**| Docker 24.0+ & Compose v2 | Docker Engine with containerd |

---

## 2. Air-Gapped Installation Procedure

### Step 1: Transfer Archive
On an internet-connected workstation, pull and export the container images, or transfer the release bundle:
```bash
docker compose -f infra/docker-compose.onprem.yml pull
docker save $(docker compose -f infra/docker-compose.onprem.yml config --images) -o sketch2step_images.tar
```
Transfer `sketch2step_images.tar` and the application repo to the target on-prem server via secure USB or internal repository.

### Step 2: Load Images & Configure Environment
On the target on-prem server:
```bash
docker load -i sketch2step_images.tar
cp .env.example .env
```
Edit `.env` to configure:
- `JWT_SECRET`: Generate with `openssl rand -hex 32`
- `ENCRYPTION_MASTER_KEY`: 32-byte base64 key
- `POSTGRES_PASSWORD`: Strong internal password
- `MINIO_ROOT_PASSWORD`: Strong internal storage password

### Step 3: Launch Stack
```bash
docker compose -f infra/docker-compose.onprem.yml up -d
```

### Step 4: Verify Service Health
```bash
# Check container status
docker compose -f infra/docker-compose.onprem.yml ps

# Inspect API health
curl -f http://localhost:8000/health
```

Access Web UI at `http://<server-ip>:3000` and API docs at `http://<server-ip>:8000/docs`.

---

## 3. Automated Disaster Recovery & Backups

Backups run via cron using `infra/scripts/backup.sh`:
```bash
# Add to crontab for daily execution at 02:00 AM UTC
0 2 * * * cd /opt/sketch2step && ./infra/scripts/backup.sh >> /var/log/sketch2step_backup.log 2>&1
```

Each backup produces a timestamped `.tar.gz` and SHA-256 integrity checksum, automatically rotating backups older than 30 days.
