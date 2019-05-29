from vowpalwabbit import pyvw

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

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

