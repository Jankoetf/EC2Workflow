from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

from model.training_constants import (N_ESTIMATORS, RANDOM_STATE)
from ec2_s3_managment.logger_config import logger

class ModelClass:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            random_state=RANDOM_STATE
        )

    def train_model(self, X_train, y_train):
        """Train the model."""
        logger.info(f"Training Started: Random Forest with {N_ESTIMATORS} trees, random_state={RANDOM_STATE}")
        self.model.fit(X_train, y_train)
        logger.info("Model training completed")
    
    @staticmethod
    def evaluate_model_static(model, X_test, y_test):
        """Evaluate model and log metrics."""
        
        # Basic metrics
        y_pred = model.predict(X_test)
        accuracy = model.score(X_test, y_test)
        
        # More detailed metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred).tolist()
        
        # Store metrics in dictionary
        metrics = {
            "accuracy": accuracy,
            "classification_report": report,
            "confusion_matrix": conf_matrix,
        }

        return metrics
        

