"""
    speedups_build
    ~~~~~~~~~~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from cffi import FFI

from gf256 import GF256LT


ffibuilder = FFI()

ffibuilder.cdef("""
    uint32_t polymulmod(uint32_t a, uint32_t b, uint32_t modulus);
    uint32_t polymul(uint32_t a, uint32_t b);
    uint32_t polydiv(uint32_t divisor, uint32_t dividend);
    uint32_t modinverse(uint32_t n, uint32_t modulus);
    uint32_t polydivmod(uint32_t a, uint32_t b, uint32_t modulus);

    uint32_t polymulmodlt(uint32_t a, uint32_t b);
    uint32_t modinverselt(uint32_t n);
    uint32_t polydivmodlt(uint32_t a, uint32_t b);
""")

ffibuilder.set_source('gf256._speedups', """
    static uint32_t EXPONENTIATION_TABLE[255] = {%(exponentiation_table)s};
    static uint32_t LOGARITHM_TABLE[255] = {%(logarithm_table)s};

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

    uint32_t polydivmod(uint32_t a, uint32_t b, uint32_t modulus) {
        return polymulmod(a, modinverse(b, modulus), modulus);
    }

    uint32_t polymulmodlt(uint32_t a, uint32_t b) {
        if (a == 0 || b == 0) {
            return 0;
        }
        return EXPONENTIATION_TABLE[
            (LOGARITHM_TABLE[a - 1] + LOGARITHM_TABLE[b - 1]) %% 255
        ];
    }

    uint32_t modinverselt(uint32_t n) {
        return EXPONENTIATION_TABLE[(255 - LOGARITHM_TABLE[n - 1]) %% 255];
    }

    uint32_t polydivmodlt(uint32_t a, uint32_t b) {
        return polymulmodlt(a, modinverselt(b));
    }
""" % {
    'exponentiation_table': ', '.join(map(str, GF256LT.exponentiation_table)),
    'logarithm_table': ', '.join(map(str, GF256LT.logarithm_table)),
})


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
