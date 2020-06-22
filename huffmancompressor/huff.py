#! /usr/bin/env python3

from heapq import heappush, heappop, heapify
from collections import defaultdict, namedtuple
import argparse
import os
import struct

# traducir huff a named tuple huff(symbol,code), named tuple no porque una tupla no permite asignacion, debe ser un dict


def encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights"""
    huffCode = namedtuple('huffCode', ' symbol code')
    lista = []
    # print(symb2freq)
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    # debemos hacer esto con el pop del heap salteando el primero, hay que optimizar esto
    salteodelprimero = 0
    for elem in heappop(heap):
        if salteodelprimero == 0:
            salteodelprimero += 1
        else:
            pop = elem
            lista.append(huffCode(pop[0], pop[1]))
    # ordeno por codigo??, con item y atr getter de la letra
    return lista


""" Comprimimos el archivo en uno nuevo con .huf"""


def compress(huff, args):
    file = open(args.file, 'rb')
    # Datos del cabezal
    numeromagico = 'JA'
    sym_arraylen = len(huff)
    sym_arraysize = len(huff[-1])
    filelen = os.stat(args.file).st_size

    # Armamos el codificado total, los datos en si comprimidos
    codificadoTotal = ''
    while True:
        b = file.read(1)
        if not b:
            break
        for h in huff:
            if b == h.symbol:
                codificado = h.code
                codificadoTotal += codificado
    # debemos agregar en cod total los 0 al final que falten para tener tamano multiplo de 8
    cantAAgregar = 8 - (len(codificadoTotal) % 8)
    for _ in range(cantAAgregar):
        codificadoTotal += '0'
    if len(codificadoTotal) / 8 > filelen and not args.force:
        file.close()
        return

    # comentado para trabajar mientras con archivos chicos sin -f
    # if not args.force:
    #     if filelen < len(codificadoTotal):
    #         print("El archivo resultante comprimido es mas grande que el dado.")
    #         file.close()
    #         return
    newfile = open(args.file + ".huff", 'wb')
    # print(sym_arraylen)
    # print(sym_arraysize)
    # print(filelen)
    newfile.write(struct.pack('>ccBBI', numeromagico[0].encode(encoding='ascii'),
                              numeromagico[1].encode(encoding='ascii'), sym_arraylen-1, sym_arraysize, filelen))
    # Ahora se debe agregar un array de elementos de 6 bytes, cada uno de los cuales identifica un símbolo, su tamano y
    # su código Huffman. En nuestro caso estos datos estan en huff
    for elem in huff:
        symb = elem.symbol
        size = len(elem.code)  # .to_bytes(1, byteorder='big')  este se agrega en 1 byte
        code = elem.code  # se agrega en 6 bytes aunque sea mas corto, como lo meto en 6 bytes??
        newfile.write(struct.pack('>cBI', symb, size, int(code)))

    print(huff)
    for x in range(0, len(codificadoTotal), 8):
        newfile.write(struct.pack('>B', int(codificadoTotal[x: x + 8], 2)))  # I o x o c? por tamano
    newfile.close()
    file.close()
    return


def main():
    parser = argparse.ArgumentParser(description='Parsea los datos pasados en consola')
    parser.add_argument('file', help='Archivo a comprimir')
    parser.add_argument('-f', '--force', help='Fuerza compresion aunque aumente el tamano', action='store_true')
    parser.add_argument('-v', '--verbose', help='Imprime informacion del avance del proceso', action='store_true')
    args = parser.parse_args()
    file = open(args.file, 'rb')
    symb2freq = defaultdict(int)
    while True:
        b = file.read(1)
        if not b:
            break
        symb2freq[b] += 1
    huff = encode(symb2freq)
    file.close()
    if args.verbose:
        print("Symbol\tWeight\tHuffman Code")
        for p in huff:
            print("%s\t%s\t%s" % (p.symbol, symb2freq[p.symbol], p.code))
    compress(huff, args)


if __name__ == '__main__':
    main()
    os._exit(0)
