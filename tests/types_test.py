from fugit.types import SignedInteger


def test_signed_int_ineq():
    neg_one = SignedInteger("-1")
    neg_zer = SignedInteger("-0")
    pos_zer = SignedInteger("+0")
    pos_one = SignedInteger("+1")

    assert (neg_one == -1.0) is True
    assert (neg_zer == -0.0) is True
    assert (pos_zer == +0.0) is True
    assert (pos_one == +1.0) is True

    assert (neg_one == -1) is True
    assert (neg_zer == -0) is False  # ints don't store sign!
    assert (pos_zer == +0) is True
    assert (pos_one == +1) is True

    assert (neg_zer != 0) is True
    assert (neg_zer == 0) is False
    assert (neg_zer == 0) is False
    assert (neg_zer < 0) is True
    assert (neg_zer > 0) is False
    assert (neg_zer.is_positive) is False

    assert (pos_one > 0) is True
    assert (pos_one < 0) is False
    assert (pos_one.is_positive) is True

    assert (neg_one < 0) is True
    assert (neg_one > 0) is False
    assert (neg_one.is_positive) is False
