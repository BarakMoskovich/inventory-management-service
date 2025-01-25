# Inventory Management Service

This is a FastAPI-based Inventory Management Service that uses PostgreSQL for data storage and Kafka for event-driven updates.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose

### Installation

1. Clone the repository:

```bash
git clone https://github.com/barakmoskovich/inventory-management-service.git
cd inventory-management-service
```

2. Build and run the Docker containers:

```bash
docker-compose up --build
```

3. The API will be available at `http://localhost:8000`

## Testing the Application

### Manual E2E Testing

1. Start the application:
   ```bash
   docker-compose up -d
   ```

2. Run tests manually:
   ```bash
   # Enter the test container
   docker-compose exec test bash

   # Run all tests
   pytest
   ```

### Swagger UI Testing

For interactive API testing:
- Access Swagger UI at `http://localhost:8000/docs`
- Endpoints for manual testing:
  - GET /items
  - GET /items/{id}
  - POST /items
  - PUT /items/{id}
  - DELETE /items/{id}

## Architecture Overview

This application follows a microservices architecture with the following components:

1. **FastAPI Application**: Handles HTTP requests and responses.
2. **PostgreSQL Database**: Stores item data.
3. **Kafka**: Manages event-driven updates for item creation and modification.
4. **Zookeeper**: Coordinates and manages Kafka brokers.
5. **SQLAlchemy**: ORM for database operations.
6. **Pydantic**: Data validation and settings management.

## Project Structure

```
├── app/
│ ├── migrations/
│ │ └── init.sql
│ │
│ ├── core/
│ │ ├── __init__.py
│ │ ├── config.py
│ │ ├── database.py
│ │ └── logger.py
│ │
│ ├── routers/
│ │ ├── __init__.py
│ │ ├── items.py
│ │
│ ├── services/
│ │ ├── __init__.py
│ │ ├── kafka_service.py
│ │ └── items_service.py
│ │
│ ├── services/
│ │ ├── items_service.py
│ │ └── kafka_service.py
│ │
│ ├── __init__.py
│ ├── schemas.py
│ ├── models.py
│ └── main.py
│
├── tests
│ └── test_items_e2e.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The application is structured as follows:
- `app/`: Main application package
  - `migrations/`: Database migration scripts
  - `core/`: Core application configurations
    - `config.py`: Application settings and environment configurations
    - `database.py`: Database connection and session management
    - `logger.py`: Logging configuration
  - `routers/`: API route definitions
  - `services/`: Business logic and external service integrations
  - `schemas.py`: Pydantic models for request/response validation
  - `models.py`: SQLAlchemy database models
  - `main.py`: FastAPI application entry point
- `tests/`: End-to-end tests
  - `test_items_e2e.py`: Tests for inventory API endpoints
- `Dockerfile`: Docker image build instructions
- `docker-compose.yml`: Multi-container Docker application configuration
- `requirements.txt`: Python dependencies
