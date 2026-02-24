# GitHub Actions CI/CD Pipeline - Complete Documentation

## Overview

This document provides complete implementation details for the Flask ToDo App's automated CI/CD pipeline using GitHub Actions.

---

## Part A: Continuous Integration (CI) Workflow

### File: `.github/workflows/ci.yml`

The CI workflow automates code quality checks and testing on every push and pull request.

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8

      - name: Lint with flake8
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
          flake8 . --count --exit-zero --max-line-length=120 --statistics

      - name: Run tests with pytest
        run: |
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

### CI Workflow Triggers

- **Push to branches**: `main`, `dev`
- **Pull Requests to branches**: `main`, `dev`

### CI Workflow Steps

1. **Checkout code** (`actions/checkout@v4`)
   - Downloads the repository code

2. **Set up Python** (`actions/setup-python@v5`)
   - Installs Python 3.11

3. **Install dependencies**
   - Upgrades pip
   - Installs packages from `requirements.txt`
   - Installs testing and linting tools: pytest, pytest-cov, flake8

4. **Lint with flake8**
   - First check: Stops build on syntax errors (E9, F63, F7, F82)
   - Second check: Reports all issues with max line length 120

5. **Run tests with pytest**
   - Runs all tests in `tests/` directory
   - Generates coverage report in XML format

6. **Upload coverage reports**
   - Uploads to Codecov for tracking code coverage over time

### Expected Output

```
Workflow triggers:
✅ Push to main
✅ Push to dev
✅ PR to main
✅ PR to dev

Steps executed:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Lint check: PASS/FAIL
5. Test run: ALL PASSED
6. Coverage uploaded
```

---

## Part B: Continuous Deployment (CD) Workflow

### File: `.github/workflows/cd.yml` (DockerHub)

The CD workflow builds and pushes Docker images to DockerHub on GitHub Release publication.

```yaml
name: CD

on:
  release:
    types: [published]

jobs:
  build-push:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract version from tag
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "VERSION=${VERSION}" >> $GITHUB_OUTPUT
          echo "Extracted version: ${VERSION}"

      - name: Build and push to DockerHub
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/todo-app:${{ steps.version.outputs.VERSION }}
            ${{ secrets.DOCKERHUB_USERNAME }}/todo-app:latest
          cache-from: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/todo-app:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/todo-app:buildcache,mode=max

      - name: Image pushed successfully
        run: |
          echo "Docker image successfully pushed to DockerHub"
          echo "Image: ${{ secrets.DOCKERHUB_USERNAME }}/todo-app:${{ steps.version.outputs.VERSION }}"
          echo "Latest tag: ${{ secrets.DOCKERHUB_USERNAME }}/todo-app:latest"
```

### CD Workflow Triggers

- **Release published**: When you create and publish a GitHub Release

### CD Workflow Steps

1. **Checkout code** (`actions/checkout@v4`)
   - Downloads the repository code

2. **Set up Docker Buildx** (`docker/setup-buildx-action@v3`)
   - Enables advanced Docker build features

3. **Log in to DockerHub** (`docker/login-action@v3`)
   - Authenticates using secrets:
     - `DOCKERHUB_USERNAME`
     - `DOCKERHUB_TOKEN`

4. **Extract version from tag**
   - Parses git tag (e.g., `v1.0.0` → `1.0.0`)
   - Stores in output variable `VERSION`

5. **Build and push to DockerHub** (`docker/build-push-action@v5`)
   - Builds Docker image from `Dockerfile`
   - Pushes with two tags:
     - Version tag: `username/todo-app:1.0.0`
     - Latest tag: `username/todo-app:latest`
   - Uses registry cache for faster builds

6. **Image pushed successfully**
   - Logs confirmation message

### Version Tag Format

Release tags must follow this format: `v{VERSION}`

Examples:
- `v1.0.0` → pushed as `username/todo-app:1.0.0`
- `v0.2.1` → pushed as `username/todo-app:0.2.1`

---

## Alternative: Amazon ECR CD Workflow

### File: `.github/workflows/cd-ecr.yml`

For AWS ECR instead of DockerHub:

```yaml
name: CD-ECR

on:
  release:
    types: [published]

jobs:
  build-push:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Log in to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Extract version from tag
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "VERSION=${VERSION}" >> $GITHUB_OUTPUT
          echo "Extracted version: ${VERSION}"

      - name: Build and push to Amazon ECR
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs.registry }}/todo-app:${{ steps.version.outputs.VERSION }}
            ${{ steps.login-ecr.outputs.registry }}/todo-app:latest
          cache-from: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/todo-app:buildcache
          cache-to: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/todo-app:buildcache,mode=max

      - name: Image pushed successfully to ECR
        run: |
          echo "Docker image successfully pushed to Amazon ECR"
          echo "Image: ${{ steps.login-ecr.outputs.registry }}/todo-app:${{ steps.version.outputs.VERSION }}"
```

---

## GitHub Secrets Configuration

### For DockerHub CD Workflow

