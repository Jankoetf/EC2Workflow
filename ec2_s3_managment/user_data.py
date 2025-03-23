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