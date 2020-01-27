from starrynight import Numerical, Brute
import numpy as np
import pytest


def run(args_list):
    N = Numerical()
    B = Brute()
    for args in args_list:
        N.b, N.theta, N.bo, N.ro = args
        B.b, B.theta, B.bo, B.ro = args
        print("{:5.3f} / {:5.3f}".format(N.flux(), B.flux()))


def test_simple():
    run(
        [
            [0.5, 0.1, 1.2, 0.1],
            [0.5, 0.1, 0.1, 1.2],
            [0.5, 0.1, 0.8, 0.1],
            [0.5, 0.1, 0.9, 0.2],
            [0.5, np.pi + 0.1, 0.8, 0.1],
            [0.5, np.pi + 0.1, 0.9, 0.2],
            [0.5, 0.1, 0.5, 1.25],
            [0.5, np.pi + 0.1, 0.5, 1.25],
        ]
    )


def test_PQT():
    run(
        [
            # b > 0
            [0.4, np.pi / 3, 0.5, 0.7],
            [0.4, 2 * np.pi - np.pi / 3, 0.5, 0.7],
            [0.4, np.pi / 2, 0.5, 0.7],
            [0.4, np.pi / 2, 1.0, 0.2],
            [0.00001, np.pi / 2, 0.5, 0.7],
            [0, np.pi / 2, 0.5, 0.7],
            [0.4, -np.pi / 2, 0.5, 0.7],
            # b < 0
            [-0.4, np.pi / 3, 0.5, 0.7],
            [-0.4, 2 * np.pi - np.pi / 3, 0.5, 0.7],
            [-0.4, np.pi / 2, 0.5, 0.7],
        ]
    )


def test_PT():
    run(
        [
            # b > 0
            [0.4, np.pi / 6, 0.3, 0.3],
            [0.4, np.pi + np.pi / 6, 0.1, 0.6],
            [0.4, np.pi + np.pi / 3, 0.1, 0.6],
            [0.4, np.pi / 6, 0.6, 0.5],
            [0.4, -np.pi / 6, 0.6, 0.5],
            [0.4, 0.1, 2.2, 2.0],
            [0.4, -0.1, 2.2, 2.0],
            [0.4, np.pi + np.pi / 6, 0.3, 0.8],
            [0.75, np.pi + 0.1, 4.5, 5.0],
            # b < 0
            [-0.95, 0.0, 2.0, 2.5],
            [-0.1, np.pi / 6, 0.6, 0.75],
            [-0.5, np.pi, 0.8, 0.5],
            [-0.1, 0.0, 0.5, 1.0],
        ]
    )


def test_triple():
    run(
        [
            [
                0.5488316824842527,
                4.03591586925189,
                0.34988513192814663,
                0.7753986686719786,
            ],
            [
                0.5488316824842527,
                2 * np.pi - 4.03591586925189,
                0.34988513192814663,
                0.7753986686719786,
            ],
            [
                -0.5488316824842527,
                4.03591586925189 - np.pi,
                0.34988513192814663,
                0.7753986686719786,
            ],
            [
                -0.5488316824842527,
                2 * np.pi - (4.03591586925189 - np.pi),
                0.34988513192814663,
                0.7753986686719786,
            ],
        ]
    )


def test_quadruple():
    run(
        [[0.5, np.pi, 0.99, 1.5], [-0.5, 0.0, 0.99, 1.5],]
    )


@pytest.mark.xfail
def test_edge_cases():
    run(
        [[0.5, np.pi, 1.0, 1.5],]
    )