Navigate to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value | How to Get |
|------------|-------|-----------|
| `DOCKERHUB_USERNAME` | Your DockerHub username | DockerHub account |
| `DOCKERHUB_TOKEN` | DockerHub access token | DockerHub → Account Settings → Security → New Access Token (select read/write permissions) |

### For Amazon ECR CD Workflow

Navigate to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value | How to Get |
|------------|-------|-----------|
| `AWS_ACCESS_KEY_ID` | AWS access key ID | AWS Console → IAM → Users → Your User → Security Credentials → Access Keys |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | AWS Console → IAM (shown only once during creation) |
| `AWS_REGION` | AWS region code | e.g., `us-east-1`, `eu-west-1` |

### Creating DockerHub Access Token

1. Go to https://hub.docker.com
2. Click your username → **Account Settings**
3. Click **Security** tab
4. Click **New Access Token**
5. Enter a name (e.g., "GitHub Actions")
6. Select **Read, Write & Delete** permissions
7. Click **Generate**
8. Copy the token (shown only once)
9. Add to GitHub as `DOCKERHUB_TOKEN` secret

### Creating AWS IAM Access Keys

1. Go to AWS Console → IAM
2. Click **Users** → Select your user
3. Click **Security credentials** tab
4. Click **Create access key**
5. Select **Command Line Interface (CLI)**
6. Acknowledge the warning and click **Create access key**
7. Copy the **Access Key ID** and **Secret Access Key**
8. Add to GitHub as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

---

## Complete End-to-End Flow

### Step 1: Feature Development

1. Create feature branch from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/new-endpoint
   ```

2. Make changes and commit:
   ```bash
   # Edit files
   git add .
   git commit -m "Add new endpoint"
   git push origin feature/new-endpoint
   ```

3. CI workflow runs automatically:
   - ✅ Code is linted
   - ✅ Tests run
   - ✅ Coverage reported

### Step 2: Code Review

1. Create Pull Request: `feature/new-endpoint` → `dev`
2. CI workflow runs again on PR
3. Review and merge to `dev`

### Step 3: Prepare Release

1. Create PR: `dev` → `main`
2. CI workflow runs
3. Review and merge to `main`

### Step 4: Publish Release

1. Go to GitHub → **Releases**
2. Click **Create a new release**
3. Fill in:
   - Tag version: `v1.0.0` (must start with `v`)
   - Release title: "Version 1.0.0"
   - Release notes: Describe changes
4. Click **Publish release**

### Step 5: Automated Deployment

CD workflow automatically:
1. Checks out code
2. Builds Docker image
3. Logs into registry (DockerHub or ECR)
4. Pushes image with version tag and "latest" tag
5. Logs completion

---

## Monitoring Workflow Runs

### View Workflow Dashboard

1. Go to Repository → **Actions** tab
2. See all workflow runs
3. Click on a run to see details

### Successful CI Run

```
✅ Checkout code
✅ Set up Python 3.11
✅ Install dependencies
✅ Lint with flake8
✅ Run tests with pytest
✅ Upload coverage reports
```

### Successful CD Run

```
✅ Checkout code
✅ Set up Docker Buildx
✅ Log in to DockerHub
✅ Extract version from tag
✅ Build and push to DockerHub
✅ Image pushed successfully
```

### Troubleshooting Failed Runs

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | Add to `requirements.txt` |
| `flake8` errors | Code style issues | Fix according to error message |
| `pytest` failures | Test failures | Debug test code |
| `Login failed` | Wrong secrets | Verify secret names and values |
| `CD not triggering` | Tag format wrong | Use `v1.0.0` format exactly |
| `image not found in registry` | Build failed silently | Check workflow logs for build errors |

---

## File Structure Recap

```
.github/workflows/
├── ci.yml          # Runs on push/PR to lint and test
├── cd.yml          # Runs on release to build and push (DockerHub)
└── cd-ecr.yml      # Alternative: build and push to ECR

app.py             # Flask application
requirements.txt   # Python dependencies
Dockerfile         # Container specification
tests/
├── __init__.py
└── test_app.py    # Unit tests
```

---

## Key Learnings

1. **CI/CD Automation**: Automates repetitive tasks (testing, linting, building)
2. **Quality Gates**: Ensures code meets standards before merge
3. **Secrets Management**: Never commit credentials; use GitHub Secrets
4. **Git Workflow**: Feature branches → dev → main → release
5. **Containerization**: Docker images tagged with version info
6. **Triggering Workflows**: Different events (push, PR, release)

---

## Reference: Example Release Command

```bash
# Create and push a new release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Then publish it on GitHub (or let workflow auto-detect)
```

Or use GitHub CLI:

```bash
gh release create v1.0.0 --title "Version 1.0.0" --notes "Release notes here"
```

---

## Next Steps

1. Add more tests for comprehensive coverage
2. Add code quality gates (require 80% coverage)
3. Add deployment to staging/production
4. Set up notifications on failures
5. Use GitHub Environments for production deployments
