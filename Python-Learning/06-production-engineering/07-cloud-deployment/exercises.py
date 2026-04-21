"""
Cloud Deployment - Exercises

8 exercises covering:
- AWS SageMaker deployment configuration
- GCP Vertex AI setup
- Serverless deployment (Lambda, Cloud Run)
- Cost estimation
- Auto-scaling configuration
- Multi-region deployment
"""

from typing import Dict, List, Any


# ============================================================================
# Exercise 1-2: AWS SageMaker
# ============================================================================

def exercise_1_sagemaker_endpoint_config() -> str:
    """
    Exercise 1: Create AWS SageMaker endpoint configuration.

    Requirements:
    - Endpoint configuration name
    - Model name
    - Initial instance count: 2
    - Instance type: ml.m4.xlarge
    - Variant traffic weight: 100
    - Return CloudFormation or boto3 code

    Returns:
        Complete AWS configuration code as string
    """
    pass


def exercise_2_sagemaker_batch_transform() -> str:
    """
    Exercise 2: Create SageMaker batch transform job configuration.

    Requirements:
    - Batch job name
    - Model artifact location (S3)
    - Input data path (S3)
    - Output path (S3)
    - Instance type and count for processing
    - Max concurrent transforms: 4
    - Max payload: 10MB
    - Return configuration code

    Returns:
        Complete batch transform configuration as string
    """
    pass


# ============================================================================
# Exercise 3-4: GCP Vertex AI
# ============================================================================

def exercise_3_vertex_ai_custom_training() -> str:
    """
    Exercise 3: Create Vertex AI custom training job.

    Requirements:
    - Training script location
    - Machine type: n1-standard-4
    - Replica count: 1
    - Training container image
    - Model display name
    - Output model location (GCS)
    - Return Python code using aiplatform SDK

    Returns:
        Complete Vertex AI training code as string
    """
    pass


def exercise_4_vertex_ai_endpoint_deploy() -> str:
    """
    Exercise 4: Deploy model to Vertex AI endpoint.

    Requirements:
    - Endpoint name
    - Deployed model name
    - Min replica count: 1
    - Max replica count: 5
    - Machine type: n1-standard-2
    - Traffic split: 100% to new model
    - Return deployment code

    Returns:
        Complete Vertex AI deployment code as string
    """
    pass


# ============================================================================
# Exercise 5-6: Serverless Deployment
# ============================================================================

def exercise_5_lambda_inference_handler() -> str:
    """
    Exercise 5: Create AWS Lambda handler for inference.

    Requirements:
    - Handle HTTP POST with JSON body
    - Extract features from request
    - Invoke SageMaker endpoint
    - Format response as JSON
    - Handle errors gracefully
    - Return complete lambda_handler code

    Returns:
        Complete AWS Lambda handler code as string
    """
    pass


def exercise_6_cloud_run_fastapi_app() -> str:
    """
    Exercise 6: Create containerized FastAPI app for Cloud Run.

    Requirements:
    - FastAPI application
    - Health check endpoint (/health)
    - Prediction endpoint (/predict)
    - Load model on startup
    - Graceful shutdown
    - Return complete app code and Dockerfile

    Returns:
        Combined FastAPI app code and Dockerfile as string
    """
    pass


# ============================================================================
# Exercise 7: Cost Estimation
# ============================================================================

def exercise_7_cost_estimation() -> Dict[str, Any]:
    """
    Exercise 7: Calculate deployment costs for different scenarios.

    Requirements:
    - Calculate 3 deployment options:
      1. SageMaker endpoint (1 instance, 24/7)
      2. SageMaker batch (2-hour batch job, daily)
      3. Lambda (10,000 invocations/day)
    - Include compute, storage, data transfer costs
    - Compare total monthly cost
    - Recommend most cost-effective option
    - Return detailed cost breakdown

    Returns:
        Dictionary with cost analysis for each option
    """
    pass


# ============================================================================
# Exercise 8: Auto-scaling and Multi-region
# ============================================================================

def exercise_8_autoscaling_multiregion() -> str:
    """
    Exercise 8: Create auto-scaling and multi-region deployment config.

    Requirements:
    - Define auto-scaling policy:
      * Min replicas: 2, Max replicas: 10
      * Target CPU: 70%
      * Target latency: 100ms
    - Multi-region setup:
      * Primary region: us-central1
      * Failover region: us-east1
      * Traffic distribution
    - Health check configuration
    - Return complete Terraform/CloudFormation code

    Returns:
        Complete infrastructure-as-code for auto-scaling and multi-region
    """
    pass
