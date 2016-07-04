#!/usr/bin/env python3.5
"""
    benchmark
    ~~~~~~~~~

    A simple benchmark to figure out how much time arithmetic operations take.

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import timeit


REPEAT = 3
NUMBER = 1000000


def benchmark(stmt, **kwargs):
    kwargs['stmt'] = stmt
    number = kwargs.get('number', NUMBER)
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


def benchmark_implementation(class_name, repeat=REPEAT, number=NUMBER):
    setup = '\n'.join([
        'import random',
        'from gf256 import {class}',
        'a = {class}(random.randrange(256))',
        'b = {class}(random.randrange(256))'
    ]).format(**{'class': class_name})
    setup_nonzero_b = '\n'.join([
        'import random',
        'from gf256 import {class}',
        'a = {class}(random.randrange(256))',
        'b = {class}(random.randrange(1, 256))'
    ]).format(**{'class': class_name})
    benchmarks = [
        ('Addition', 'a + b', setup),
        ('Subtraction', 'a - b', setup),
        ('Multiplication', 'a * b', setup),
        ('Division', 'a / b', setup_nonzero_b)
    ]
    for label, statement, setup in benchmarks:
        execution_time = benchmark(
            statement, setup=setup, repeat=repeat, number=number
        )
        yield label, execution_time


def main():
    implementations = ['GF256', 'GF256LT']
    for implementation in implementations:
        print('Benchmarking: {}'.format(implementation))
        results = list(benchmark_implementation(implementation))
        max_label_length = max(len(label) for label, _ in results)
        for operation, execution_time in results:
            print('{}: {} {}'.format(
                operation,
                ' ' * (max_label_length - len(operation)),
                execution_time
            ))
        print()


if __name__ == '__main__':
    main()
