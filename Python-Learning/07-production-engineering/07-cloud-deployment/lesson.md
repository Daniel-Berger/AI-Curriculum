# Cloud Deployment: Scaling ML Services

## Overview

Cloud platforms provide managed services for deploying and scaling ML applications. This lesson covers AWS SageMaker, GCP Vertex AI, serverless options, and cost optimization.

## 1. AWS SageMaker

Fully managed service for building, training, and deploying ML models.

### Deployment Options

**SageMaker Endpoint**: Real-time inference
```python
import sagemaker
from sagemaker.estimator import Estimator

# Create and train model
role = sagemaker.get_execution_role()
estimator = Estimator(
    image_uri="246618743249.dkr.ecr.us-west-2.amazonaws.com/sagemaker-xgboost:latest",
    role=role,
    instance_count=1,
    instance_type="ml.m4.xlarge"
)

estimator.fit(s3_data_path)

# Deploy endpoint
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m4.xlarge"
)

# Invoke endpoint
prediction = predictor.predict(test_data)
```

**SageMaker Batch Transform**: Batch inference
```python
batch_transformer = estimator.transformer(
    instance_count=1,
    instance_type="ml.m4.xlarge"
)

batch_transformer.transform(
    data=s3_input_path,
    content_type="text/csv"
)
```

**SageMaker Multi-Model Endpoint**: Serve multiple models
```python
multi_model_endpoint_config_name = 'multi-model-endpoint'
sm.create_endpoint_config(
    EndpointConfigName=multi_model_endpoint_config_name,
    ProductionVariants=[{
        'VariantName': 'AllTraffic',
        'ModelName': 'xgboost-model',
        'InitialInstanceCount': 1,
        'InstanceType': 'ml.m4.xlarge'
    }]
)
```

### SageMaker Features

- **Built-in Algorithms**: XGBoost, Linear Learner, K-Means, etc.
- **Notebook Instances**: Jupyter notebooks for development
- **Autopilot**: Automatic ML model selection
- **Model Registry**: Version control for models
- **Feature Store**: Centralized feature management

## 2. GCP Vertex AI

Google Cloud's unified ML platform.

### Deployment on Vertex AI

**Custom Training**
```python
from google.cloud import aiplatform

aiplatform.init(project='my-project', location='us-central1')

job = aiplatform.CustomTrainingJob(
    display_name='my-training-job',
    script_path='training_script.py',
    container_uri='gcr.io/cloud-aiplatform/training/tf-cpu.2-8:latest'
)

model = job.run(
    machine_type='n1-standard-4',
    replica_count=1
)
```

**Deploy to Vertex AI Endpoint**
```python
endpoint = model.deploy(
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=5
)

# Get predictions
predictions = endpoint.predict(
    instances=[[1, 2, 3, 4]]
)
```

**Batch Predictions**
```python
batch_prediction_job = model.batch_predict(
    job_display_name='batch_job',
    instances_format='csv',
    gcs_source=['gs://bucket/input.csv'],
    gcs_destination_prefix='gs://bucket/output/'
)
```

### Vertex AI Features

- **AutoML**: Automatic model training
- **Workbench**: Jupyter notebooks
- **Feature Store**: Managed feature management
- **Model Registry**: Version control
- **Experiments**: Track training runs
- **Monitoring**: Data drift and model drift detection

## 3. Serverless Deployment

Run code without managing infrastructure.

### AWS Lambda

Deploy inference as serverless function.

```python
# lambda_handler.py
import json
import boto3

sagemaker = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = 'my-endpoint'

def lambda_handler(event, context):
    # Parse input
    body = json.loads(event['body'])
    data = body['data']

    # Invoke SageMaker endpoint
    response = sagemaker.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps(data)
    )

    result = json.loads(response['Body'].read())

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**Limitations:**
- 15-minute timeout
- 10GB memory max
- Cold start latency (1-5 seconds)
- Good for: Low-frequency, simple predictions

### Google Cloud Run

Deploy containerized services serverless.

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
```

**Deploy:**
```bash
gcloud run deploy my-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900
```

**Advantages:**
- Automatic scaling
- No cold start penalty
- Pay per invocation
- Good for: APIs, moderate traffic

### Modal

Purpose-built for ML inference.

