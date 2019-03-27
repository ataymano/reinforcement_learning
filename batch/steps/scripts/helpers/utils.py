from azureml.core.run import Run


def _f_range(lower_bound, upper_bound, step):
    while lower_bound <= upper_bound:
        yield lower_bound
        lower_bound += step


def f_range(s):
    elements = s.split(':')
    if len(elements) == 3:
        return list(_f_range(
            float(elements[0]),
            float(elements[1]),
            float(elements[2])
        ))
    raise ValueError(
        'Bad range format: have to be $lower_bound:$upper_bound:$step'
    )


def logger(key, value):
    Run.get_context().log(key, value)
    print(key + ': ' + str(value))
