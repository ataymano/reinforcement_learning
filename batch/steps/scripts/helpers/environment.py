from mpi4py import MPI
from helpers import logger

class environment:
    def __init__(self, runtime, job_pool):
        self.runtime = runtime
        self.job_pool = job_pool
        self.logger = logger.logger(self.runtime)


