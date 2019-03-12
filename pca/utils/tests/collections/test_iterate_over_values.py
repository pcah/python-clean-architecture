
from pca.utils.collections import iterate_over_values


def test_iterate_over_standard_example():
    collection = {
        '1': 1,
        'list': [2, 3, 4],
        'tuple': (5, 6),
        'x': {
            '7': 7,
            '8': (8, 9),
        },
    }
    assert list(iterate_over_values(collection)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
