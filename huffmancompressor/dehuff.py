#! /usr/bin/env python3

import argparse
import os
import struct
from collections import namedtuple


def main():
    parser = argparse.ArgumentParser(description='Parsea los datos pasados en consola')
    parser.add_argument('file', help='Archivo a descomprimir')
    parser.add_argument('-v', '--verbose', help='Imprime informacion del avance del proceso', action='store_true')
    # con el parser debo procesar el nombre del archivo
    args = parser.parse_args()
    file = open(args.file, 'rb')  # debemos controlar el caso de que el file no sea encontrado\
    # Debemos leer el sym array y armar un dicc de named tuples con cada codigo y su correspondiente simbolo
    mn = file.read(2)
    print(mn)
    sym_arraylen = ord(file.read(1)) + 1
    sym_arraysize = ord(file.read(1))
    filelen = file.read(4)
    print(sym_arraylen)
    huffCode = namedtuple('huffCode', ' symbol code')
    huff = []
    for _ in range(sym_arraylen):
        symbol = file.read(1)
        size = file.read(1)
        code = file.read(4)
        print(code)


if __name__ == '__main__':
    main()
    os._exit(0)
