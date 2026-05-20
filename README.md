# CryptoHub — 实时加密货币数据聚合平台

Real-time cryptocurrency data aggregation dashboard with market analytics,
trend tracking, alerts, and membership tiers.

## Live Demo

| Service | URL |
|---------|-----|
| Frontend (Custom Domain) | [cryptohub.dpdns.org](https://cryptohub.dpdns.org) |
| Frontend (Pages.dev) | [crypto-hub-b3f.pages.dev](https://crypto-hub-b3f.pages.dev) |
| Backend API | [crypto-hub-api.onrender.com](https://crypto-hub-api.onrender.com) |
| API Docs (Swagger) | [crypto-hub-api.onrender.com/docs](https://crypto-hub-api.onrender.com/docs) |

## Architecture

```
Browser → Cloudflare Pages (Vue 3 SPA)
               ↓ fetch (REST API)
        Render Web Service (FastAPI + Uvicorn)  ←── Cloudflare Workers (keep-awake cron)
               ↓ SQLAlchemy                              └─ every 5 min ping health endpoint
        Supabase PostgreSQL (IPv4 Connection Pooler)
```

## Tech Stack

### Frontend

| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | Vue 3 (Composition API + `<script setup>`) | 3.5+ |
| Build | Vite | 8.x |
| Language | TypeScript | 6.x, strict |
| CSS | Tailwind CSS | 4.x (`@tailwindcss/vite` plugin) |
| State | Pinia | 3.x |
| Router | Vue Router | 4.x, lazy routes |
| Charts | Chart.js + vue-chartjs / lightweight-charts | TradingView-style candlesticks |

### Backend

| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | FastAPI | 0.115+, auto-docs at `/docs` |
| Server | Uvicorn | 0.30+ |
| ORM | SQLAlchemy | 2.x, declarative models |
| Validation | Pydantic | 2.x |
| Auth | python-jose + passlib | JWT (HS256, 30d expiry), bcrypt |
| Scheduler | APScheduler | AsyncIOScheduler, interval-based |
| HTTP | httpx | Async client for CoinGecko |
| Database | PostgreSQL (psycopg2-binary) | SQLite fallback for local dev |
| Payments | Stripe | Premium monthly ($0.99) & lifetime ($9.90) |

### Data Source

- [CoinGecko API](https://www.coingecko.com/en/api) — market data, trends, alerts
- Crawls 20+ major cryptocurrencies every 5 minutes (configurable)

## Features

| Feature | Free | Premium ($0.99/mo) | Lifetime ($9.90) |
|---------|:----:|:-------------------:|:-----------------:|
| Market Dashboard (real-time) | ✅ | ✅ | ✅ |
| Coin Detail & Search | ✅ | ✅ | ✅ |
| Hot Trends & Alerts | ✅ | ✅ | ✅ |
| New Coin Radar | ✅ | ✅ | ✅ |
| Mock Data Fallback | ✅ | ✅ | ✅ |
| **Interactive OHLC Price Chart** | — | ✅ | ✅ |
| **Theme Switching (Neon Pulse)** | — | ✅ | ✅ |
| **Advanced Multi-Filter** | — | ✅ | ✅ |
| **Custom Strategies** | — | ✅ | ✅ |
| **Ad-Free Experience** | — | ✅ | ✅ |
| **Data Export (CSV)** | — | ✅ | ✅ |
| **API Access (5000 req/day)** | — | — | ✅ |

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Coins

| Method | Path | Description |
|--------|------|-------------|
| GET | `/coins` | List coins (filter by `symbol`, `chain`, `sort_by`, `limit`) |
| GET | `/coins/{id}` | Get coin detail |
| GET | `/market/overview` | Market-wide stats (total cap, volume, BTC dominance) |
| GET | `/new-coins` | Recently listed coins |

### Trends & Alerts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/trends` | Trending coins (filter by `type`, `limit`) |
| GET | `/alerts` | Market alerts (filter by `severity`, `limit`) |

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Get current user profile (requires Bearer token) |
| POST | `/auth/purchase` | Purchase membership plan (requires Bearer token) |

### Payment

| Method | Path | Description |
|--------|------|-------------|
| POST | `/payment/create-checkout-session` | Stripe checkout |
| POST | `/payment/webhook` | Stripe webhook |

## Project Structure

```
crypto-hub/
├── index.html                     # SPA entry point
├── package.json
├── vite.config.ts                 # Vite (vue + tailwind + @ alias)
├── tsconfig.json
│
├── backend/
│   ├── main.py                    # FastAPI app, CORS, startup
│   ├── config.py                  # Pydantic Settings (env-based)
│   ├── database.py                # SQLAlchemy engine + session + migrations
│   ├── models.py                  # ORM models (Coin, Trend, Alert, User, PasswordReset)
│   ├── schemas.py                 # Pydantic request/response
│   ├── crawler.py                 # CoinGecko data crawler (httpx, async)
│   ├── scheduler.py               # APScheduler setup
│   ├── data_seed.py               # Seed / demo data
│   ├── email_utils.py             # Resend email integration
│   ├── requirements.txt
│   └── routers/
│       ├── coins.py               # /api/v1/coins, /chart
│       ├── trends.py              # /api/v1/trends
│       ├── alerts.py              # /api/v1/alerts
│       ├── auth.py                # /api/v1/auth (register, login, forgot/reset password, theme)
│       └── payment.py             # Stripe checkout
│
├── src/
│   ├── main.ts                    # Vue app bootstrap
│   ├── App.vue
│   ├── style.css
│   ├── api/index.ts               # API client (native fetch, 8s timeout)
│   ├── router/index.ts            # 12 lazy-loaded routes
│   ├── stores/crypto.ts           # Pinia store (data + auth + UI)
│   ├── types/index.ts             # TypeScript interfaces
│   ├── data/mock.ts               # Offline mock data
│   ├── components/                # Shared components
│   │   ├── NavBar.vue             #   Nav + user menu + theme panel
│   │   ├── FooterSection.vue
│   │   ├── AppLayout.vue
│   │   ├── StatCard.vue
│   │   ├── HeatScore.vue
│   │   ├── RiskBadge.vue
│   │   ├── AdSlot.vue
│   │   ├── MemberGate.vue          #   Premium content gating
│   │   ├── ThemeSwitcher.vue       #   Premium theme selector
│   │   ├── PriceChart.vue          #   Interactive OHLC chart (lightweight-charts)
│   │   └── ComplianceBanner.vue
│   └── views/
│       ├── HomePage.vue            # Main dashboard
│       ├── CoinDetail.vue          # Per-coin detail view + premium chart
│       ├── TrendsPage.vue          # Trend exploration
│       ├── AdvancedFilter.vue      # Premium multi-filter
│       ├── PricingPage.vue         # Membership plans
│       ├── LoginPage.vue
│       ├── RegisterPage.vue
│       ├── ForgotPassword.vue      # Password reset request
│       ├── ResetPassword.vue       # Password reset form
│       ├── CheckoutPage.vue
│       ├── AboutPage.vue
│       ├── ContactPage.vue
│       └── PrivacyPage.vue
│
├── workers/keep-awake/             # Cloudflare Workers: keep Render alive
│   ├── wrangler.toml               #   Cron trigger: */5 * * * *
│   ├── package.json
│   └── src/index.ts                #   Pings /api/v1/health every 5 minutes
│
└── register_domain.py             # Playwright: auto-register .us.kg domain
```

## Getting Started

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- (Optional) CoinGecko API key for higher rate limits

### Frontend

```bash
# Install dependencies
npm install

# Start dev server on http://localhost:5173
npm run dev

# Build for production
npm run build
```

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
# Create .env file with:
#   DATABASE_URL=sqlite:///./crypto_hub.db
#   COINGECKO_API_KEY=your_key_here
#   JWT_SECRET=your_secret_here
#   STRIPE_SECRET_KEY=sk_test_...

# Start API server on http://localhost:8000
uvicorn backend.main:app --reload
```

The backend auto-generates tables and seeds demo data on first startup.
When the CoinGecko API is unreachable, it falls back to built-in demo data.

### Domain Registration (Free .us.kg)

```bash
# Register a free .us.kg domain via DigitalPlat
export DOMAIN_PASSWORD="your_password"
python3 register_domain.py --headless
```

## Environment Variables

### Backend (set in Render Dashboard)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DATABASE_URL` | `sqlite:///./crypto_hub.db` | No | PostgreSQL URL for production |
| `COINGECKO_API_KEY` | `""` | No | CoinGecko API key (higher rate limit) |
| `CRAWLER_INTERVAL_MINUTES` | `5` | No | Data refresh interval |
| `CORS_ORIGINS` | `http://localhost:5173,...` | No | Allowed CORS origins (生产环境加上所有前端域名) |
| `JWT_SECRET` | dev-only fallback | **Yes (prod)** | JWT signing secret |
| `STRIPE_SECRET_KEY` | `""` | No | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | `""` | No | Stripe webhook signing secret |
| `FRONTEND_URL` | `http://localhost:5173` | No | Frontend URL for Stripe redirects |
| `RESEND_API_KEY` | `""` | No (see below) | Resend API key for password reset emails |
| `APP_URL` | `http://localhost:5173` | No | Frontend URL used in password reset links |

> **注意**: `CORS_ORIGINS` 在 Render Dashboard 设置，包含所有前端域名，例如：
> `https://cryptohub.dpdns.org,https://crypto-hub-b3f.pages.dev,http://localhost:5173`

### Frontend (set in Cloudflare Pages Dashboard)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000` | API 地址，生产环境设为 `https://crypto-hub-api.onrender.com` |

## Deployment

### Frontend → Cloudflare Pages

```bash
npm run build     # outputs to dist/
# Deploy dist/ via Cloudflare Pages dashboard or Wrangler
```

### Backend → Render

1. Push `backend/` to a Git repo
2. Create a new Web Service on Render
3. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables in Render dashboard:

   | 变量 | 值 |
   |------|-----|
   | `CORS_ORIGINS` | `https://cryptohub.dpdns.org,https://crypto-hub-b3f.pages.dev,http://localhost:5173` |
   | `JWT_SECRET` | 随机字符串 |

   > 后端代码中的默认值仅用于本地开发。生产环境的配置（包括 CORS、JWT secret 等）**必须在 Render Dashboard 设置环境变量**，覆盖代码中的默认值。`CORS_ORIGINS` 要包含所有前端域名，否则浏览器会因跨域限制回退到 mock 数据。

### Keep Awake — Prevent Render Free Tier Sleep

Render 免费实例 15 分钟无请求后会自动休眠，导致 APScheduler 爬虫停止。  
使用 Cloudflare Workers Cron Trigger 每 5 分钟 ping health endpoint 保持唤醒。

```bash
cd workers/keep-awake
npx wrangler deploy
```

| 部署信息 ||
|---|---|
| Worker URL | `https://cryptohub-keep-awake.cryptohubwork.workers.dev` |
| Cron | `*/5 * * * *`（每 5 分钟） |
| Ping 目标 | `https://crypto-hub-api.onrender.com/api/v1/health` |
| 超时/重试 | 30s 连接超时 + 90s 总超时 + 5 次重试，应对冷启动 |

### Database → Supabase

1. Create a free Supabase project
2. Copy the PostgreSQL connection string (IPv4 pooler)
3. Set as `DATABASE_URL` on Render

---

## Planned Work

### Short-term
- [ ] Configure **Resend** email sending for password reset (register domain → verify DKIM → set `RESEND_API_KEY`)
- [ ] Add Stripe webhook endpoint for automatic membership upgrades
- [ ] Backend unit tests (pytest)
- [ ] Rate limiting on API endpoints

### Medium-term
- [ ] Portfolio tracking (watchlist, P&L)
- [ ] Price alerts (email/notification when coin hits target)
- [ ] More chart timeframes (15m, 1H, 4H)
- [ ] i18n support (中文 / English toggle)
- [ ] PWA support (offline access, install prompt)

### Long-term
- [ ] WebSocket real-time price updates
- [ ] Social trading signals aggregation
- [ ] Mobile app (React Native / Flutter)
- [ ] Admin dashboard for user management
