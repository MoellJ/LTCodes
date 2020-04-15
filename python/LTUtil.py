import sys

def get_bytes_from_file(filename):
    with open(filename, 'rb') as input_file:
        return input_file.read()

def is_pow_of_two(input):
    return count_bits(input) == 1

def count_bits(input):
    num = 0
    if input == 0:
        return 0
    c = 0; iv = input
    while iv > 0:
        iv = iv & (iv -1)
        c = c + 1
    num = num + c
    return num


def byte_xor(var, key):
    int_var = int.from_bytes(var, sys.byteorder)
    int_key = int.from_bytes(key, sys.byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)