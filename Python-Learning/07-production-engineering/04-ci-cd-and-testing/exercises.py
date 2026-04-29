"""
CI/CD and Testing - Exercises

10 exercises covering:
- GitHub Actions workflows
- Testing strategies and pyramid
- Pre-commit hooks
- Model validation gates
- Secrets management
- Artifact management
- Deployment strategies
"""

from typing import Dict, List


# ============================================================================
# Exercise 1-2: GitHub Actions Workflows
# ============================================================================

def exercise_1_basic_test_workflow() -> str:
    """
    Exercise 1: Create a basic GitHub Actions workflow for testing.

    Requirements:
    - Trigger on push and pull_request
    - Run on ubuntu-latest
    - Checkout code
    - Set up Python 3.11
    - Install dependencies from requirements.txt
    - Run pytest with coverage
    - Report coverage

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


def exercise_2_docker_build_push() -> str:
    """
    Exercise 2: Create GitHub Actions workflow for Docker build and push.

    Requirements:
    - Trigger on push to main branch
    - Build Docker image with tag: myregistry/ml-api:${{ github.sha }}
    - Tag with 'latest' for main branch
    - Login to Docker registry
    - Push image to registry
    - Add build metadata

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


# ============================================================================
# Exercise 3-4: Testing Strategies
# ============================================================================

def exercise_3_unit_test_suite() -> str:
    """
    Exercise 3: Write unit test code for utility functions.

    Requirements:
    - Test validate_email() function
    - Test calculate_score() with various inputs
    - Test error handling
    - Use pytest and assertions
    - Minimum 5 test cases

    Returns:
        Complete unit test code as string
    """
    pass


def exercise_4_integration_test_api() -> str:
    """
    Exercise 4: Write integration tests for FastAPI endpoints.

    Requirements:
    - Test GET /predict endpoint with mocked model
    - Test POST /train with file upload
    - Test error cases (400, 404, 500)
    - Use TestClient
    - Use fixtures for setup/teardown
    - Minimum 6 test cases

    Returns:
        Complete integration test code as string
    """
    pass


# ============================================================================
# Exercise 5: Pre-commit Hooks
# ============================================================================

def exercise_5_pre_commit_config() -> str:
    """
    Exercise 5: Create .pre-commit-config.yaml for ML project.

    Requirements:
    - Black for code formatting
    - isort for import sorting
    - Flake8 for linting
    - mypy for type checking
    - bandit for security scanning
    - detect-secrets for credential detection
    - trailing-whitespace
    - end-of-file-fixer

    Returns:
        Complete .pre-commit-config.yaml content as string
    """
    pass


# ============================================================================
# Exercise 6: Model Validation Gates
# ============================================================================

def exercise_6_model_validation_workflow() -> str:
    """
    Exercise 6: Create GitHub Actions workflow for model validation.

    Requirements:
    - Trigger on push to main
    - Load trained model
    - Validate metrics: accuracy >= 0.90, F1 >= 0.85
    - Check model size limit (500MB)
    - Run regression test suite
    - Only allow deployment if validation passes
    - Comment on PR with results

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


# ============================================================================
# Exercise 7: Secrets Management
# ============================================================================

def exercise_7_deployment_with_secrets() -> str:
    """
    Exercise 7: Create GitHub Actions workflow using secrets.

    Requirements:
    - Use GitHub secrets: API_KEY, DB_PASSWORD, DOCKER_USERNAME, DOCKER_PASSWORD
    - Authenticate to Docker registry with secrets
    - Deploy with secret environment variables
    - Mask secrets in logs
    - Separate dev and prod deployments
    - Use different secrets per environment

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


# ============================================================================
# Exercise 8: Artifact Management
# ============================================================================

def exercise_8_artifact_workflow() -> str:
    """
    Exercise 8: Create GitHub Actions workflow for artifact management.

    Requirements:
    - Build Python wheel package
    - Build Docker image and save as artifact
    - Save test coverage report as artifact
    - Save model weights as artifact (simulated)
    - Upload artifacts with 30-day retention
    - Download artifacts in deployment job
    - Archive artifacts after deployment

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


# ============================================================================
# Exercise 9-10: Deployment Strategies
# ============================================================================

def exercise_9_canary_deployment() -> str:
    """
    Exercise 9: Create GitHub Actions workflow for canary deployment.

    Requirements:
    - Deploy to 10% of users initially
    - Monitor error rate and latency
    - If metrics good, increase to 50%
    - If metrics good, increase to 100%
    - Automatic rollback if threshold exceeded
    - Run smoke tests at each stage
    - Send notifications on completion

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass


def exercise_10_blue_green_deployment() -> str:
    """
    Exercise 10: Create GitHub Actions workflow for blue-green deployment.

    Requirements:
    - Deploy to "green" environment (not receiving traffic)
    - Run full test suite on green environment
    - Run smoke tests
    - Switch traffic to green (make it blue)
    - Keep previous blue as backup for rollback
    - Health checks before switching
    - Automatic rollback capability

    Returns:
        Complete GitHub Actions YAML workflow as string
    """
    pass
