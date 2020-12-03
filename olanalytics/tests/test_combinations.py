import olanalytics.combinations as lib


def test_combinations_ij():

    n = 20
    for index, ij in enumerate(lib.combinations_ij(n)):
        assert lib.S(*ij, n) == index
        assert lib.S_inv(index, n) == ij
