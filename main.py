from ec2_s3_managment.ec2_class import Ec2ManagerClass

def main():
    ec2_manager_instance = Ec2ManagerClass()
    ec2_manager_instance.create_key_pair() # Ensures an SSH key pair exists both in AWS and locally
    instance_id = ec2_manager_instance.start_instance()

    #important: instance will shut down and terminated automaticaly - this simulate notification when the whole process is finished
    ec2_manager_instance.wait_for_instance_target_status(instance_id, 'terminated')

if __name__ == "__main__":
    main()
