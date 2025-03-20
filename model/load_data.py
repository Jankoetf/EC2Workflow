import pandas as pd
from model.training_constants import TRAIN_DATASET_PATH, TEST_DATASET_PATH
from ec2_s3_managment.logger_config import logger


def load_training_data():
    """Load and prepare data for training TEST example"""
    logger.info(f"Loading data from {TRAIN_DATASET_PATH} and {TEST_DATASET_PATH}")
    
    train_data = pd.read_csv(TRAIN_DATASET_PATH)
    test_data = pd.read_csv(TEST_DATASET_PATH)
    
    # Prepare data
    X_train = train_data.iloc[:, :-1]
    y_train = train_data.iloc[:, -1]
    X_test = test_data.iloc[:, :-1]
    y_test = test_data.iloc[:, -1]
    
    logger.info(f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")
    
    return X_train, y_train, X_test, y_test