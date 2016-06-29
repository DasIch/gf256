"""
    speedups_build
    ~~~~~~~~~~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from cffi import FFI


ffibuilder = FFI()

ffibuilder.cdef("""
    uint32_t polymulmod(uint32_t a, uint32_t b, uint32_t modulus);
    uint32_t polymul(uint32_t a, uint32_t b);
    uint32_t polydiv(uint32_t divisor, uint32_t dividend);
    uint32_t modinverse(uint32_t n, uint32_t modulus);
""")

ffibuilder.set_source('gf256._speedups', """
    uint32_t polymulmod(uint32_t a, uint32_t b, uint32_t modulus) {
        uint32_t product = 0;
        int i;
        for (i = 0; i < 8; i++) {
            product ^= (a & 1) * b;
            b = (b << 1) ^ ((b >> 7) * modulus);
            a >>= 1;
        }
        return product;
    }

    uint32_t polymul(uint32_t a, uint32_t b) {
        uint32_t product = 0;
        while (a) {
            product ^= (a & 1) * b;
            b <<= 1;
            a >>= 1;
        }
        return product;
    }

    static uint32_t bit_length(uint32_t n) {
        uint32_t length = 0;
        while (n != 0) {
            length++;
            n >>= 1;
        }
        return length;
    }

    uint32_t polydiv(uint32_t dividend, uint32_t divisor) {
        uint32_t quotient = 0;
        uint32_t remainder = dividend;
        uint32_t product;
        while (bit_length(remainder) >= bit_length(divisor)) {
            product = 1 << (bit_length(remainder) - bit_length(divisor));
            quotient ^= product;
            remainder ^= polymul(product, divisor);
        }
        return quotient;
    }

    uint32_t modinverse(uint32_t n, uint32_t modulus) {
        uint32_t old_t = 0;
        uint32_t t = 1;
        uint32_t old_r = modulus;
        uint32_t r = n;
        uint32_t temp;
        while (r != 0) {
            uint32_t quotient = polydiv(old_r, r);
            temp = r;
            r = old_r ^ polymul(quotient, r);
            old_r = temp;
            temp = t;
            t = old_t ^ polymul(quotient, t);
            old_t = temp;
        }
        return old_t;
    }
""")


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
