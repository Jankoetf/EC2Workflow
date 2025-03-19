from ec2_s3_managment.ec2_class import Ec2S3Manager

def test_ec2_class():
    ec2_manager_instance = Ec2S3Manager()
    ec2_manager_instance.create_key_pair()
    instance_id = ec2_manager_instance.start_instance()
    ec2_manager_instance.terminate_instance(instance_id)

if __name__ == "__main__":
    print("main")
    #test_ec2_class()