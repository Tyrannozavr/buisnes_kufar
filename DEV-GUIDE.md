# Development Guide

## Local Development Setup (Recommended for Windows)

### Quick Start

Run the following command to start the development environment:

```powershell
.\dev-local.ps1
```

This will:
- Start backend services in Docker (database, RabbitMQ, backend API, Celery workers)
- Start the frontend locally on `http://localhost:3001`

### Manual Setup

If you prefer to start services manually:

**1. Start backend services:**

```powershell
docker-compose -f docker-compose.dev.yml up -d db rabbitmq backend celery-worker celery-beat
```

**2. Wait for services to be ready:**

```powershell
# Check backend health
curl http://localhost:8002/api/health

# View logs if needed
docker-compose -f docker-compose.dev.yml logs -f backend
```

**3. Start frontend locally:**

```powershell
cd frontend
npm install  # First time only
npm run dev
```

Your application will be available at:
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8002
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

---

## Creating a Test User

### Option 1: Quick Test User (Recommended for Development)

Run the automated script:

```powershell
.\create-test-user.ps1
```

This creates a test user with credentials:
- **Email**: `test@example.com`
- **Password**: `Test123!`
- **Company**: Test Company LLC (INN: 1234567890)

### Option 2: Manual Registration (Full Flow)

**Step 1: Register**

1. Go to http://localhost:3001/auth/register
2. Fill in the registration form:
   - First Name, Last Name, Patronymic (optional)
   - Email
   - Phone number
   - Accept terms

3. Get the verification link from backend logs:

```powershell
docker-compose -f docker-compose.dev.yml logs -f backend | Select-String "verification"
```

Look for a URL like:
```
http://localhost:3001/auth/register/complete?token=abc123...
```

**Step 2: Complete Registration**

1. Open the verification link in your browser
2. Enter your company INN (tax ID)
3. Set your password
4. Submit to complete registration

**Step 3: Login**

1. Go to http://localhost:3001/auth/login
2. Enter your email and password
3. You'll be redirected to the dashboard

---

## Authentication System

### How It Works

1. **Registration** (2-step process):
   - Step 1: User submits email, phone, and personal info → email sent with verification link
   - Step 2: User clicks link, enters INN and password → account activated

2. **Login**:
   - User enters email (or phone) and password
   - Backend returns JWT access token
   - Token stored in `access_token` cookie
   - User data stored in Pinia store

3. **Protected Routes**:
   - All `/profile/*` routes require authentication
   - Middleware checks for `isAuthenticated` flag and `access_token` cookie
   - Unauthenticated users redirected to `/auth/login`

### Authentication Components

- **Middleware**: `frontend/middleware/auth.global.ts`
- **User Store**: `frontend/stores/user.ts`
- **Auth API**: `frontend/api/auth.ts`
- **Backend Auth**: `backend/app/api/authentication/`

---

## Working with Authenticated Pages

### Profile Pages (Require Authentication)

All these routes require authentication:

| Route | Description |
|-------|-------------|
| `/profile` | Dashboard |
| `/profile/auth` | Company profile settings |
| `/profile/products` | Manage your products |
| `/profile/announcements` | Your announcements |
| `/profile/announcements/create` | Create new announcement |
| `/profile/announcements/edit/[id]` | Edit announcement |
| `/profile/contracts` | Your contracts |
| `/profile/contracts/editor` | Contract editor |
| `/profile/messages` | Inbox |
| `/profile/messages/new` | New message |
| `/profile/messages/[id]` | View message |
| `/profile/partners` | Your partners |
| `/profile/suppliers` | Your suppliers |
| `/profile/buyers` | Your buyers |
| `/profile/sales` | Sales history |
| `/profile/purchases` | Purchase history |
| `/profile/documents` | Documents |
| `/profile/administration` | Admin panel |

### Public Pages (No Authentication Required)

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/auth/login` | Login |
| `/auth/register` | Registration |
| `/auth/recover-password` | Password recovery |
| `/companies` | Company directory |
| `/companies/[slug]` | Company profile |
| `/announcements` | Announcements list |
| `/announcements/[id]` | Announcement details |
| `/catalog/products` | Product catalog |
| `/catalog/services` | Services catalog |
| `/about` | About page |
| `/terms` | Terms of service |
| `/privacy-policy` | Privacy policy |

---

## Environment Configuration

### Root `.env`

Configuration for Docker services:

```env
# Database
SQLALCHEMY_DATABASE_URL=postgresql://postgres:postgres@db/buisnes_kufar

# Ports
DEV_BACKEND_PORT=8002
DEV_FRONTEND_PORT=3001
DEV_NGINX_PORT=8080

# Frontend API (for local development)
NUXT_DEV_API_PROXY_TARGET=http://localhost:8002

# Backend CORS
BACKEND_CORS_ORIGINS=["http://localhost:3001","http://127.0.0.1:3001"]
```

### Frontend `.env`

Frontend-specific configuration:

```env
# API URL for frontend (uses proxy)
VITE_PUBLIC_API_URL=/api

# Disable font loading
NUXT_UI_FONTS=false
```

---

## Common Tasks

### View Backend Logs

```powershell
docker-compose -f docker-compose.dev.yml logs -f backend
```

### View All Service Logs

```powershell
docker-compose -f docker-compose.dev.yml logs -f
```

### Restart Backend

```powershell
docker-compose -f docker-compose.dev.yml restart backend
```

### Stop All Services

```powershell
docker-compose -f docker-compose.dev.yml down
```

### Database Migrations

```powershell
# Run pending migrations
docker-compose -f docker-compose.dev.yml run --rm migrations poetry run alembic upgrade head

# Create new migration
docker-compose -f docker-compose.dev.yml run --rm migrations poetry run alembic revision --autogenerate -m "Description"
```

### Access Database

```powershell
# Using psql
docker exec -it buisnes_kufar-db-1 psql -U postgres -d buisnes_kufar

# Using pgAdmin or any PostgreSQL client:
# Host: localhost
# Port: 5432 (exposed from db container)
# User: postgres
# Password: postgres
# Database: buisnes_kufar
```

---

## Troubleshooting

### Frontend can't connect to backend

**Check API proxy configuration:**
- Ensure `NUXT_DEV_API_PROXY_TARGET=http://localhost:8002` in root `.env`
- Restart frontend after changing `.env`

**Verify backend is running:**
```powershell
curl http://localhost:8002/api/health
```

### Docker networking errors

**Clean up stale networks:**
```powershell
docker-compose -f docker-compose.dev.yml down
docker network prune -f
docker-compose -f docker-compose.dev.yml up -d
```


### Port already in use

**Find and kill process using the port:**
```powershell
# Find process on port 3000
netstat -ano | findstr :3000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Database connection refused

**Ensure database container is running:**
```powershell
docker-compose -f docker-compose.dev.yml up -d db

# Wait for it to be ready
docker-compose -f docker-compose.dev.yml logs -f db
```

---
