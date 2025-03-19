import boto3
import os
import time
from ec2_s3_managment.ec2_s3_constants import KEY_DIR, INSTANCE_AMI, SECURITY_GROUP_NAME, DESCIPTION, EC2_KEY_NAME

class Ec2S3Manager:
    def __init__(self):
        self.ec2_client = boto3.client('ec2')
    
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
        run_response = self.ec2_client.run_instances(
            ImageId = INSTANCE_AMI,
            MinCount = 1,
            MaxCount = 1,
            InstanceType = 't2.micro',
            KeyName = EC2_KEY_NAME,
            BlockDeviceMappings = [
                {
                    "DeviceName": "/dev/xvda",
                    'Ebs':{
                        'DeleteOnTermination':True,
                        'VolumeSize':20
                    }
                }
            ]
        )
        instance_id = run_response["Instances"][0]["InstanceId"]
        # print("instance_id: ", instance_id)

        security_group_id = self.__create_security_group()
        self.ec2_client.modify_instance_attribute(InstanceId = instance_id, Groups=[security_group_id])

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
    
    #status, start, stop, delete
    def wait_for_instance_target_status(self, instance_id, target_status):
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



        

    



    



    


        
            
        
        


