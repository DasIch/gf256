"""
    test_gf256
    ~~~~~~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import pytest
from hypothesis import assume, given
from hypothesis.strategies import integers

from gf256 import GF256, GF256LT, _polydiv


def test_polydiv():
    # _polydiv should never be called with 0 as a divisor in the regular code,
    # so the case won't be covered by any other tests. We do nevertheless want
    # the right thing to happen here, if something goes wrong.
    with pytest.raises(ZeroDivisionError):
        _polydiv(1, 0)


def create_test_class(GF256):
    gf256s = integers(min_value=0, max_value=255).map(GF256)

    class TestGF256:
        @given(integers())
        def test_init_fails_outside_of_range(self, a):
            """
            For all `a` such that `a < 0` or `a > 255`, `GF256(a)` should raise
            a :exc:`ValueError`.
            """
            assume(not (0 <= a < 256))
            with pytest.raises(ValueError):
                GF256(a)

        @pytest.mark.parametrize(('a', 'polynomial'), [
            (0b0, '0'),
            (0b1, '1'),
            (0b10, 'x'),
            (0b11, 'x + 1'),
            (0b11111111, 'x**7 + x**6 + x**5 + x**4 + x**3 + x**2 + x + 1')
        ])
        def test_to_polynomial_string(self, a, polynomial):
            assert GF256(a).to_polynomial_string() == polynomial

        @given(gf256s, gf256s)
        def test_distinct_hashes(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)` such that `a != b` the equation
            `hash(a) != hash(b)` should all, that is their hashes should be
            distinct.
            """
            assume(a != b)
            assert hash(a) != hash(b)

        @given(gf256s)
        def test_repr_evals_to_equal_obj(self, a):
            evaluated = eval(repr(a), {}, {GF256.__name__: GF256})
            assert evaluated == a

        @given(gf256s, gf256s)
        def test_closure_under_addition(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)`, `a + b` should be in
            `GF(2 ** 8)`.
            """
            c = a + b
            assert isinstance(c, GF256)
            assert 0 <= int(c) < 256

        @given(gf256s, gf256s)
        def test_closure_under_multiplication(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)`, `a * b` should be in
            `GF(2 ** 8)`.
            """
            c = a * b
            assert isinstance(c, GF256)
            assert 0 <= int(c) < 256

        @given(gf256s, gf256s, gf256s)
        def test_associativity_of_addition(self, a, b, c):
            """
            For all `a`, `b`, and, `c` in `GF(2 ** 8)` the equation
            `a + (b + c) == (a + b) + c` should hold.
            """
            assert a + (b + c) == (a + b) + c

        @given(gf256s, gf256s, gf256s)
        def test_associativity_of_multiplication(self, a, b, c):
            """
            For all `a`, `b`, and, `c` in `GF(2 ** 8)` the equation
            `a * (b * c) == (a * b) * c` should hold.
            """
            assert a * (b * c) == (a * b) * c

        @given(gf256s, gf256s)
        def test_commutativity_of_addition(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)` the equation `a + b == b + a`
            should hold.
            """
            assert a + b == b + a

        @given(gf256s, gf256s)
        def test_commutativity_of_multiplication(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)` `a * b == b * a` holds.
            """
            assert a * b == b * a

        @given(gf256s)
        def test_existence_of_additive_identity_element(self, a):
            """
            There exists exactly one element in `GF(2 ** 8)`, called the
            *additive identity* element, which is denotated by `0`. For all `a`
            in `GF(2 ** 8)` `a + 0 == a` holds.
            """
            zeros = {zero for zero in map(GF256, range(256)) if a + zero == a}
            assert len(zeros) == 1
            zero = zeros.pop()
            assert zero == GF256(0)

        @given(gf256s)
        def test_existence_of_multiplicative_identity_element(self, a):
            """
            There exists an element in `GF(2 ** 8)`, called the
            *multiplicative identity* element, which is denotated by `1`. For
            all `a` in `GF(2 ** 8)` the equation `a * 1  = a` should hold.
            """
            assert any(a * one == a for one in map(GF256, range(256)))

        @given(gf256s)
        def test_existence_of_additive_inverses(self, a):
            """
            For every `a` in `GF(2 ** 8)`, there exists an element `-a` in
            `GF(2 ** 8)` such that `a + (-a) = 0`.

            (This is required for subtraction to work.)
            """
            assert any(
                a + inverse == GF256(0) for inverse in map(GF256, range(256))
            )

        @given(gf256s)
        def test_existence_of_multiplicative_inverses(self, a):
            """
            For every `a` in `GF(2 ** 8)`, there exists an element
            `a**(-1)` in `GF(2 ** 8)` such that `a * (a ** (-1)) = 1`.

            (This is required for division to work.)
            """
            assume(a != GF256(0))  # You can't divide by zero
            assert any(
                a * inverse == GF256(1) for inverse in map(GF256, range(256))
            )

        @given(gf256s, gf256s, gf256s)
        def test_left_distributivity(self, a, b, c):
            """
            For all `a`, `b`, and `c` in `GF(2 ** 8)`,
            `a * (b + c) == (a * b) + (a * c)` holds.
            """
            assert a * (b + c) == (a * b) + (a * c)

        @given(gf256s, gf256s, gf256s)
        def test_right_distributivity(self, a, b, c):
            """
            For all `a`, `b`, and `c` in `GF(2 ** 8)`,
            `(b + c) * a == (b * a) + (c * a)` holds.
            """
            assert (b + c) * a == (b * a) + (c * a)

        @given(gf256s, gf256s)
        def test_subtraction(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)` with `c = a + b` the equation
            `c - b == a` holds.
            """
            c = a + b
            assert c - b == a

        @given(gf256s, gf256s)
        def test_division(self, a, b):
            """
            For all `a` and `b` in `GF(2 ** 8)` with `c = a * b` the equation
            `c / b == a` holds.
            """
            assume(b != GF256(0))
            c = a * b
            d = c / b
            assert d == a

        @given(gf256s)
        def test_divide_by_zero(self, a):
            with pytest.raises(ZeroDivisionError):
                a / GF256(0)

        @given(gf256s, gf256s)
        def test_pow(self, a, b):
            power_through_op = a ** b
            power_manually = GF256(1)
            for _ in range(int(b)):
                power_manually *= a
            assert power_through_op == power_manually

        @given(gf256s)
        def test_pow_of_one(self, a):
            assert a ** GF256(0) == GF256(1)

        @given(gf256s, gf256s)
        def test_equality(self, a, b):
            if a == b:
                assert int(a) == int(b)
            else:
                assert int(a) != int(b)

        @given(gf256s, gf256s)
        def test_inequality(self, a, b):
            if a != b:
                assert int(a) != b
            else:
                assert int(a) == int(b)

        @given(gf256s, gf256s)
        def test_equal_and_unequal_are_inverse(self, a, b):
            if a == b:
                assert not (a != b)
            else:
                assert a != b
            if a != b:
                assert not (a == b)
            else:
                assert a == b

        @given(integers(min_value=0, max_value=255))
        def test_int_coercion(self, a):
            assert int(GF256(a)) == a

        def test_addition_with_different_type(self):
            with pytest.raises(TypeError):
                GF256(1) + 1

        def test_subtraction_with_different_type(self):
            with pytest.raises(TypeError):
                GF256(1) - 1

        def test_multiplication_with_different_type(self):
            with pytest.raises(TypeError):
                GF256(1) * 1

        def test_pow_with_different_type(self):
            with pytest.raises(TypeError):
                GF256(1) ** 1

        def test_truediv_with_different_type(self):
            with pytest.raises(TypeError):
                GF256(1) / 1

    TestGF256.__name__ = 'Test{}'.format(GF256.__name__)
    return TestGF256


TestGF256 = create_test_class(GF256)
TestGF256LT = create_test_class(GF256LT)


class TestImplementationEquality:
    gf256s = integers(min_value=0, max_value=255)

    @given(gf256s, gf256s)
    def test_addition(self, a, b):
        assert int(GF256(a) + GF256(b)) == int(GF256LT(a) + GF256LT(b))

    @given(gf256s, gf256s)
    def test_subtraction(self, a, b):
        assert int(GF256(a) - GF256(b)) == int(GF256LT(a) - GF256LT(b))

    @given(gf256s, gf256s)
    def test_multiplication(self, a, b):
        assert int(GF256(a) * GF256(b)) == int(GF256LT(a) * GF256LT(b))

    @given(gf256s, gf256s)
    def test_division(self, a, b):
        assume(b != 0)
        assert int(GF256(a) / GF256(b)) == int(GF256LT(a) / GF256LT(b))
