from ec2_s3_managment.s3_class import S3ManagerClass
from model.load_data import LoaderClass
from model.model_class import ModelClass
from ec2_s3_managment.logger_config import logger

def run_local_training_pipeline():
    """
    Main function to execute the full training pipeline - local version
    This function tests the whole process:
        - loading data
        - model training,
        - model evaluation
        - uploading model metrics and logs to S3, dowloading model
        - downloading model metrics and logs localy
        - evaluating downloaded and loaded model
    """
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
    
    # download metrics, model, logger from S3
    s3_manager_instance.download_experiment_files_from_s3()

    # test
    loaded_model = s3_manager_instance.load_model_localy()
    metrics = ModelClass.evaluate_model_static(loaded_model, X_test, y_test)
    print("accuracy: ", metrics["accuracy"])
    
    logger.info(f"=== Logger END ===\n\n")

def download_experiment_data_and_evaluate_model():
    """
    downloads newest folder from S3 bucket, loads and evaluates the model

    this function is used after main.py finish running
    """
    s3_manager_instance = S3ManagerClass()
    if not s3_manager_instance.download_possible:
        print("nothing to download")
        return

    loader_instance = LoaderClass()
    
    # Load train test data
    X_train, y_train, X_test, y_test = loader_instance.load_training_data()

    # download metrics, model, logger from S3
    s3_manager_instance.download_experiment_files_from_s3()

    # load model
    loaded_model = s3_manager_instance.load_model_localy()

    # evaluate model
    metrics = ModelClass.evaluate_model_static(loaded_model, X_test, y_test)
    print("accuracy: ", metrics["accuracy"])

if __name__ == "__main__":
    download_experiment_data_and_evaluate_model()