from ec2_s3_managment.ec2_class import Ec2ManagerClass
from ec2_s3_managment.s3_class import S3ManagerClass
from model.load_data import LoaderClass
from model.model_class import ModelClass
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
    loader_instance = LoaderClass()
    model_instance = ModelClass()

    # Load data
    X_train, y_train, X_test, y_test = loader_instance.load_training_data()

    # Train model
    model_instance.train_model(X_train, y_train)

    #evaluate model
    metrics = model_instance.evaluate_model(X_test, y_test)

    # upload metrics, model, logger to S3
    s3_manager_instance.upload_metrics_to_s3(metrics)
    s3_manager_instance.upload_model_to_s3(model_instance.model)
    logger.info("=== Model training pipeline completed ===")
    s3_manager_instance.upload_log_to_s3()
    
    # download metrics, model, logger from S3
    s3_manager_instance.download_experiment_files_from_s3()

    # test
    loaded_model = s3_manager_instance.load_model_localy()
    metrics = ModelClass.evaluate_model_static(loaded_model, X_test, y_test)
    print("accuracy: ", metrics["accuracy"])
    
    logger.info(f"=== Logger END ===\n\n")

if __name__ == "__main__":
    print("main")
    run_local_training_pipeline()
