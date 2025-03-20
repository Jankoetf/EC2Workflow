from ec2_s3_managment.ec2_class import Ec2ManagerClass
from ec2_s3_managment.s3_class import S3ManagerClass
from ec2_s3_managment.logger_config import logger

def test_ec2_class():
    ec2_manager_instance = Ec2ManagerClass()
    ec2_manager_instance.create_key_pair()
    instance_id = ec2_manager_instance.start_instance()
    ec2_manager_instance.terminate_instance(instance_id)

def test_s3_class():
    s3_manager_instance = S3ManagerClass()
    print(s3_manager_instance)
    s3_manager_instance.upload_single_file("TestFiles/test_file.txt", "test_file.txt")

def run_local_training_pipeline():
    """Main function to execute the full training pipeline."""
    logger.info(f"=== Starting model training pipeline ===")
    s3_manager_instance = S3ManagerClass()
    print(s3_manager_instance)

    metrics = {"lol":"ide gassssssssssssssssssss"}
    s3_manager_instance.upload_metrics_to_s3(metrics)

    logger.info("=== Model training pipeline completed ===")
    

    s3_manager_instance.download_experiment_files_from_s3()
    print(s3_manager_instance)


    logger.info(f"=== Logger END ===\n\n")

if __name__ == "__main__":
    print("main")
    #test_ec2_class()
    run_local_training_pipeline()
    #test_s3_class()