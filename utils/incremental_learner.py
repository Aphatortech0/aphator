import tensorflow as tf
import numpy as np
from threading import Thread
import time
import logging

class IncrementalLearner(Thread):
    def __init__(self, model, update_interval=300):
        super().__init__()
        self.model = model
        self.update_interval = update_interval
        self.running = True
        self.daemon = True
        self.training_data = []
        
    def add_training_data(self, features, labels):
        self.training_data.append((features, labels))
        if len(self.training_data) > 1000:  # Keep last 1000 samples
            self.training_data.pop(0)
    
    def run(self):
        while self.running:
            try:
                if len(self.training_data) >= 32:  # Minimum batch size
                    features = np.array([x[0] for x in self.training_data[-32:]])
                    labels = np.array([x[1] for x in self.training_data[-32:]])
                    
                    # Incremental training with small batch
                    self.model.train_on_batch(features, labels)
                    
                    logging.info("Incremental model update completed")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logging.error(f"Error in incremental learning: {str(e)}")
                time.sleep(self.update_interval)
    
    def stop(self):
        self.running = False
