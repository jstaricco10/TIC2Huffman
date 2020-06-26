#! /usr/bin/env python3

import argparse
import os
import struct
import mmap
from collections import namedtuple


def decompress(huff, args, sym_arraylen, filelen, sym_arraysize):
    """decompress: Descompresion del archivo .huff en un nuevo .orig

    Args:
        huff ([type]): [description]
        args ([type]): [description]
        sym_arraylen ([type]): [description]
        filelen ([type]): [description]
        sym_arraysize ([type]): [description]

    Returns:
        [type]: [description]
    """
    # print(huff)
    with open(args.file, 'rb') as file:
        mmp = mmap.mmap(file.fileno(), length=0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
        mmp.seek(8 + 6 * sym_arraylen)  # ignoramos el cabezal y el sym array

        codificado = ''
        ceros = '00000000'
        while True:
            b = mmp.read(1)  # lee byts y cuando se acaba corta
            if not b:
                break
            byte = struct.unpack('>B', b)[0]
            byte = str(bin(byte)).lstrip('0b')  # se saca el 0b de binario
            end = 8 - len(byte)
            byte = ceros[0:end] + byte  # se ponene los ceros a la izquierda de cada byte
            codificado += byte  # se pone cada byte en un string todos seguidos
        newfile = open(args.file[:-4] + "orig", 'wb')

        codigo = ''
        for dig in codificado:  # va formando cadenas de ceros y unos en codigo agregando de a 1
            # desde el primer digito de codificado
            # y cuando esa cadena es key del diccionario huff entonces se agrega
            # el symbolo de esa key al archivo
            codigo = codigo + dig
            if codigo in huff.keys():
                tuplaHuff = huff.get(codigo)
                if codigo == tuplaHuff.code and newfile.tell() != filelen:  # la ultima parte del if hace q no se
                    # tengan en cuenta los bits de relleno
                    newfile.write(tuplaHuff.symbol)
                    codigo = ''

        file.close()

        size = newfile.tell()
        newfile.close()
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
        mmp = mmap.mmap(file.fileno(), length=0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
        mn = mmp.read(2).decode()  # se saca el magic number del cabezal
        if mn != 'JA':  # se comprueba que el archivo empiece con magic number
            return print(
                "El archivo no es valido para descomprimir, tiene un numero magico que no es el de la compresion.")
        sym_arraylen = ord(mmp.read(1)) + 1  # se guardan el resto de datos del cabezal
        sym_arraysize = ord(mmp.read(1))
        filelen = struct.unpack('!i', mmp.read(4))[0]
        huffCode = namedtuple('huffCode', 'symbol size code')
        huff = {}
        for _ in range(sym_arraylen):  # se crea un diccionario con clave codigo huff y valor una tupla con el
            # symbolo de ese codigo, el tamano del huff cofde y el huff code
            symbol = mmp.read(1)
            size = mmp.read(1)
            size = int.from_bytes(size, byteorder='big')
            code = mmp.read(4)
            huff[f'%0{size}d' % (struct.unpack('>I', code)[0])] = (
                huffCode(symbol, size, f'%0{size}d' % (struct.unpack('>I', code)[0])))

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
