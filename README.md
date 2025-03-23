# EC2Workflow

Training model on raw EC2 instance, saving 40% money in comparison with sagemaker notebooks.<br>Technologies: AWS (EC2, S3), Docker, Python, Bash

## Cost-Efficient Model Training with AWS EC2

This project implements workflow for training machine learning models on AWS EC2 instances, providing approximately 40% cost savings compared to SageMaker notebooks while maintaining full flexibility and control over the training environment.

## Overview

EC2Workflow creates a fully automated pipeline that:

- Spins up an EC2 instance on demand
- Installs and configures Docker on the instance
- Pulls and runs training container
- Automatically terminates all resources when training completes
- Uploads trained models, metrics, and logs to S3

## Key Features

- **Local/Remote Flexibility:** Train in the cloud or localy
- **Cost efficient approch:** Only model training is performing on EC2 instance. Data preprocessing, model configuration, and trained model evaluation are performed localy.
- **S3 integration:** persistent storage of model, metrics and logs, [s3_class](./ec2_s3_managment/s3_class.py) also keep track of newest model in bucket
- **Fully automated pipeline:** [ec2_class.py](./ec2_s3_managment/ec2_class.py) manages everything related to EC2 instance, no need for manual intervention, [user_data.py](./ec2_s3_managment/user_data.py) will run container on EC2 and automatically shut down and terminate instance
- **User will be notified when the whole process is finished:** [main.py](./main.py) will wait for "terminated" status of EC2 instance, when instance is terminated it will stop runing and will print a message

## Project Structure

**EC2Workflow/**<br>
├── [**ec2_s3_managment/**](./ec2_s3_managment/)<br>
│ ├── [**ec2_class.py**](./ec2_s3_managment/ec2_class.py) # ec2 managment, start-termination, security group, role, policy<br>
│ ├── [logger_config.py](./ec2_s3_managment/logger_config.py) # Logging configuration<br>
│ ├── [**s3_class.py**](./ec2_s3_managment/s3_class.py) # uploading model, metrics, logs to S3 bucket, and tracking the newest output folder<br>
│ ├── [**user_data.py**](./ec2_s3_managment/user_data.py) # Bash script to run on EC2 when EC2 starts running <br>
│ └── [ec2_s3_constants.py](./ec2_s3_managment/ec2_s3_constants.py) # Configuration constants for S3 and EC2<br>
├── [**model/**](./model/) # model configuration<br>
│ ├── [Resources](./model/Resources/) # Training resources and data<br>
│ ├── [load_data.py](./model/load_data.py) # Data loading<br>
│ ├── [model_class.py](./model/model_class.py) # Simple model architecture definition<br>
│ └── [training_constants.py](./model/training_constants.py) # Model hyperparameters and settings<br>
├── [**main.py**](./main.py) #starting Ec2 instance - starting docker container<br>
├── [**main_local.py**](./main_local.py) #downloading and loading remotely trained model<br>
├── [**main_cloud.py**](./main_cloud.py) # code for docker image (model training)<br>
├── [.env.example](./.env) # example of .env file<br>
├── [dockerfile](./dockerfile) # Docker container definition<br>
├── [.dockerignore](./.dockerignore) # Docker build exclusions<br>
├── [.gitignore](./.gitignore) # Git exclusions<br>
├── [requirements.txt](./requirements.txt) # Project dependencies<br>
└── README.md # Project documentation<br>

## Prerequisites

- AWS Account
- AWS CLI configured with access credentials
- Python 3.8+ with dependencies from requirements.txt

## Getting Started (Installation)

Step-by-step guide to set up your project locally:

- **step 1: clone the repositiry:**
  ```
  git clone https://github.com/Jankoetf/EC2Workflow.git
  ```
- optional step - create virtual environment, windows

  ```
  python -m venv venv
  venv\Scripts\activate
  ```

- **step 2: add and edit .env (see .env.example):**<br>
  Make sure you add globaly unique bucket name, try longer name:

  ```
  S3_BUCKET_NAME=your-bucket-name-unique-123
  ```

  **Important S3 Bucket Naming Rules:**

  - Bucket names must be between 3 and 63 characters long
  - Bucket names can consist only of lowercase letters, numbers, and hyphens (-)
  - Bucket names must begin and end with a letter or number
  - Bucket names cannot contain underscores, spaces, or uppercase letters
  - Bucket names cannot be formatted as an IP address (e.g., 192.168.5.4)
  - Bucket names must be unique across all AWS accounts in all AWS regions

- **step 3: go to root directory, install requirenments and run main.py**<br>
  This will run docker training container on EC2 and save training artifacts to S3

  ```
  cd EC2Workflow
  pip install -r requirements.txt
  python main.py
  ```

- **step 4: after main.py execution is finished, you can run main_local.py**<br>
  this will connect to S3 and load the latest training artifacts from S3
  ```
  python main_local.py
  ```

## Extending the Project (Docker installed required)

To truly customize this project for your specific machine learning needs, you'll need to modify the model, datasets, and Docker configuration:

- Modify your model architecture and datasets in the [model/](./model/) file to implement your specific neural network or machine learning algorithm ([model_class.py](./model/model_class.py)), and corresponding [load_data.py](./model/load_data.py) script

- Modify [dockerfile](./dockerfile)

- Build a new Docker image with your changes (currenty you are using my public image...):

  ```
  docker build -t yourusername/your-model-name:latest .
  ```

- Push your Docker image to Docker Hub (must be public for EC2 to pull it):

  ```
  docker login
  docker push yourusername/your-model-name:latest
  ```

- Update the image reference in user_data.py:
  ```
  IMAGE_NAME = "yourusername/your-model-name:latest"
  ```

<br><br><br><br><br><br>

## Thank you for exploring my project!

If you'd like to learn more about my background and qualifications, please visit my [LinkedIn profile](https://www.linkedin.com/in/jankomitrovic)
