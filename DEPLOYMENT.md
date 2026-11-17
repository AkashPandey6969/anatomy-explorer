# Hosting & Deployment Guide

This project is fully prepared for hosting. You can choose any of the deployment options below:

---

## Architecture Overview

- **Frontend**: React 19 + Three.js (`@react-three/fiber`, `@react-three/drei`) built with Vite.
- **Backend**: FastAPI + SQLAlchemy (SQLite default with pre-seeded `anatomy.db`, or PostgreSQL via `DATABASE_URL`).
- **Static 3D Asset**: `ct_derived_human_skeleton.glb` served from frontend static public assets.

---

## Option 1: Split Hosting (Recommended — 100% Free Tier)

Deploy the **Frontend** on Vercel or Netlify and the **Backend** on Render or Railway.

### Step 1: Deploy Backend on Render

1. Go to [Render.com](https://render.com) and click **New + > Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name**: `anatomy-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Add Environment Variables:
   - `PORT`: `10000` (Render sets this automatically)
   - `ALLOWED_ORIGINS`: `*` (or your frontend domain once deployed)
5. Click **Create Web Service**. Once deployed, copy your backend URL (e.g. `https://anatomy-backend.onrender.com`).
6. Test your backend by visiting: `https://anatomy-backend.onrender.com/health`

*(Alternatively, you can use Render's Blueprint feature with the included [render.yaml](file:///render.yaml).)*

---

### Step 2: Deploy Frontend on Vercel

1. Go to [Vercel.com](https://vercel.com) and click **Add New > Project**.
2. Import your GitHub repository.
3. Configure project settings:
   - **Root Directory**: Click "Edit" and select `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   - `VITE_API_URL`: Paste your Render backend URL (e.g. `https://anatomy-backend.onrender.com`)
5. Click **Deploy**.

> **Note**: If deploying on **Netlify** instead of Vercel, the configuration is already included via [netlify.toml](file:///netlify.toml) and [frontend/public/_redirects](file:///frontend/public/_redirects).

---

## Option 2: All-in-One Deployment (Single Service / Container)

If you prefer to deploy everything under **one single URL** (frontend UI + backend API together) without managing two separate services:

The backend is configured to automatically serve the compiled frontend (`frontend/dist`) as a Single Page Application (SPA) whenever the build directory exists.

### Using the Root Dockerfile
You can deploy directly to Railway, Fly.io, Google Cloud Run, or AWS App Runner using the root [Dockerfile](file:///Dockerfile):

1. Platform automatically builds the frontend in Stage 1 and compiles the Python app in Stage 2.
2. The entire application is hosted on a single container port (`PORT` or 8000).
3. The API is accessible at `/api/bones` and `/health`, and the 3D web UI is served at `/`.

---

## Option 3: Self-Hosting with Docker Compose (VPS / Local)

Deploy on any Linux server (DigitalOcean droplet, Hetzner, AWS EC2, Linode) or test locally:

```bash
# Clone the repository
git clone <your-repo-url>
cd bone

# Build and run containers
docker compose up -d --build
```

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Health**: `http://localhost:8000/health`
- **Interactive API Docs**: `http://localhost:8000/docs`

To stop:
```bash
docker compose down
```

---

## Environment Variables Reference

### Backend (`backend/.env`):
| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Port for the Uvicorn server |
| `HOST` | `0.0.0.0` | Host binding interface |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed CORS domains |
| `DATABASE_URL` | SQLite (`anatomy.db`) | Optional PostgreSQL connection string |

### Frontend (`frontend/.env`):
| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | Dev: `http://localhost:8000`, Prod: `''` (relative) | URL of the backend API |

---

## Pre-deployment Verification Checklist

- [x] Backend dependency list (`requirements.txt`) generated.
- [x] Python import path resolution fixed for both root and subfolder execution.
- [x] Relative SQLite path resolved safely to `backend/anatomy.db`.
- [x] Dynamic `DATABASE_URL` (PostgreSQL) support added.
- [x] Dynamic CORS handling (`ALLOWED_ORIGINS`) configured.
- [x] Automatic database seeding on cold start implemented.
- [x] Frontend dynamic API URL (`VITE_API_URL`) integrated.
- [x] Vite dev proxy configured.
- [x] SPA redirect configurations for Vercel (`vercel.json`) and Netlify (`_redirects`, `netlify.toml`).
- [x] Dockerfile, backend Dockerfile, and frontend Nginx setup created.
- [x] Docker Compose configuration verified.
- [x] Render Blueprint (`render.yaml`) created.
