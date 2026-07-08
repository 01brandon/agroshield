# AgroShield 
### AI-Powered Food Security & Agricultural Intelligence Platform

> Empowering smallholder farmers with real-time intelligence, mobile markets, and AI-driven tools — built for Africa and beyond.

---

## The Problem

Over **700 million people** face chronic hunger globally. Smallholder farmers produce roughly 70% of the world's food yet have zero access to crop disease detection, fair market pricing, weather intelligence, or financial services. AgroShield closes that gap.

---

## What AgroShield Does

A single Django-powered platform with **20 interconnected modules** covering every part of a farmer's working life:

| Module | What It Does |
|---|---|
| Crop Disease Detection | Farmer uploads a photo → Google Vision AI diagnoses the disease → treatment advice in seconds |
| Weather Intelligence | Celery pulls OpenWeatherMap every 3 hours per farm GPS → SMS + push alerts for drought, frost, flood |
| Farmer Marketplace | Live auction and fixed-price listings with M-Pesa Daraja escrow payments |
| Satellite Field Monitoring | Planet API NDVI maps updated every 5 days showing field health |
| Farm Finance Dashboard | P&L per crop season, credit scoring, tax assistant |
| Carbon Credits | Log sustainable practices, earn and sell verified carbon certificates |
| Community Forum | AI co-pilot (OpenAI GPT-4o-mini) + verified agronomist 

---

## Tech Stack

### Backend
- **Django 5** + Django REST Framework
- **PostgreSQL 16** — primary database
- **Redis 7** — caching and message broker
- **Celery** — async task queue
- **Celery Beat** — scheduled tasks (weather, NDVI, campaigns)
- **Django Channels** — WebSockets for live auction and forum

### Frontend
- **HTML5, CSS3, JavaScript** — vanilla, no framework
- **Chart.js** — financial and stat charts
- **Leaflet.js** — geospatial maps
- **Progressive Web App** — offline-first with service worker

### Authentication
- **JWT** (djangorestframework-simplejwt)
- **Google OAuth 2.0** + **Facebook OAuth** via django-allauth
- Role-based access: farmer, buyer, agronomist, NGO, admin

### AI & Machine Learning
- **Google Cloud Vision API** — crop disease detection from photos
- **Vertex AI** — post classifier and price regression
- **OpenAI GPT-4o-mini** — forum AI co-pilot

### Payments
- **M-Pesa Daraja** — STK Push, B2C payout, escrow
- **Flutterwave** — card and mobile money for international buyers

### Cloud & Infrastructure
- **Docker + Docker Compose** — containerised development
- **Google Cloud Run** — production deployment
- **Cloud SQL** — managed PostgreSQL in production
- **Cloud Pub/Sub** — async Vision AI job queue
- **Cloudinary** — image CDN and storage
- **Google Cloud Storage** — satellite imagery backup

### External APIs
| API | Purpose |
|---|---|
| OpenWeatherMap | Hyperlocal weather per farm GPS |
| Planet API | Satellite NDVI field health imagery |
| Twilio | SMS alerts and IVR voice calls |
| Africa's Talking | USSD gateway for feature phones |
| Google Translate | Multilingual forum support |
| Resend | Transactional email |
| Carbon Interface | Carbon sequestration estimates |
| YouTube Data API | Learning academy video management |

### API Documentation & Testing
- **drf-spectacular** — auto-generated OpenAPI 3.0 Swagger UI at `/api/schema/swagger-ui/`
- **Postman** — full collection imported from OpenAPI schema with 3 environments

---

## Project Structure

```
agroshield/
├── apps/
│   ├── accounts/        # custom user model, JWT auth, Google OAuth
│   ├── farms/           # farm registration and management
│   ├── disease/         # crop scan + Google Vision AI
│   ├── weather/         # OpenWeatherMap + alerts + Twilio SMS
│   ├── marketplace/     # listings, auctions, M-Pesa escrew
│   ├── satellite/       # Planet NDVI monitoring
│   ├── forum/           # community forum + OpenAI co-pilot
│   ├── carbon/          # carbon credit logging and verification
│   ├── finance/         # farm ledger and credit scoring
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py          # WebSocket routing
│   └── celery.py
├── templates/           # Django HTML templates
├── static/              # CSS, JS, images
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

## Getting Started

### Prerequisites
- Docker Desktop
- Python 3.12+
- Git

### 1. Clone and set up

```bash
git clone https://github.com/yourusername/agroshield.git
cd agroshield
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Start all services

