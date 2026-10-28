# AWS ECS Deployment Handover â€” Car Price Prediction API

**Last updated:** 2026-10-28
**Status:** Docker image is in ECR, ECS cluster and task definition are created. Networking and running the task are still pending.

## 1. Goal

Deploy the Flask car-price prediction API from the local project `C:\MLOPS\new_app` to AWS ECS on AWS Fargate, in the Mumbai region.

The API listens on `0.0.0.0:5000` and exposes `POST /predict`.

## 2. AWS account and CLI

- **AWS account ID:** `750727660705`
- **Region:** `ap-south-1` (Asia Pacific â€” Mumbai)
- **CLI profile:** `mlops-deployment-user`
- **IAM user:** `mlops-deployment-user`
- **IAM group:** `MLOpsDeploymentGroup`
- **Project folder:** `C:\MLOPS\new_app`

Use the named profile on commands rather than the root account:

```powershell
--region ap-south-1 --profile mlops-deployment-user
```

Do not put access keys, passwords, session tokens, or other secrets in this handover document.

## 3. Local application and Docker image

### Flask app

File: `apps/flask_app.py`

- Loads `models/xgb_car_price_model.pkl` at startup.
- Runs on host `0.0.0.0`, port `5000`.
- Endpoint: `POST /predict`
- Example request body:

```json
{
  "km_driven": 45000,
  "mileage": 18,
  "age": 5,
  "fuel_type": "Petrol"
}
```

- Expected response format:

```json
{
  "predicted_price": 123456.0
}
```

The number above is illustrative; actual predictions depend on the model and request.

### Dockerfile notes

The current Dockerfile uses `python:3.10-slim`, installs `requirements.txt`, copies `apps/flask_app.py` into `/app/flask_app.py`, and copies the model to `/app/models/xgb_car_price_model.pkl`. It exposes port 5000 and starts `python flask_app.py`.

### ECR image

- **Repository:** `new-app`
- **Image URI:** `750727660705.dkr.ecr.ap-south-1.amazonaws.com/new-app:latest`
- **Last observed image digest:** `sha256:3dfdccc7b6964f97d0059a3f1b046bf0054aeed18ae0899d6104bc2f4517e90c`
- **Last observed image size:** approximately 742 MB

The digest/size are from the last reported ECR query and may change if a new image is pushed.

## 4. IAM setup completed

### Deployment user policies

The `mlops-deployment-user` belongs to `MLOpsDeploymentGroup`, which currently has:

- AWS managed policy `AmazonEC2ContainerRegistryPowerUser`
- AWS managed policy `AmazonECS_FullAccess`
- Customer inline policy `ECRCreateRepositoryPolicy`

An additional inline policy, `ECSExecutionRoleAccess`, was instructed to be added to the group to allow `iam:GetRole` and `iam:PassRole` on the specific execution role. The user confirmed `aws iam get-role` succeeds afterward. Verify the inline policy exists in the console if needed.

### ECS task execution role

- **Role:** `ecsTaskExecutionRole`
- **ARN:** `arn:aws:iam::750727660705:role/ecsTaskExecutionRole`
- **Trust service:** `ecs-tasks.amazonaws.com`
- **Attached policy:** `AmazonECSTaskExecutionRolePolicy`

Verified with:

```powershell
aws iam get-role --role-name ecsTaskExecutionRole --profile mlops-deployment-user --region ap-south-1
aws iam list-attached-role-policies --role-name ecsTaskExecutionRole --profile mlops-deployment-user --region ap-south-1
```

## 5. ECS resources created

### Cluster

- **Name:** `car-price-cluster`
- **ARN:** `arn:aws:ecs:ap-south-1:750727660705:cluster/car-price-cluster`
- **Status:** `ACTIVE`

### Task definition

- **Family:** `car-price-task`
- **Revision:** `1`
- **CPU:** `512` (0.5 vCPU)
- **Memory:** `2048` MiB (2 GiB)
- **Network mode:** `awsvpc`
- **Launch compatibility:** `FARGATE`
- **Container name:** `car-price-container`
- **Container port:** `5000`
- **Image:** `750727660705.dkr.ecr.ap-south-1.amazonaws.com/new-app:latest`
- **Execution role:** `ecsTaskExecutionRole`
- **CloudWatch log group:** `/ecs/car-price-task` (configured to be created on launch)

The task definition was registered from a generated file named `ecs-task-definition.json` in the project directory.

Verify the task definition:

```powershell
aws ecs describe-task-definition --task-definition car-price-task --region ap-south-1 --profile mlops-deployment-user --query "taskDefinition.{Family:family,Revision:revision,CPU:cpu,Memory:memory,Image:containerDefinitions[0].image}" --output table
```

