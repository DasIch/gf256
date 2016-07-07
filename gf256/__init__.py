"""
    gf256
    ~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from operator import itemgetter
try:
    from gf256._speedups import lib as _speedups
except ImportError:
    _speedups = None


#: The version as a string.
__version__ = '0.2.0'

#: The version as a tuple. Use this for any comparisions, you may need to make.
__version_info__ = (0, 2, 0)


def _polymul(a, b):
    """
    Returns the product of two polynomials using carry-less addition.
    """
    product = 0
    while a:
        product ^= (a & 1) * b
        b <<= 1
        a >>= 1
    return product


def _polydiv(dividend, divisor):
    """
    Returns the quotient computed using euclidean division.
    """
    if divisor == 0:
        raise ZeroDivisionError()

    quotient = 0
    remainder = dividend
    while remainder.bit_length() >= divisor.bit_length():
        # We want to create a product that multiplied with the divisor produces
        # the highest product found in the remainder. So we figure out what the
        # exponent for that product has to be and create a polynomial where the
        # corresponding coefficient is set to 1.
        product = 1 << (remainder.bit_length() - divisor.bit_length())
        # Add that product to the quotient.
        quotient ^= product
        # Multiply with divisor and subtract from the remainder.
        remainder ^= _polymul(product, divisor)
    return quotient


class _GF256Base:
    def __init__(self, n):
        if not 0 <= n < 256:
            raise ValueError('{} is not in range(0, 256)'.format(n))
        self.n = n

    def to_polynomial_string(self):
        """
        Returns a string representation of the polynomial:

        >>> GF256(0b00011011).to_polynomial_string()
        'x**4 + x**3 + x + 1'
        """
        products = [
            'x**{}'.format(exponent) for exponent in range(7, 1, -1)
            if (self.n >> exponent) & 1
        ]
        if (self.n >> 1) & 1:
            products.append('x')
        if self.n & 1 or not products:
            products.append(str(self.n & 1))
        return ' + '.join(products)

    def __add__(self, other):
        if isinstance(other, _GF256Base):
            return self.__class__(self.n ^ other.n)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, _GF256Base):
            return self.__class__(self.n ^ other.n)
        return NotImplemented

    def __pow__(self, other):
        # modulo not supported
        if isinstance(other, _GF256Base):
            power = self.__class__(1)
            for _ in range(int(other)):
                power *= self
            return power
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, _GF256Base):
            return self * other._multiplicative_inverse()
        return NotImplemented

    def __int__(self):
        return self.n

    def __hash__(self):
        return self.n

    def __eq__(self, other):
        if isinstance(other, _GF256Base):
            return self.n == other.n
        return NotImplemented

    def __repr__(self):
        return '{0.__class__.__qualname__}(0b{0.n:0>8b})'.format(self)


class GF256(_GF256Base):
    """
    Represents an element in GF(2 ** 8).

    You can do arithmetic using `+`, `-`, `*`, `/` and `**`. Additionally `==`
    and `!=` operations are implemented. GF256 objects are hashable and can be
    used as keys. Use `int()` to turn an object into an integer.
    """

    #: The irreducible polynomial `x**8 + x**4 + x**3 + x + 1` used as a
    #: modulus for multiplication.
    #:
    #: This particular polynomial was chosen due to it's use in AES.
    irreducible_polynomial = 0b100011011

    def __mul__(self, other):
        if isinstance(other, GF256):
            # We multiply using binary multiplication modulo
            # :attr:`irreducible_polynomial`.
            #
            # The algorithm takes two factors `a` and `b` and iteratively
            # halves `a` and doubles `b`. The product is then the sum of all
            # `b`s whose corresponding `a` is odd, modulo the modulus.
            #
            # In an effort to try to be invulnerable to timing side channel
            # attacks, this implementation does exactly the same thing, in
            # terms of which operations are executed and in what order, no
            # matter what the inputs are.

            a, b = self.n, other.n
            product = 0
            # We can't let either `a` or `b` have any impact on how many
            # iterations we perform because that would leak information about
            # `a` and `b` through the runtime. Instead we perform one iteration
            # per bit.
            #
            # This means that there will be iterations where `a == 0` and we
            # already have the finished product.
            for _ in range(8):
                # If `a` is odd, add `b` to the product.
                product ^= (a & 1) * b

                # Double `b`. If the carry `(b >> 7)` is `1` and therefore
                # `(b << 1)` overflows, continue with the remainder
                # `(b << 1) % self.irreducible_polynomial`.
                #
                # In implementing the modulo operation we can take advantage of
                # the fact that in case of an overflow `(b << 1)` is a
                # polynomial of degree 8 and that the irreducible polynomial is
                # also a polynomial of degree 8. A single subtraction
                # (exclusive or in this field) is therefore enough to get the
                # remainder.
                b = (b << 1) ^ ((b >> 7) * self.irreducible_polynomial)

                # Halve `a` by shifting it one bit to the right.
                a >>= 1
            return self.__class__(product)
        return NotImplemented

    if _speedups:
        def __mul__(self, other):  # noqa
            if isinstance(other, GF256):
                return self.__class__(_speedups.polymulmod(
                    self.n, other.n, self.irreducible_polynomial
                ))
            return NotImplemented

        def __truediv__(self, other):
            if isinstance(other, GF256):
                if other.n == 0:
                    raise ZeroDivisionError()
                return self.__class__(_speedups.polydivmod(
                    self.n, other.n, self.irreducible_polynomial
                ))
            return NotImplemented

    def _multiplicative_inverse(self):
        """
        Returns the multiplicative inverse that is the element that, if
        multiplied with the one this method was called on produced 1::

            element * element._multiplicative_inverse() == 1

        Such an inverse exists for all elements except 0, for which a
        :exc:`ZeroDivisionError` is raised.
        """
        if self == self.__class__(0):
            raise ZeroDivisionError()

        # We use a variant of the *extended Euclidean algorithm* to find the
        # multiplicative inverse.
        #
        # The extended Euclidean algorithm computes - in addition to the
        # greatest common divisor (gcd) which the Euclidean algorithm computes
        # - two integers `s` and `t` such that::
        #
        #   s*a + t*b == gcd(a, b)
        #
        # In our case `gcd(a, b) == 1` holds, applying equivalence
        # transformations we can show that `t` is the multiplicative inverse.
        #
        #       s*a + t*b == 1      | % a
        #    => 0*a + t*b == 1 % a
        #   <=>       t*b == 1 % a
        #
        # You can easily find explanations that describe the algorithm, instead
        # we'll only cover the differences to the textbook definition and
        # application specific details here.
        #
        # The algorithm calls for Euclidean division, :func:`_polydiv`
        # implements that for polynomials. The function defintition has more
        # information on how that is implemented.
        #
        # The sequence of remainders computed as part of the algorithm includes
        # the modulus, which in our case is the irreducible polynomial. This
        # means that the remainders are not (all) elements of `GF(2**8)`.
        # `quotient` and through that `t` are also affected by this issue. In
        # order to deal this issue, we use multiplication without the modulo
        # part here.
        #
        # Subtraction is defined as exclusive or in `GF(2**8)`, so we
        # use that instead of subtraction in the algorithm.
        old_t, t = 0, 1
        old_r, r = self.irreducible_polynomial, self.n
        while r != 0:
            quotient = _polydiv(old_r, r)
            old_r, r = r, old_r ^ _polymul(quotient, r)
            old_t, t = t, old_t ^ _polymul(quotient, t)

        # old_r is the gcd. The gcd should always be 1 here. If it isn't, this
        # would indicate that either `self` is 0 (which a check above prevents)
        # or that the :attr:`irreducible_polynomial` isn't actually
        # irreducible.
        assert old_r == 1  # old_r is the gcd
        return self.__class__(abs(old_t))


class GF256LT(_GF256Base):
    """
    Represents an element in `GF(2 ** 8)`, implemented using lookup tables for
    fast multiplication and division.

    Works like :class:`GF256`.
    """

    generator = 3
    exponentiation_table = [
        int(GF256(3) ** GF256(i)) for i in range(255)
    ]
    logarithm_table = [
        logarithm
        for logarithm, exponent in sorted(
            enumerate(exponentiation_table, 0),
            key=itemgetter(1)
        )
    ]

    def __mul__(self, other):
        if isinstance(other, GF256LT):
            if self.n == 0 or other.n == 0:
                return self.__class__(0)
            return self.__class__(self.exponentiation_table[
                (
                    self.logarithm_table[self.n - 1]
                    + self.logarithm_table[other.n - 1]
                ) % 255
            ])
        return NotImplemented

    if _speedups:
        def __mul__(self, other):  # noqa
            if isinstance(other, GF256LT):
                return self.__class__(_speedups.polymulmodlt(self.n, other.n))
            return NotImplemented

        def __truediv__(self, other):
            if isinstance(other, GF256LT):
                if other.n == 0:
                    raise ZeroDivisionError()
                return self.__class__(_speedups.polydivmodlt(self.n, other.n))
            return NotImplemented

    def _multiplicative_inverse(self):
        if self.n == 0:
            raise ZeroDivisionError()
        return self.__class__(
            self.exponentiation_table[
                (-self.logarithm_table[self.n - 1]) % 255
            ]
        )
