
# AgroShield

AI-Powered Food Security and Agricultural Intelligence Platform for smallholder farmers across Africa and beyond.

## Overview

AgroShield solves a documented global crisis: over 700 million people face chronic hunger, yet the smallholder farmers who produce 70% of the world's food have zero access to the tools that could help them. AgroShield closes that gap by combining AI crop diagnosis, real-time weather intelligence, a live produce marketplace with M-Pesa escrow, satellite field monitoring, carbon credit logging, and farm finance management into a single platform accessible from any phone.

Production: https://agroshield-production-f5fc.up.railway.app
API Docs: https://agroshield-production-f5fc.up.railway.app/api/schema/swagger-ui/

## Active Modules

| Module | What It Does |
|---|---|
| Crop Disease Detection | Farmer uploads a photo. Gemini 1.5 Flash returns disease name, confidence, treatment with dosage, and organic alternative. |
| Weather Intelligence | OpenWeatherMap data per farm GPS. Temperature, humidity, wind, rainfall, disease risk signal. |
| Farmer Marketplace | Fixed price or auction listings. Buyers bid. M-Pesa STK Push escrow. |
| Community Forum | Post questions, get Gemini AI co-pilot answers, reply, upvote. |
| Satellite Monitoring | Planet API NDVI per farm every 5 days. |
| Carbon Credits | Log agroforestry or cover crop. CO2 auto-calculated and verified. |
| Farm Finance | Income and expense ledger. P&L summary. |
| Account Settings | Update profile, change password. |
| Global Search | Search forum posts, listings, and farms simultaneously. |

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Django 5, Django REST Framework, PostgreSQL, Redis, Celery |
| Frontend | HTML5, CSS3, Vanilla JavaScript, PWA |
| AI | Google Gemini 1.5 Flash, OpenAI GPT-4o fallback |
| Payments | M-Pesa Daraja STK Push and B2C, Flutterwave |
| Storage | Cloudinary, PostgreSQL |
| Deployment | Docker, Railway |
| APIs | OpenWeatherMap, Planet, Twilio, Resend, Gemini, Safaricom Daraja |
| Auth | JWT via simplejwt, Google OAuth via allauth |
| Docs | drf-spectacular, Swagger UI, Postman |

## Project Structure

```
agroshield/
├── apps/
│   ├── accounts/     # user model, JWT auth, profile
│   ├── farms/        # farm GPS management
│   ├── disease/      # Gemini AI crop diagnosis
│   ├── weather/      # OpenWeatherMap
│   ├── marketplace/  # listings, bids, M-Pesa escrow
│   ├── forum/        # community + Gemini co-pilot
│   ├── carbon/       # carbon credit logging
│   ├── finance/      # farm ledger and P&L
│   └── satellite/    # Planet API NDVI
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── asgi.py
├── templates/
├── static/
│   ├── css/
│   └── js/
├── scripts/
│   └── generate_postman.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt## Getting Started

```
```bash
git clone https://github.com/yourusername/agroshield.git
cd agroshield
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

Open http://localhost:8000

## Environment Variables

| Variable | Description |
|---|---|
| SECRET_KEY | Django secret key |
| DEBUG | True for development |
| ALLOWED_HOSTS | Comma-separated hostnames |
| DB_NAME, DB_USER, DB_PASSWORD, DB_HOST | PostgreSQL credentials |
| REDIS_URL | Redis connection URL |
| CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET | Cloudinary |
| GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET | Google OAuth |
| GEMINI_API_KEY | Google Gemini for crop AI and forum co-pilot |
| OPENAI_API_KEY | OpenAI fallback |
| MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, MPESA_PASSKEY | M-Pesa |
| MPESA_ENV | sandbox or production |
| MPESA_CALLBACK_URL | Public URL for Safaricom callbacks |
| FLUTTERWAVE_PUBLIC_KEY, FLUTTERWAVE_SECRET_KEY | Flutterwave |
| TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER | Twilio SMS |
| RESEND_API_KEY | Transactional email |
| OPENWEATHER_API_KEY | Weather data |
| PLANET_API_KEY | Satellite NDVI |


