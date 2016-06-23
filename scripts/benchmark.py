#!/usr/bin/env python3.5
"""
    benchmark
    ~~~~~~~~~

    A simple benchmark to figure out how much time arithmetic operations take.

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import timeit


SETUP = '\n'.join([
    'import random',
    'from gf256 import GF256',
    'a = GF256(random.randrange(256))',
    'b = GF256(random.randrange(256))'
])


SETUP_NONZERO_B = '\n'.join([
    'import random',
    'from gf256 import GF256',
    'a = GF256(random.randrange(256))',
    'b = GF256(random.randrange(1, 256))'
])

REPEAT = 3
NUMBER = 1000000


def benchmark(stmt, setup=SETUP, repeat=REPEAT, number=NUMBER, **kwargs):
    kwargs.update(stmt=stmt, setup=setup, repeat=REPEAT, number=number)
    execution_time = min(timeit.repeat(**kwargs))
    time_per_operation = execution_time * 1e6 / number
    precision = 3
    unit = 'µs'
    if time_per_operation > 1000:
        time_per_operation /= 1000
        precision += 3
        unit = 'ms'
    if time_per_operation > 1000:
        time_per_operation /= 1000
        precision += 3
        unit = 's'
    return '{:.{}} {}'.format(time_per_operation, precision, unit)


def main():
    benchmarks = [
        ('Addition', 'a + b', SETUP),
        ('Subtraction', 'a - b', SETUP),
        ('Multiplication', 'a * b', SETUP),
        ('Division', 'a / b', SETUP_NONZERO_B)
    ]
    max_label = max(len(label) for label, _, _ in benchmarks)
    for label, statement, setup in benchmarks:
        time_per_operation = benchmark(statement)
        print('{0}:{1} {2}'.format(
            label,
            ' ' * (max_label - len(label)),
            time_per_operation
        ))


if __name__ == '__main__':
    main()
