#! /usr/bin/env python3

import argparse
import os
import struct
from collections import namedtuple


def decompress(huff, args, sym_arraylen, filelen):
    file = open(args.file, 'rb')
    file.seek(8 + 6 * sym_arraylen)  # ignoramos el cabezal y el sym array
#    byte = struct.unpack('>B', file.read(1))[0]  # nos quedamos con la posicion 0 ya que unpack nos da una tupla
#    print(type(bin(byte)))
#    byte2 = file.read(1)
#    print(type(byte2))
    codificado = ''
    ceros = '00000000'
    while True:
        b = file.read(1)
        if not b:
            break
        byte = struct.unpack('>B',b)[0]
        byte = str(bin(byte)).lstrip('0b')
        end = 8-len(byte)
        byte = ceros[0:end] + byte
        codificado += byte
    newfile = open(args.file[:-4] + "orig", 'wb')
    sizeOp = 0
    while sizeOp != filelen:    #filelen
        for cod in huff:
            if codificado.startswith(cod[2]):
                newfile.write(cod[0])
                codificado = codificado[cod[1]:]
                sizeOp +=1
                break
                
#    while True:
#        byte = file.read(1)
#        print(byte)
#        if not byte:
#            break
#        for h in huff:
#            codificado = ''
#            for bit in byte:
#                #print(bin(byte))
#                codificado += bit.decode()
#                if codificado == h.code:
#                    decodificadoTotal += h.symbol
#                    codificado = ''



    newfile.close()
    file.close()
    pass


def main():
    parser = argparse.ArgumentParser(description='Parsea los datos pasados en consola')
    parser.add_argument('file', help='Archivo a descomprimir')
    parser.add_argument('-v', '--verbose', help='Imprime informacion del avance del proceso', action='store_true')
    # con el parser debo procesar el nombre del archivo
    args = parser.parse_args()
    file = open(args.file, 'rb')  # debemos controlar el caso de que el file no sea encontrado\
    # Debemos leer el sym array y armar un dicc de named tuples con cada codigo y su correspondiente simbolo
    mn = file.read(2)
    sym_arraylen = ord(file.read(1)) + 1
    sym_arraysize = ord(file.read(1))
    filelen = struct.unpack('!i', file.read(4))[0]
    huffCode = namedtuple('huffCode', ' symbol size code')
    huff = []
    for _ in range(sym_arraylen):
        symbol = file.read(1)
        size = file.read(1)
        size = int.from_bytes(size, byteorder='big')
        code = file.read(4)
        huff.append(huffCode(symbol, size, f'%0{size}d' % (struct.unpack('>I', code)[0],)))
    decompress(huff, args, sym_arraylen, filelen)
    file.close()


if __name__ == '__main__':
    main()
    os._exit(0)
