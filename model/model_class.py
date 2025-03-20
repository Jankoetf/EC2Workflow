from sklearn.ensemble import RandomForestClassifier

from model.training_constants import (N_ESTIMATORS, RANDOM_STATE)

class ModelClass:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            random_state=RANDOM_STATE
        )