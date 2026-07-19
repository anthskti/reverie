# Reverie

Each year, a staggering 92 million tonnes of clothing waste end up in landfills. Fast fashion is the third biggest polluter in the world. It has been shown that upcycling clothes helps the environment by keeping clothes out of landfills. Reverie is an AI-powered app that makes sustainable fashion accessible to everyone and teaches them lifelong skills to help them become more mindful of their fashion footprint.

## Overview

Reverie is built as a backend-first application with a focus on sustainable fashion, upcycling, and ethical marketplace experiences. The API supports authenticated user workflows, AI-driven upcycle creation, inventory management, environmental analytics, and a marketplace for upcycled garments, materials, and tools.

## Project Structure

The backend is organized into a clear separation of concerns:

- `backend/main.py`: FastAPI application instance and router inclusion.
- `backend/core/auth.py`: Auth0 JWT verification dependency with JWKS validation.
- `backend/core/config.py`: Environment variables and configuration.
- `backend/controllers/`: Thin route handlers for each subsystem.
- `backend/services/`: Core business logic and service orchestration.
- `backend/models/`: SQLAlchemy models for items, projects, stats, and listings.
- `backend/repositories/`: Database repositories for inventory, upcycle, and marketplace operations.

## Authentication

User-facing endpoints are protected with Auth0 JWT validation. The backend extracts the Auth0 user ID from the JWT `sub` claim, so clients no longer provide `user_id` in request bodies. When `TESTING=True`, the JWKS validation is bypassed and a mock subject ID is used for local or CI testing.

## API Subsystems

### Analytics

- Endpoint: `GET /api/stats/global`
- Publicly available.
- Aggregates total platform impact metrics such as water saved, CO2 offset, and landfill diverting totals.

### Inventory & Profile

- Base route: `/api/inventory`
- Requires JWT authentication.
- `GET /api/inventory/me/stats`: Fetches environmental impact stats for the authenticated user.
- `GET /api/inventory/me`: Lists physical wardrobe items belonging to the user.
- `GET /api/inventory/{item_id}`: Retrieves a specific item only if it belongs to the user.

### Agentic AI Pipeline

- Base route: `/api/upcycle`
- Requires JWT authentication.
- `POST /api/upcycle/ideate`: Uploads an image, runs AI upcycling concept generation, optionally renders mockups, and creates an item.
- `POST /api/upcycle/execute`: Executes the selected upcycling concept, generates sewing guidance, computes environmental impact metrics, and creates a project.
- `POST /api/upcycle/{item_id}/verify`: Validates a completed garment against the mockup and returns a verification score and feedback.

### Marketplace

- Base route: `/api/marketplace`
- Supports active listing browsing, creation, checkout, and settlement.
- `POST /api/marketplace/list`: Creates marketplace listings for upcycled clothing, materials, or tools.
- `PATCH /api/marketplace/{listing_id}`: Allows sellers to update listing details and cancel listings.
- `GET /api/marketplace`: Fetches active listings with category filtering and keyword search.
- `GET /api/marketplace/{listing_id}`: Retrieves listing details publicly.
- `POST /api/marketplace/checkout/{listing_id}`: Initiates checkout, creates a Unifold session, and places the listing into pending payment.
- `POST /api/marketplace/settle/{listing_id}`: Finalizes the sale after buyer confirmation and triggers payout.

### Webhooks

- Base route: `/api/webhooks`
- No Auth0 token required, but uses HMAC-SHA256 signature verification.
- `POST /api/webhooks/unifold`: Handles Unifold deposit and payout events, updates listing escrow status, and records payout transactions.

## AI & Storage Behavior

- The AI pipeline can run on Vertex AI or Gemini AI Studio.
- Local offline mode stores uploaded images in `static/inventory` when Supabase is unconfigured.
- Generated content includes upcycling concepts, mockups, sewing guides, verification feedback, and environmental impact narratives.

## Goals

Reverie aims to make sustainable fashion approachable by connecting wardrobe management, creative upcycling workflows, environmental impact tracking, and a responsible e-commerce experience in a single system.
