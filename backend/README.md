# Backend for ESP32 API

This is the backend for the ESP32 API. It is a REST API that allows the ESP32 to send data to the backend and retrieve data from the backend. The backend is built using FastAPI and PostgreSQL.

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
After installing the dependencies, you can run the backend using the following command:
```bash
python main.py
```

## Apply black formatter
To apply the black formatter to the code, you can run the following command:
```bash
black --config .\pyproject.toml .
```

## Docker commands
### Build the image
```bash
docker build -t esp32server .
```

### Run the container
```bash
docker run -d -p 8080:8080 esp32server
```

## Push the image to ECR
### Create an ECR repository

To create an ECR repository, you can use the AWS Management Console, AWS CLI, or AWS SDKs. You can also use the AWS Management Console to manage your ECR repositories.

Command to create an ECR repository:

```bash
aws ecr create-repository --repository-name my-repo --profile chris-profile
```

Autenitcation in ECR:

```bash
aws ecr get-login-password --region us-east-1 --profile chris-profile | docker login --username AWS --password-stdin 850995540863.dkr.ecr.us-east-1.amazonaws.com
```

### Push a container image to ECR

To push a container image to ECR, you can use the AWS Management Console, AWS CLI, or AWS SDKs. You can also use Docker CLI to push a container image to ECR.

Command to tag a container image:

```bash
docker tag esp32server:latest 850995540863.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest
```

Command to push a container image:

```bash
docker push 850995540863.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest
```