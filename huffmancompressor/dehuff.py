#! /usr/bin/env python3

import argparse
import os
import struct
from collections import namedtuple


def decompress(huff, args, sym_arraylen, filelen, sym_arraysize):
    file = open(args.file, 'rb')
    file.seek(8 + 6 * sym_arraylen)  # ignoramos el cabezal y el sym array

    codificado = ''
    ceros = '00000000'

    while True:
        b = file.read(1)  # lee byts y cuando se acaba corta
        if not b:
            break
        byte = struct.unpack('>B', b)[0]
        byte = str(bin(byte)).lstrip('0b')  # se saca el 0b de binario
        end = 8 - len(byte)
        byte = ceros[0:end] + byte  # se ponene los ceros a la izquierda de cada byte
        codificado += byte  # se pone cada byte en un string todos seguidos
    newfile = open(args.file[:-4] + "orig", 'wb')
    sizeOp = 0
    decod = ''
    for _ in range (filelen):       # se hace hasta tener la misma cantidad de caracteres que en el archivo original
        for cod in huff:
            if codificado.startswith(cod[2]):
                # si la cadena codificada empieza con uno de los codigos huff se agrega la letra de dicho codigo al
                # newfile
                decod += cod[0].decode()  #esto se usa para el verbose no mas, va imprimiendo el decodificado
                newfile.write(cod[0])
                codificado = codificado[cod[1]:]  # se saca el codigo huff de la letra ya escrita en el newfile
#                if args.verbose:
#                    print(cod[0].decode())
                break
#    newfile.close()
    file.close()
    if args.verbose:
        print(decod)
#    newfile.seek(0,2) # move the cursor to the end of the file
    size = newfile.tell()
    newfile.close
    return size


def main():
    parser = argparse.ArgumentParser(description='Desomprime archivos usando un arbol de Huffman')
    parser.add_argument('file', help='Nombre del archivo a descomprimir')
    parser.add_argument('-v', '--verbose', help='Imprime informacion del avance del proceso', action='store_true')
    # con el parser debo procesar el nombre del archivo
    args = parser.parse_args()
    if args.file.endswith(".huff"):

        file = open(args.file, 'rb')  # debemos controlar el caso de que el file no sea encontrado\
        # Debemos leer el sym array y armar un dicc de named tuples con cada codigo y su correspondiente simbolo
        mn = file.read(2).decode()
        if mn != 'JA':
            return print("El archivo no es valido para descomprimir, tiene un numero magico que no es el de la compresion.")
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
        decompressedlen = decompress(huff, args, sym_arraylen, filelen, sym_arraysize)
        if args.verbose:
            print(f"El tamano del archivo antes de comprimido era de: {str(filelen)} bytes")
            print(f"El tamano del archivo comprimido era de: {os.stat(args.file).st_size} bytes")
            print(f"El tamano del archivo descomprimido es de: {str(decompressedlen)} bytes")
        file.close()
    else:
        print("el archivo debe terminar en .huff para ser descompreso")


if __name__ == '__main__':
    main()
    os._exit(0)
