"""
Docker Execution Script

This script defines the EC2 instance's user data, which runs automatically when the instance starts.

Key points:
    sleep 60
        Instance waits for 60 seconds because instance will first start running and only then S3 access rule will
        be attached - so we need to wait until EC2 instance has S3 access
    shutdown -h now
        Initiates system shutdown once the container execution completes,
        Combined with instance 'terminate on shutdown' setting, this ensures complete cleanup
        All resources (instance, EBS volumes) are automatically terminated and deleted
"""

IMAGE_NAME = "jankoi/model-training:latest"
user_data = f"""#!/bin/bash
yum update -y
yum install docker -y
systemctl start docker
systemctl enable docker
docker pull {IMAGE_NAME}
sleep 60
docker run {IMAGE_NAME}
shutdown -h now
"""