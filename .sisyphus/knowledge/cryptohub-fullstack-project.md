# CryptoHub — Full-Stack Crypto Data Aggregation Platform

## Project Overview

CryptoHub is a real-time cryptocurrency data aggregation platform. It crawls CoinGecko for market data, trends, and alerts, displays them on a dashboard with filtering/analysis, and supports membership tiers with JWT auth.

## Architecture

```
Browser → Cloudflare Pages (Vue 3 SPA)
               ↓ fetch (REST API)
        Render Web Service (FastAPI + Uvicorn)
               ↓ SQLAlchemy
        Supabase PostgreSQL (via IPv4 Connection Pooler)
```

### Deployed Services

| Service | Platform | URL | Cost |
|---|---|---|---|
| Frontend (Vue SPA) | Cloudflare Pages | `https://crypto-hub-b3f.pages.dev` | $0 |
| Backend (FastAPI) | Render Web Service | `https://crypto-hub-api.onrender.com` | $0 (Hobby + free instance) |
| Database | Supabase PostgreSQL | `pooler.supabase.com:6543` (IPv4) | $0 (Free tier, 500MB) |
| Alternate Frontend | Cloudflare Workers | `https://crypto-hub.cryptohubwork.workers.dev` | $0 |

**Note**: Two frontend URLs exist because the project migrated from Workers → Pages during deployment.

---

## 1. Tech Stack

### Frontend

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Framework | Vue 3 | 3.5+ | Composition API + `<script setup>` |
| Build | Vite | 8.x | Fast dev server, tree-shaking |
| Language | TypeScript | 6.x | Strict mode |
| CSS | Tailwind CSS | 4.x | `@tailwindcss/vite` plugin (no PostCSS) |
| State | Pinia | 3.x | One store: `crypto.ts` |
| Router | Vue Router | 4.x | Hash-free `createWebHistory` + lazy routes |
| Charts | Chart.js + vue-chartjs | 4.x/5.x | Dashboard charts |
| Charts (alt) | lightweight-charts | 5.x | TradingView-style charts |

### Backend

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Framework | FastAPI | 0.115+ | ASGI, auto-docs at `/docs` |
| Server | Uvicorn | 0.30+ | Running on Render |
| ORM | SQLAlchemy | 2.x | Declarative models, auto-create tables on startup |
| Validation | Pydantic | 2.x | `BaseSettings` for config |
| Auth | python-jose + passlib | — | JWT (HS256, 30d expiry), bcrypt hashing |
| Scheduler | APScheduler | 3.10+ | AsyncIOScheduler, interval-based |
| HTTP | httpx | 0.27+ | Async HTTP client for CoinGecko |
| DB Driver | psycopg2-binary | 2.9+ | PostgreSQL adapter |

### Key Dependencies (backend/requirements.txt)

```
fastapi, uvicorn[standard], sqlalchemy, httpx, apscheduler,
pydantic, pydantic-settings, python-jose[cryptography],
passlib[bcrypt], bcrypt<4.1, psycopg2-binary
```

### Key Dependencies (package.json)

```
vue, vue-router, pinia, tailwindcss, @tailwindcss/vite,
chart.js, vue-chartjs, lightweight-charts, vite, vue-tsc,
typescript, @vitejs/plugin-vue
```

---

## 2. Project Structure

```
crypto-hub/
├── index.html                     # SPA entry point
├── package.json
├── vite.config.ts                 # Vite config (vue + tailwind alias)
├── tsconfig.json                  # TypeScript config
├── register_domain.py             # Playwright script for .us.kg domain
│
├── backend/
│   ├── main.py                    # FastAPI app, startup, CORS, route registration
│   ├── config.py                  # Pydantic Settings (env-based)
│   ├── database.py                # SQLAlchemy engine + session + graceful fallback
│   ├── models.py                  # Coin, Trend, Alert, User (SQLAlchemy ORM)
│   ├── schemas.py                 # Pydantic request/response models
│   ├── crawler.py                 # CoinGecko data crawler (httpx, async)
│   ├── scheduler.py               # APScheduler job setup (AsyncIOScheduler)
│   ├── requirements.txt
│   └── routers/
│       ├── coins.py               # /api/v1/coins
│       ├── trends.py              # /api/v1/trends
│       ├── alerts.py              # /api/v1/alerts
│       └── auth.py                # /api/v1/auth (register, login, me, purchase)
│
├── src/
│   ├── main.ts                    # Vue app bootstrap
│   ├── api/index.ts               # API client (native fetch, 8s timeout, no Axios)
│   ├── router/index.ts            # 13 routes (lazy loaded, createWebHistory)
│   ├── stores/crypto.ts           # Pinia store (data + auth + UI state)
│   ├── types/index.ts             # TypeScript interfaces
│   ├── data/mock.ts               # Offline mock data fallback
│   ├── components/                # Shared components (NavBar, Footer, AdSlot...)
│   └── views/                     # 11 page components
│
└── .sisyphus/knowledge/
    └── cryptohub-fullstack-project.md
```

