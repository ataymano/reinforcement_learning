from mpi4py import MPI

class local:
    def map(self, elements):
        return elements

    def reduce(self, elements):
        return elements

class mpi:
    def map(self, elements):
        result = []
        i = MPI.COMM_WORLD.Get_rank()
        step = MPI.COMM_WORLD.Get_size()
        while i < len(elements):
            result.append(elements[i])
            i = i + step
        return result

    def reduce(self, elements):
        return MPI.COMM_WORLD.allreduce(elements, MPI.SUM)