```python
import modal

app = modal.App("ml-api")
model = modal.Image.debian_slim().pip_install("torch", "transformers")

@app.function(image=model, gpu="A100")
def predict(prompt: str) -> str:
    from transformers import pipeline
    pipe = pipeline("text-generation", device=0)
    return pipe(prompt, max_length=100)[0]["generated_text"]

@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    app = FastAPI()

    @app.post("/predict")
    async def get_prediction(prompt: str):
        return {"result": predict.remote(prompt)}

    return app
```

**Advantages:**
- GPU-optimized
- Distributed computing
- Low cold start
- Good for: ML workloads, expensive models

## 4. Cost Optimization

### Cost Estimation

**AWS SageMaker On-Demand:**
```
Endpoint cost = (instance_count × hourly_rate) + data_transfer
Example: 1x ml.m4.xlarge = $0.245/hour = $180/month
```

**Batch processing comparison:**
```
Real-time endpoint: $180/month
Batch job: $0.03/hour × 2 hours/month = $0.06/month
10x cheaper but no real-time response
```

**Serverless comparison:**
```
AWS Lambda: $0.0000166667/GB-second + $0.20/million invocations
100 requests/day: ~$0.50/month
Scale to 10,000/day: ~$5/month (vs $180 for endpoint)
```

### Cost Reduction Strategies

1. **Right-sizing Instances**
   - Use smaller instances for development
   - Auto-scale based on load
   - Use spot instances (70% cheaper)

2. **Batch vs Real-time**
   - Use batch for non-urgent predictions
   - Schedule batch jobs during off-peak hours
   - Batch: 100x cheaper than real-time

3. **Model Optimization**
   - Quantization: Reduce precision (int8 vs float32)
   - Pruning: Remove unnecessary parameters
   - Distillation: Train smaller model to match large model
   - 50% smaller model = 50% lower compute cost

4. **Caching**
   - Cache common predictions
   - Use CDN for static content
   - Reduce redundant API calls

5. **Reserved Capacity**
   - AWS: 30-60% discount with 1-3 year commitment
   - GCP: Similar discounts
   - Good for stable, predictable workloads

## 5. Scaling Strategies

### Vertical Scaling
Increase instance size/capability.
```
Benefits: Simple, no code changes
Limits: Single machine bottlenecks
```

### Horizontal Scaling
Increase number of instances.
```yaml
deployment:
  replicas:
    min: 2
    max: 10
  scale_when:
    - cpu > 70%
    - latency > 500ms
```

### Auto-scaling Configuration
```python
# SageMaker variant auto-scaling
scaling_config = {
    'MinCapacity': 2,
    'MaxCapacity': 10,
    'TargetValue': 70.0,
    'PredefinedMetricSpecification': {
        'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
    },
    'ScaleOutCooldown': 300,
    'ScaleInCooldown': 300
}
```

## 6. Monitoring and Observability

### CloudWatch (AWS)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='MyApp/ML',
    MetricData=[
        {
            'MetricName': 'InferenceLatency',
            'Value': 125,
            'Unit': 'Milliseconds'
        }
    ]
)
```

### Cloud Monitoring (GCP)
```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

series = monitoring_v3.TimeSeries()
series.metric.type = 'custom.googleapis.com/inference_latency'
series.resource.type = 'global'

point = monitoring_v3.Point()
point.interval.end_time.seconds = int(time.time())
point.value.double_value = 125.0
series.points = [point]

client.create_time_series(name=project_name, time_series=[series])
```

## 7. Best Practices

1. **Infrastructure as Code**
   - Version control deployments
   - Reproducible environments
   - Terraform, CloudFormation, Pulumi

2. **Secrets Management**
   - Never hardcode credentials
   - Use managed secret stores
   - Rotate secrets regularly

3. **High Availability**
   - Multi-region deployment
   - Failover strategies
   - Health checks and auto-recovery

4. **Model Versioning**
   - Track model versions
   - Easy rollback
   - A/B test new versions

5. **Disaster Recovery**
   - Backup models and data
   - Recovery time objective (RTO)
   - Recovery point objective (RPO)

## Summary

Cloud deployment considerations:
- **Latency requirements**: Real-time (SageMaker, Vertex AI) vs Batch (SageMaker Batch)
- **Cost constraints**: Serverless (Lambda, Cloud Run) for variable load
- **Scale requirements**: Managed services handle scaling automatically
- **Development speed**: Vertex AI AutoML for rapid deployment
- **Control level**: SageMaker for fine control, Vertex AI for ease

Choose based on your workload characteristics and business requirements.
