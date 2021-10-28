import os

import fire
from tqdm import tqdm

from model.XGBoost import XGBoost
import core.config as conf

class Run(object):
    def __init__(self, mode="train"):
        self.model = XGBoost()
        self.mode = mode
        
    def run(self) :
        if self.mode == "train" :
            self.model.train()
        elif self.mode == "train_valid" :
            self.model.train(True)
        elif self.mode == "submission" :
            self.model.predict()

if __name__ == "__main__":
    fire.Fire(Run)

