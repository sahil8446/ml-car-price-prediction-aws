# Car Price Prediction API

An end-to-end machine learning project that serves car price predictions through a Flask API and supports containerized deployment on AWS.

## Tech Stack
- Python and machine learning
- Flask REST API
- Docker
- Amazon ECR
- Amazon ECS Fargate
- Amazon CloudWatch Logs

## API Endpoint
POST /predict

### Example Request
```json
{
  "km_driven": 45000,
  "mileage": 18,
  "age": 5,
  "fuel_type": "Petrol"
}
```

### Example Response
```json
{
  "predicted_price": 7.6462
}
```

The prediction above is an example from a previous deployment; actual results depend on the model and input.

## Deployment Architecture
1. Package the application using Docker.
2. Push the image to Amazon ECR.
3. Run the container on Amazon ECS Fargate.
4. Send HTTP requests to the running API.

## Repository Structure
- `apps/` - Application implementations
- `data/` - Dataset
- `models/` - Trained model artifacts
- `notebooks/` - Experiments and analysis
- `scripts/` - Training and prediction utilities
- `tests/` - Automated tests
- `Dockerfile` - Container build instructions
- `ecs-task-definition.json` - ECS task configuration

## Run and Deploy
See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

## Security
Do not commit AWS credentials, access keys, passwords, or private environment files.
