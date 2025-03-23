from ec2_s3_managment.ec2_class import Ec2ManagerClass

def main():
    ec2_manager_instance = Ec2ManagerClass()
    ec2_manager_instance.create_key_pair()
    instance_id = ec2_manager_instance.start_instance()

if __name__ == "__main__":
    main()
