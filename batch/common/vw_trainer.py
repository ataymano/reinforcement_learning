from vowpalwabbit import pyvw

class vw_trainer:
    def __init__(self, args):
        self.impl = pyvw.vw(args)

    def train(self, examples):
        for e in examples:
            self.impl.learn(e)

    def save_model(self, path):
        self.impl.save(path)

    def finish(self):
        self.impl.finish()

