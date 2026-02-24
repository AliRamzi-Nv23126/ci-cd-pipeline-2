# Flask ToDo App with GitHub Actions CI/CD Pipeline

A complete Flask ToDo application with automated CI/CD pipelines using GitHub Actions.

## Features

- ✅ Full REST API for ToDo management
- ✅ Automated CI workflow (lint + tests on push/PR)
- ✅ Automated CD workflow (Docker build & push on release)
- ✅ Comprehensive test suite with pytest
- ✅ Linting with flake8
- ✅ Docker containerization
- ✅ Health check endpoint

## Project Structure

```
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .github/workflows/
│   ├── ci.yml              # CI pipeline (lint + test)
│   ├── cd.yml              # CD pipeline (DockerHub)
│   └── cd-ecr.yml          # CD pipeline (Amazon ECR)
├── tests/
│   ├── __init__.py
│   └── test_app.py         # Unit tests
└── README.md
```

## Setup Instructions

### Local Development

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd ci-cd-pipeline-2
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Run tests locally:
   ```bash
   pytest tests/ -v --cov=app
   ```

6. Run linting:
   ```bash
   flake8 . --max-line-length=120
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with todos |
| GET | `/health` | Health check |
| GET | `/todos` | Get all todos |
| POST | `/todos` | Create new todo |
| PUT | `/todos/<id>` | Update todo |
| DELETE | `/todos/<id>` | Delete todo |

## GitHub Actions CI/CD

### CI Workflow

Runs automatically on push and PRs to main/dev branches:
- Lint code with flake8
- Run tests with pytest
- Upload coverage reports

### CD Workflow

Runs automatically on GitHub Release publication:
- Build Docker image
- Push to DockerHub with version tag

### Setup GitHub Secrets

For DockerHub CD workflow:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

For ECR CD workflow:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

## Testing

```bash
pytest tests/ -v --cov=app
```

## Docker

```bash
docker build -t todo-app:latest .
docker run -p 5000:5000 todo-app:latest
```

## License

MIT License
