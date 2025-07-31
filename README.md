# Cybersecurity Portfolio Backend

FastAPI backend for Akshaj's cybersecurity portfolio website.

## Features
- Complete CRUD APIs for portfolio data
- MongoDB integration with proper models
- CORS enabled for frontend integration
- Production-ready deployment configuration

## Tech Stack
- FastAPI
- MongoDB with Motor (async driver)
- Pydantic models
- Python 3.11+

## Environment Variables Required
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=portfolio_db
PORT=8000
```

## API Endpoints
- `GET /api/` - Health check
- `POST /api/seed-data` - Initialize database with portfolio data
- `GET /api/portfolio/{user_id}` - Get complete portfolio
- `GET /api/portfolio/{user_id}/experience` - Get experience data
- `GET /api/portfolio/{user_id}/projects` - Get projects data
- `GET /api/portfolio/{user_id}/skills` - Get skills data
- `GET /api/portfolio/{user_id}/education` - Get education data
- `GET /api/portfolio/{user_id}/certifications` - Get certifications data

## Deployment
This backend is configured for Railway deployment with automatic Python detection.