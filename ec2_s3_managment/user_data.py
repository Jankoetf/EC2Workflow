user_data = """#!/bin/bash
yum update -y
yum install docker -y
systemctl start docker
systemctl enable docker
docker pull jankoi/model-training:latest
sleep 60
docker run jankoi/model-training:latest
"""