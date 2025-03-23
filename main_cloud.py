from ec2_s3_managment.s3_class import S3ManagerClass
from model.load_data import LoaderClass
from model.model_class import ModelClass
from ec2_s3_managment.logger_config import logger

def run_cloud_training_pipeline():
    """Main function to execute the full training pipeline - cloud version"""
    logger.info(f"=== Starting model training pipeline ===")
    s3_manager_instance = S3ManagerClass()
    loader_instance = LoaderClass()
    model_instance = ModelClass()

    # Load data
    X_train, y_train, X_test, y_test = loader_instance.load_training_data()

    # Train model
    model_instance.train_model(X_train, y_train)

    #evaluate model
    metrics = ModelClass.evaluate_model_static(model_instance.model, X_test, y_test)

    # upload metrics, model, logger to S3
    s3_manager_instance.upload_metrics_to_s3(metrics)
    s3_manager_instance.upload_model_to_s3(model_instance.model)
    logger.info("=== Model training pipeline completed ===")
    s3_manager_instance.upload_log_to_s3()

    logger.info(f"=== Logger END ===\n\n")

if __name__ == "__main__":
    run_cloud_training_pipeline()