---

## 3. Database Models

### Coin (cryptocurrency)
| Field | Type | Description |
|---|---|---|
| id | String PK | CoinGecko ID (e.g. "bitcoin") |
| symbol | String | e.g. "BTC", "ETH" |
| name | String | e.g. "Bitcoin" |
| price | Float | Current price in USD |
| market_cap | Float | Total market cap |
| volume | Float | 24h trading volume |
| change_24h | Float | 24h price change % |
| heat_score | Float | Social/market heat score |
| risk_level | String | "low" / "medium" / "high" |
| chain | String | Blockchain (Bitcoin, Ethereum, Solana...) |

### User
| Field | Type | Description |
|---|---|---|
| id | String (UUID) PK | Auto-generated |
| email | String (unique) | Login email |
| name | String | Display name |
| password_hash | String | bcrypt hash |
| membership | String | "free" / "premium_monthly" / "lifetime" |
| membership_expiry | DateTime | Membership expiration (null for free) |

### Trend / Alert
- **Trend**: Market trends, social heat, media coverage
- **Alert**: Events affecting coins (listing, funding, upgrade, policy)

---

## 4. API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health` | — | Health check |
| GET | `/api/v1/coins` | — | List coins (?symbol=&chain=&sort_by=&limit=) |
| GET | `/api/v1/coins/{id}` | — | Single coin detail |
| GET | `/api/v1/trends` | — | Trending data |
| GET | `/api/v1/alerts` | — | Latest alerts |
| GET | `/api/v1/new-coins` | — | Newly listed coins |
| GET | `/api/v1/market/overview` | — | Market stats summary |
| POST | `/api/v1/auth/register` | — | Register (email, name, password) |
| POST | `/api/v1/auth/login` | — | Login (email, password) |
| GET | `/api/v1/auth/me` | Bearer | Current user profile |
| POST | `/api/v1/auth/purchase` | Bearer | Purchase membership (plan: premium_monthly/lifetime) |

### Auth Flow
1. Register/Login → returns JWT token (HS256, 30-day expiry)
2. Token stored in `localStorage` key `crypto_token`
3. Subsequent requests via `Authorization: Bearer <token>`
4. Purchase updates `membership` field on User row
5. Frontend checks `useCryptoStore().isMember` for ad visibility

### Pricing
| Tier | Price | Notes |
|---|---|---|
| Free | $0 | Default, visible ads |
| Premium Monthly | $0.99 | Ad-free, 30-day expiry |
| Lifetime | $9.90 | Ad-free, expires year 2099 |

---

## 5. Configuration (backend/config.py)

```python
class Settings(BaseSettings):
    database_url: str                    # default: sqlite:///./crypto_hub.db
    coingecko_base_url: str              # https://api.coingecko.com/api/v3
    coingecko_api_key: str               # optional paid API key
    crawler_interval_minutes: int        # default: 5
    cors_origins: str                    # comma-separated, parsed via @property
    jwt_secret: str                      # HS256 signing key

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
```

**Key pattern**: `cors_origins` is `str` (not `list[str]`) to avoid Pydantic env var parsing issues. A `@property` splits by comma for CORS middleware.

---

## 6. CoinGecko Crawler

### Architecture
- **Startup**: `main.py` → `start_scheduler()` → `AsyncIOScheduler`
- **Interval**: 5 minutes (configurable via env `crawler_interval_minutes`)
- **Each tick**: `crawl_market_data()` + `crawl_trending()` in parallel

### API Calls
- `/coins/markets` — price, volume, market cap for TOP_COINS (10 coins)
- `/search/trending` — trending searches
- **Rate limit handling**: 429 with `retry-after` header → skip cycle

### Seed Data
- On first startup: `seed_initial_data()` populates coins with mock data
- Coin metadata (symbol, chain, listing date) defined in `COIN_META` dict
- Risk level computed from price_change, market_cap, holders concentration

### Error Resilience
- Timeout → skip and log
- 429 rate limit → skip this cycle
- Any HTTP error → skip and log
- Never crashes the scheduler

---