```bash
docker-compose up --build
```

### 4. Run migrations and create admin

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5. Collect static files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 6. Open the app

| URL | Description |
|---|---|
| `http://localhost:8000/` | Landing page |
| `http://localhost:8000/dashboard/` | Farmer dashboard |
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/api/schema/swagger-ui/` | Swagger API docs |

---

## Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=agroshield_db
DB_USER=agroshield_user
DB_PASSWORD=agroshield_pass
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Google Cloud
GCP_PROJECT_ID=your_project_id
GCP_PUBSUB_TOPIC=agroshield-scans

# M-Pesa
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
MPESA_ENV=sandbox

# Flutterwave
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_key
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_key
FLUTTERWAVE_ENCRYPTION_KEY=your_key

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Resend (email)
RESEND_API_KEY=re_your_key
DEFAULT_FROM_EMAIL=onboarding@resend.dev

# OpenWeatherMap
OPENWEATHER_API_KEY=your_key

# Planet (satellite)
PLANET_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=sk-your_key

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

---

## API Endpoints

The full API is documented at `/api/schema/swagger-ui/`. Key endpoint groups:

```
POST   /api/auth/register/          Register new user
POST   /api/auth/login/             Get JWT tokens
GET    /api/farms/                  List farmer's farms
POST   /api/disease/                Submit crop scan
GET    /api/weather/alerts/         Get weather alerts
GET    /api/marketplace/listings/   Browse all listings
POST   /api/marketplace/escrow/{id}/pay/     Initiate M-Pesa payment
POST   /api/marketplace/escrow/{id}/release/ Release funds to farmer
POST   /api/forum/posts/            Create forum post
POST   /api/forum/posts/{id}/ai_answer/      Get AI co-pilot response
GET    /api/satellite/              Get NDVI readings
POST   /api/carbon/                 Log carbon activity
GET    /api/finance/ledger/summary/ Get P&L summary
```

---

## Scheduled Tasks (Celery Beat)

| Task | Schedule | What It Does |
|---|---|---|
| fetch_weather_for_all_farms | Every 3 hours | Pulls OpenWeatherMap per farm GPS |
| fetch_ndvi_for_all_farms | Every 5 days | Fetches Planet satellite NDVI data |
| check_food_security_risk | Daily at 6am | Generates regional food security alerts |
| send_scheduled_campaigns | Every 30 minutes | Sends pending SMS/push/email campaigns |
| send_alert_emails | Every 15 minutes | Emails farmers about active weather alerts |

---

## Key API Integrations

### M-Pesa Flow
1. Buyer clicks **pay** on an escrow → STK Push sent to phone
2. Buyer enters PIN → Safaricom callback fires
3. Django updates escrow to `held`
4. Farmer confirms delivery → B2C payment released to farmer

### Disease Detection Flow
1. Farmer uploads photo → Cloudinary stores it (unsigned upload preset)
2. Celery task fires → Google Cloud Vision analyses image
3. Labels mapped to disease database → treatment advice returned
4. If confidence < 75% → routed to agronomist for review

### Weather Alert Flow
1. Celery Beat triggers every 3 hours
2. OpenWeatherMap API called per farm GPS
3. Temperature, humidity, wind thresholds checked
4. Alert created → Twilio SMS sent to farmer's phone

---


---

## License

MIT License — see `LICENSE` for details.

---

---

*AgroShield — Django · Python · JavaScript · HTML/CSS · Cloudinary · Google Cloud · OAuth · Docker · M-Pesa · Flutterwave · 25+ APIs · Swagger · Postman*