## 6. VPC and subnet investigation

- **Default VPC:** `vpc-05b1182730c40c995`
- **VPC CIDR:** `172.31.0.0/16`
- **Subnets observed:**
  - `subnet-02894bde1e97e80f6` â€” `ap-south-1b`, `172.31.0.0/20`
  - `subnet-0472e39a462e62871` â€” `ap-south-1c`, `172.31.16.0/20`
  - `subnet-0b244ca58f58f23bf` â€” `ap-south-1a`, `172.31.32.0/20`
- All three reported `MapPublicIpOnLaunch=True`. This alone does not prove internet routing.
- A route-table query filtered by subnet association returned no output. Likely the subnet has no explicitly associated route table and uses the VPC's **main route table**. This is not yet verified.
- **Do not assume the subnet is public until the main route table is checked.**

Next command to inspect the VPC's main route table:

```powershell
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-05b1182730c40c995" "Name=association.main,Values=true" --region ap-south-1 --profile mlops-deployment-user --query "RouteTables[*].{RouteTableId:RouteTableId,Routes:Routes}" --output json
```

Check whether a route exists with destination `0.0.0.0/0` and a gateway ID beginning with `igw-`. If not, inspect the other route tables and VPC internet gateway before making changes.

## 7. Immediate next steps

1. Inspect the VPC's main route table using the command above.
2. If it has a default route to an internet gateway, choose an appropriate subnet and create a security group allowing inbound TCP 5000 **from the user's current public IP only**, if practical.
3. Ensure outbound access is sufficient for ECR image pulls and CloudWatch Logs. A public Fargate task in a public subnet with a public IP is a straightforward test configuration; avoid creating a NAT Gateway unless required, because NAT Gateways can cost significantly more.
4. Launch one Fargate task in `car-price-cluster`, with `assignPublicIp=ENABLED`.
5. Wait for the task to reach `RUNNING`; obtain its public IP from the task ENI.
6. Inspect CloudWatch logs if startup fails.
7. Test `POST http://<public-ip>:5000/predict` with the sample JSON body.
8. Restrict or stop the task when not needed to reduce cost.

### Likely useful commands

List route tables:

```powershell
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-05b1182730c40c995" --region ap-south-1 --profile mlops-deployment-user --query "RouteTables[*].{RouteTableId:RouteTableId,Main:Associations[?Main==`true`].Main,Routes:Routes}" --output json
```

List security groups in the VPC:

```powershell
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=vpc-05b1182730c40c995" --region ap-south-1 --profile mlops-deployment-user --query "SecurityGroups[*].{GroupId:GroupId,Name:GroupName,Description:Description}" --output table
```

Describe ECS tasks after launch:

```powershell
aws ecs list-tasks --cluster car-price-cluster --region ap-south-1 --profile mlops-deployment-user
```

## 8. Important cost and security notes

- Fargate compute is billed while tasks run; public IPv4 addresses may also incur charges. Credits/eligibility depend on the account offer and should not be assumed to cover every charge.
- Do not create a load balancer or NAT Gateway for this simple test unless needed.
- Prefer limiting inbound port 5000 to your own public IP. Do not leave a prediction API open to the whole internet unless intended.
- Never commit AWS credentials, access keys, or session tokens into the project or this document.
- The application loads a Python pickle model at startup. Only use trusted model files because unpickling an untrusted file can execute code.

## 9. Files to keep track of

- `Dockerfile` â€” image build instructions.
- `apps/flask_app.py` â€” Flask API.
- `models/xgb_car_price_model.pkl` â€” trained model.
- `requirements.txt` â€” Python dependencies.
- `ecs-task-definition.json` â€” ECS task definition input created during deployment.

## 10. Current status checklist

- [x] AWS CLI installed and working.
- [x] Named AWS CLI profile configured and identity verified.
- [x] ECR repository `new-app` created.
- [x] Docker image pushed to ECR.
- [x] ECS task execution role created and policy attached.
- [x] ECS cluster `car-price-cluster` created.
- [x] ECS task definition `car-price-task:1` registered and verified.
- [x] Default VPC and subnets discovered.
- [ ] Main route table / internet route verified.
- [ ] Security group created.
- [x] Fargate task launched and tested previously; task is currently stopped to reduce costs.
- [x] Public IP obtained during the previous test deployment.
- [x] `/predict` endpoint tested successfully during the previous deployment.

---
This is an operational handover document based on the deployment details confirmed so far. Re-run verification commands if anything may have changed since the last check.
