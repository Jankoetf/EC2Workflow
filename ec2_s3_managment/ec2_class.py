import boto3
import os
import time
import json
from botocore.exceptions import ClientError

from ec2_s3_managment.ec2_s3_constants import (KEY_DIR, INSTANCE_AMI, SECURITY_GROUP_NAME, DESCIPTION, EC2_KEY_NAME, ROLE_NAME)
from ec2_s3_managment.user_data import user_data

class Ec2ManagerClass:
    """
    This class manages various aspects of AWS EC2 resources, including instance 
    lifecycle, key pairs, security groups, and IAM roles.
    
    Example usage:
        ec2_manager = Ec2ManagerClass()
        ec2_manager.create_key_pair()
        instance_id = ec2_manager.start_instance()
        ec2_manager.wait_for_instance_target_status(instance_id, 'terminated')
    """
    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.iam_client = boto3.client('iam')
    
    # key pair creation
    def __create_new_key_pair(self):
        resp = self.ec2_client.create_key_pair(KeyName = EC2_KEY_NAME)
        file = open(f"{KEY_DIR}/{EC2_KEY_NAME}.pem", "w")
        file.write(resp["KeyMaterial"])
        file.close()
        print("new key pair created")

    def __check_if_key_pair_exists(self):
        # checking if key-pair already exist
        all_key_pairs = self.ec2_client.describe_key_pairs()

        for key_pair in all_key_pairs.get('KeyPairs', []):
            if key_pair['KeyName'] == EC2_KEY_NAME:
                print(f"Key pair '{EC2_KEY_NAME}' elready exists.")
                return True
        return False
    
    def create_key_pair(self):
        """
        This method is used to ensure consistency between AWS resources and local files:
        
        1. If the key pair exists in AWS and locally: do nothing
        2. If the key pair exists in AWS but not locally: delete the AWS key and create a new one
        3. If the key pair doesn't exist at all: create a new one
        
        This ensures you always have access to the private key material needed
        for SSH connections to EC2 instances.
        """
        if self.__check_if_key_pair_exists():
            #check if there is .pem with specific name localy
            local_key_path = f"{KEY_DIR}/{EC2_KEY_NAME}.pem"
            if os.path.isfile(local_key_path):
                #if exists everything is ok, return
                return
            else:
                self.ec2_client.delete_key_pair(KeyName=EC2_KEY_NAME)
                print("old key pair deleted")
                self.__create_new_key_pair()
        else:
            self.__create_new_key_pair()
    
    #creating instance
    def __run_ec2_instance(self):
        """
        Launch a new EC2 instance with predefined configuration settings.
        
        This method creates a new EC2 instance with specific configurations including:
        - t2.micro instance type for cost-effective computing
        - Custom user data script for instance initialization
        - Automatic termination upon shutdown
        - 20GB EBS volume with automatic deletion
        - Custom tagging for easy identification
        
        After launching the instance, this method also:
        1. Configures a security group to control network access
        2. Ensures the instance has proper IAM role for S3 access
        
        Returns:
            str: The ID of the newly created EC2 instance, which can be used
                 for future operations like termination or status checks
        """
        run_response = self.ec2_client.run_instances(
            ImageId = INSTANCE_AMI,
            MinCount = 1,
            MaxCount = 1,
            InstanceType = 't2.micro',
            UserData=user_data,
            KeyName = EC2_KEY_NAME,
            InstanceInitiatedShutdownBehavior='terminate',
            BlockDeviceMappings = [
                {
                    "DeviceName": "/dev/xvda",
                    'Ebs':{
                        'DeleteOnTermination':True,
                        'VolumeSize':20
                    }
                }
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'Model-Training-Instance'
                        }
                    ]
                }
            ],
        )
        instance_id = run_response["Instances"][0]["InstanceId"]

        security_group_id = self.__create_security_group()
        self.ec2_client.modify_instance_attribute(InstanceId = instance_id, Groups=[security_group_id])

        self.__ensure_s3_role(instance_id)

        return instance_id #important, we need this for termination, or stoping...
    
    def __check_if_security_group_name_exists(self):
        response = self.ec2_client.describe_security_groups()
        for security_group in response['SecurityGroups']:
            if security_group['GroupName'] == SECURITY_GROUP_NAME:
                print(f"Security group '{SECURITY_GROUP_NAME}' already exists.")
                return True
        return False

    def __get_group_id_by_name(self):
        response = self.ec2_client.describe_security_groups()
        for security_group in response['SecurityGroups']:
            if security_group['GroupName'] == SECURITY_GROUP_NAME:
                return security_group['GroupId']
        raise f"ERROR no security group named {SECURITY_GROUP_NAME}"


    def __create_security_group(self):
        """
        Create or retrieve a security group for EC2 instance access control.
        
        1. First checks if a security group with the predefined name exists
        2. If it exists, returns its ID without creating a duplicate
        3. If it doesn't exist, creates a new security group with SSH access (port 22) open to all IP addresses
        
        The security group controls network traffic to and from EC2 instances.
        
        Returns:
            str: The ID of the security group (either existing or newly created)
        """
        if self.__check_if_security_group_name_exists():
            return self.__get_group_id_by_name()

        response = self.ec2_client.create_security_group(
            GroupName = SECURITY_GROUP_NAME,
            Description = DESCIPTION
        )
        security_group_id = response["GroupId"]
        response = self.ec2_client.authorize_security_group_ingress(
            GroupId = security_group_id,
            IpPermissions = [
                {
                    "IpProtocol":"tcp",
                    "FromPort":22, #SSH port
                    "ToPort":22,
                    "IpRanges":[{"CidrIp": "0.0.0.0/0"}]
                }
            ]
        )
        return security_group_id
    
    def __ensure_s3_role(self, instance_id):
        """
        Create and attach an IAM role to the EC2 instance for S3 access.
        
        1. Creates an IAM role with S3 full access (if it doesn't exist)
        2. Creates an instance profile (if it doesn't exist)
        3. Attaches the role to the instance profile
        4. Associates the instance profile with the EC2 instance
        
        The method includes retry logic to handle potential race conditions
        when attaching the profile to a newly created instance.
        
        Parameters:
            instance_id (str): The ID of the EC2 instance to attach the role to
        """
        role_name = ROLE_NAME
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        s3_policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"

        try:
            response = self.iam_client.get_role(RoleName=role_name)
            print(f"IAM role '{role_name}' already exists")
        except ClientError as e:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="EC2 role granting full S3 access"
            )
            print(f"Created IAM role '{role_name}'")
            self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=s3_policy_arn)
            print(f"Attached policy {s3_policy_arn} to '{role_name}'")

        # role_arn = response["Role"]["Arn"]
        # print("Role ARN:", role_arn)

        instance_profile_name = role_name
        # This is critical: EC2 cannot directly use IAM roles - it needs the role to be wrapped in an "instance profile"
        try:
            self.iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
        except ClientError as e:
            self.iam_client.create_instance_profile(InstanceProfileName=instance_profile_name)
            self.iam_client.add_role_to_instance_profile(
                InstanceProfileName=instance_profile_name,
                RoleName=role_name
            )

        instance_profile = self.iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)['InstanceProfile']
        instance_profile_arn = instance_profile['Arn']
        for _ in range(10):
            try:
                # Try to associate the instance profile with the EC2 instance, with retry logic
                # This is necessary because there's often a propagation delay between:
                #   1. When an instance is created and
                #   2. When AWS allows IAM profiles to be attached to it

                self.ec2_client.associate_iam_instance_profile(
                    InstanceId=instance_id,
                    IamInstanceProfile={'Arn': instance_profile_arn}
                )
                break
            except ClientError as e:
                wait_period = 30 # 30 seconds between retry attempts
                print(f"waiting for {wait_period} seconds")
                time.sleep(wait_period)
        else:
            raise RuntimeError("Failed to associate instance profile after multiple retries")
        print(f"Associated Instance Profile '{instance_profile_name}' with EC2 {instance_id}")
    
    #status, start, stop, delete
    def wait_for_instance_target_status(self, instance_id, target_status):
        """
        Wait for an EC2 instance to reach a specified status through polling.
        
        This is particularly useful when you need to wait for an instance to
        complete initialization before performing subsequent operations that
        depend on the instance being in a specific state.
        
        Parameters:
            instance_id (str): The ID of the EC2 instance to monitor
            target_status (str): The desired instance status to wait for
                                 (e.g., 'running', 'stopped', 'terminated')
        """
        while True:
            response = self.ec2_client.describe_instances(InstanceIds = [instance_id])
            
            status = response["Reservations"][0]['Instances'][0]["State"]["Name"]
            if status == target_status:
                print(f"Instance is in {target_status} state!")
                break
            else:
                time.sleep(10)

    def start_instance(self):
        print("starting instance")
        instance_id = self.__run_ec2_instance()
        self.wait_for_instance_target_status(instance_id, "running")
        return instance_id #important, we need this for termination, or stoping...
    
    def stop_instance(self, instance_id):
        print("stopping instance")
        self.ec2_client.stop_instances(InstanceIds = [instance_id])
        self.wait_for_instance_target_status(instance_id, "stopped")
    
    def terminate_instance(self, instance_id):
        print("terminating instance")
        self.ec2_client.terminate_instances(InstanceIds = [instance_id])
        self.wait_for_instance_target_status(instance_id, "terminated")



        

    



    



    


        
            
        
        