## 7. Frontend Architecture

### Routing (13 routes, lazy loaded)
```
/                  → HomePage       (dashboard with market overview)
/coin/:id          → CoinDetail     (single coin detail page)
/trends            → TrendsPage     (market trends feed)
/advanced-filter   → AdvancedFilter (filter/sort coins)
/pricing           → PricingPage    (membership plans)
/login             → LoginPage
/register          → RegisterPage
/checkout/:plan    → CheckoutPage   (payment flow)
/about             → AboutPage
/contact           → ContactPage
/privacy           → PrivacyPage
```

### Pinia Store (`useCryptoStore`)
- **Data state**: coins, trends, alerts, newCoins
- **Auth state**: user, token, isMember
- **UI state**: searchQuery, selectedChain, loading, error, usingMock
- **Actions**: fetchData (coalesced API calls), login, register, logout, purchase, restoreSession
- **Computed**: hotCoins, gainers, losers
- **Membership check**: `isMember` = `user.membership !== 'free'`

### API Client (`src/api/index.ts`)
- Base URL from `import.meta.env.VITE_API_BASE` (fallback: `http://localhost:8000`)
- Simple fetch wrapper (no Axios), 8s timeout via `AbortSignal`
- Returns `null` on any error — no exceptions thrown to components
- Auth endpoints use explicit JSON POST, not the generic `fetchJson`

### Ad Slot
- `AdSlot.vue` checks `useCryptoStore().isMember` — hides for premium/lifetime users
- Show `<slot>` for free users (ads/content)

### Mock Data Fallback
- If API returns null, store falls back to `@/data/mock`
- 10 hardcoded coins with realistic fake prices
- 12 trends across heat/media/community/event types
- `usingMock` ref tracks whether showing real or mock data

---

## 8. Deployment Configuration

### Render Web Service
```
Build Command:  pip install -r backend/requirements.txt
Start Command:  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Plan:           Hobby ($0) + Free instance (512MB RAM, 0.1 CPU)
Note:           Free instance spins down after 15 mins of inactivity
```

### Cloudflare Pages
```
Build Command:  npm install && npm run build
Output Dir:     dist
Root Directory: (leave empty)
```

### Environment Variables

**Render (API Service):**
```
DATABASE_URL=postgresql://postgres.project:password@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
CORS_ORIGINS=https://crypto-hub-b3f.pages.dev,https://crypto-hub.cryptohubwork.workers.dev,http://localhost:5173
JWT_SECRET=<random string, e.g. openssl rand -hex 32>
```

**Cloudflare Pages (Frontend):**
```
VITE_API_BASE=https://crypto-hub-api.onrender.com
```

> **Important**: `VITE_`-prefixed env vars are baked at **build time** by Vite. Changing the value requires a new deployment.

---

## 9. Database Connection (Supabase via IPv4 Pooler)

### Connection Architecture
```
Render Web Service
    ↓ psycopg2 (port 6543)
aws-1-ap-southeast-1.pooler.supabase.com   ← IPv4 only (13.213.241.248)
    ↓
Supabase PgBouncer (connection pool)
    ↓
PostgreSQL (internal network)
```

### Why Pooler (port 6543) Instead of Direct (port 5432)
- **Supabase free tier PostgreSQL has only IPv6** on the direct connection (port 5432)
- Render's IPv6 routing to Supabase is broken ("Network is unreachable")
- **Solution**: Use the Connection Pooler hostname (`*.pooler.supabase.com`) on port **6543**
- Pooler hostname resolves to **IPv4 addresses** (13.213.241.248, 54.179.210.0)
- Format: `postgresql://postgres.<project-ref>:<password>@aws-1-<region>.pooler.supabase.com:6543/postgres`
- The `postgres.<project-ref>` user format is required for pooler auth

### database.py Robustness Patterns
```python
# 1. Fix postgres:// → postgresql:// for SQLAlchemy
if isinstance(db_url, str) and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 2. Fallback on empty/invalid URL
if not db_url or not isinstance(db_url, str) or db_url.strip() in ("", "None"):
    db_url = "sqlite:///./crypto_hub.db"

# 3. Try/except around create_engine for graceful fallback
try:
    engine = create_engine(db_url, ...)
except ArgumentError as e:
    print(f"[startup] Failed: {e}, falling back to SQLite")
    engine = create_engine("sqlite:///./crypto_hub.db", ...)
```

---

## 10. Deployment History & Git Timeline

