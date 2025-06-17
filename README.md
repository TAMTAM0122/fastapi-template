# FastAPI Project Structure

This project provides a structured boilerplate for building FastAPI applications, incorporating best practices for maintainability, scalability, and testability. It follows a layered architecture, separating concerns into distinct modules.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point, registers routes and middleware
│   ├── api/                # Controller Layer: Handles HTTP requests and responses
│   │   ├── __init__.py
│   │   └── endpoints/      # Specific API endpoint files
│   │       ├── __init__.py
│   │       └── user.py     # Example: User-related API routes (GET /users, POST /users, etc.)
│   ├── core/               # Core configurations and utilities
│   │   ├── __init__.py
│   │   ├── config.py       # Application settings (database connection, API keys, etc.)
│   │   ├── database.py     # Database connection and session management (SQLAlchemy engine and session)
│   │   └── common/         # Core common components
│   │       ├── __init__.py
│   │       ├── security.py     # Token validation logic (JWT encoding/decoding, dependency injection for current user)
│   │       ├── logger.py       # Logging configuration
│   │       └── middlewares.py  # Custom middleware (e.g., logging middleware)
│   ├── crud/               # Repository Layer (or Data Access Layer): Encapsulates database CRUD operations
│   │   ├── __init__.py
│   │   └── user.py         # Example: CRUD operations for user data (create_user, get_user, update_user, delete_user)
│   ├── models/             # Model Layer (or ORM Models): Defines database table structures
│   │   ├── __init__.py
│   │   └── user.py         # Example: SQLAlchemy ORM model, defines User table
│   ├── schemas/            # Pydantic Schemas: Defines request bodies, response bodies, and data validation models
│   │   ├── __init__.py
│   │   ├── common/         # Common Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   └── base.py     # Unified response base class (e.g., BaseResponse, includes code, message, data)
│   │   ├── user.py         # Example: UserCreate (for user creation requests), UserResponse (for user responses)
│   │   └── token.py        # Example: Token (for JWT responses)
│   └── services/           # Service Layer (or Business Logic Layer): Encapsulates business logic
│       ├── __init__.py
│       └── user.py         # Example: User-related business logic (register user, login, get user details, calls crud layer)
├── tests/                  # Test directory
│   ├── __init__.py
│   └── test_main.py        # Example test file
├── .env                    # Environment variables file (e.g., database connection string)
├── .gitignore              # Git ignore file configuration
├── Dockerfile              # Docker containerization configuration
├── requirements.txt        # Python dependencies list
└── README.md               # Project documentation
```

## Getting Started

### Prerequisites

*   Python 3.9+
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root with the following content:
    ```
    DATABASE_URL="sqlite:///./sql_app.db"
    SECRET_KEY="your-super-secret-key" # Change this to a strong, random key
    ```

### Running the Application

```bash
uvicorn app.main:app --reload
```
The application will be accessible at `http://127.0.0.1:8000`.
You can access the API documentation (Swagger UI) at `http://127.0.0.1:8000/docs` and ReDoc at `http://127.0.0.1:8000/redoc`.

### Running Tests

```bash
pytest
```

## Docker

To build and run the application using Docker:

1.  **Build the Docker image:**
    ```bash
    docker build -t fastapi-project .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 fastapi-project
    ```

The application will be accessible at `http://localhost:8000`.

## API Endpoints (Examples)

*   **POST /users/**: Create a new user.
*   **GET /users/{user_id}**: Retrieve a user by ID (requires authentication).
*   **GET /users/**: Retrieve a list of users (requires authentication).
*   **POST /token**: Obtain an access token for authentication.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.
