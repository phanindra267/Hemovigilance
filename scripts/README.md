# scripts — Utility Scripts

This folder contains developer utility scripts for the RedLink – Blood Bank Management & Hemovigilance System.

## Available Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| [`setup.sh`](setup.sh) | Linux / macOS | Full development environment setup |
| [`setup.bat`](setup.bat) | Windows | Full development environment setup |
| [`backup_db.sh`](backup_db.sh) | Linux / macOS | PostgreSQL database backup with rotation |
| [`seed_data.sh`](seed_data.sh) | Linux / macOS | Seed the database with demo data |

## Quick Start

**Linux / macOS:**
```bash
chmod +x scripts/setup.sh
bash scripts/setup.sh
```

**Windows:**
```bat
scripts\setup.bat
```

**Docker (any platform):**
```bash
make docker-up
```

> See the root [`Makefile`](../Makefile) for all common developer commands.