```
16 commits on main branch:

Chore/Init:
  672b390  chore: initialize project scaffolding
  bbea12a  feat: add backend core (database, models, schemas)
  f081b08  feat: add API routers (coins, trends, alerts, auth)
  44f1b37  feat: add backend services (crawler, scheduler, main)

Frontend:
  54dd5d9  feat: add frontend foundation (router, store, API client)
  7cc977c  feat: add UI components (layout, nav, footer, ads, gates)
  b8c3dc0  feat: add core views (dashboard, coin detail, trends, filter, pricing)
  527fabb  feat: add auth and info pages (login, register, checkout, about, contact, privacy)
  9d3eecd  feat: add registration script, store, API docs page, assets

Deployment + Fixes:
  730e027  chore: configure Render deployment (PostgreSQL, CORS, deps)
  991114a  fix: update CORS origins to Workers frontend URL
  670e242  fix: parse cors_origins from comma-separated env var string
  12f1e86  fix: change cors_origins to string type for env var compat
  da53845  fix: handle empty DATABASE_URL fallback to SQLite
  959780b  fix: add try/except around create_engine + startup logging
  3f3ef56  fix: add crypto-hub-b3f.pages.dev to CORS origins
```

---

## 11. Lessons Learned & Pitfalls

### 1. CORS + Pydantic Settings
**Never** use `cors_origins: list[str]` in Pydantic Settings. Pydantic-Settings cannot reliably parse `list[str]` from plain env var strings, even with `field_validator`. Use `str` type + `@property` to split by comma.

### 2. postgres:// vs postgresql://
Render/Supabase expose `postgres://` URLs, but SQLAlchemy 2.x requires `postgresql://`. Always normalize in `database.py`.

### 3. Empty DATABASE_URL Traps
Pydantic uses env var value even if it's an empty string, overriding the Python default. Must explicitly check:
```python
if not db_url or db_url.strip() in ("", "None"):
    db_url = "sqlite:///./crypto_hub.db"
```

### 4. Startup Logging
Use `print()` with `[startup]` prefix for critical config values. These appear in Render logs even before the logging module is configured.

### 5. Cloudflare Pages ≠ Workers
- **Pages**: Builds from git repo, serves static assets, URL like `*.pages.dev`
- **Workers**: Serverless JS runtime, URL like `*.workers.dev`
- For Vite/SPA deployment: Pages is the right choice

### 6. VITE_ Variables Are Build-Time Only
`import.meta.env.VITE_*` values are baked into the JS bundle at build time. Changing env vars in Cloudflare Pages requires triggering a new deployment (rebuild).

### 7. Supabase Free Tier IPv6 Limitation (CRITICAL)
Supabase free tier PostgreSQL **only has IPv6 DNS records** for direct connections (port 5432). Many cloud providers (Render, Vercel, etc.) have broken IPv6 routing to Supabase.

**Fix**: Use the **Connection Pooler** endpoint:
- Host: `aws-1-<region>.pooler.supabase.com`
- Port: `6543`
- User format: `postgres.<project-ref>` (not just `postgres`)
- This resolves to IPv4 addresses and connects via PgBouncer

**Do NOT use** direct Supabase host (`db.xxx.supabase.co:5432`) from Render — it's IPv6-only and will fail.

### 8. Supabase IS NOT a FastAPI Host
Supabase provides excellent managed PostgreSQL, but its Edge Functions run Deno/JS only — **no Python support**. Cannot replace Render for running a Python/FastAPI backend.

### 9. Database Provider Is Swappable
The same codebase ran on SQLite → Render Postgres → Supabase Postgres without code changes — only the `DATABASE_URL` changed. This is the benefit of using SQLAlchemy ORM.

### 10. API Client Design
Using native `fetch` + `AbortSignal.timeout(8000)` instead of Axios. API functions return `null` on error (never throw), making component code simpler: `const data = await fetchCoins() ?? mockData`.

---

## 12. Development & Testing Commands

```bash
# Local backend dev
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Local frontend dev
npm run dev          # Vite dev server on :5173

# Build frontend
npm run build        # vue-tsc type check + vite build → dist/

# Install backend deps
pip install -r backend/requirements.txt

# Test API health
curl https://crypto-hub-api.onrender.com/api/v1/health

# Test CORS
curl -H "Origin: https://crypto-hub-b3f.pages.dev" \
  -X OPTIONS https://crypto-hub-api.onrender.com/api/v1/coins \
  -D /dev/stderr

# SSH (for git push)
ssh-keygen -t ed25519 -C "your@email.com"
# Add ~/.ssh/id_ed25519.pub to GitHub Settings → SSH Keys
```
