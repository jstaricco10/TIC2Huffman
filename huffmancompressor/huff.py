#! /usr/bin/env python3


from heapq import heappush, heappop, heapify
from collections import defaultdict, namedtuple
import argparse
import os
import struct
import mmap


def encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights

    Returns:
        [list]: [retorna una lista con los caracteres y su huff code corespondiente]
    """
    huffCode = namedtuple('huffCode', ' symbol code')
    lista = []
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
    # debemos hacer esto con el pop del heap salteando el primero, hay que optimizar esto > HECHO
    for elem in heappop(heap)[1:]:
        lista.append(huffCode(elem[0], elem[1]))
    return lista


def compress(huff, args, filelen):
    """compress Comprimimos el archivo en uno nuevo con .huff

    Args:
        huff ([list]): una lista con los caracteres y su huff code corespondiente
        args : argumentos pasados al programa, obligatoriamente un archivo a comprimir y 
               opcionalmente flags: -f para comprimir aunque el compreso sea mas grande
               y -v para ver detalles de la compresion
        filelen ([int]): tamano en bytes del archivo a comprimir

    Returns:
        [int]: tamano en bytes del archivo compresso
    """
    try:
        with open(args.file, 'rb') as file:
            mmp = mmap.mmap(file.fileno(), length=0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
            # Datos del cabezal
            numeromagico = 'JA'
            sym_arraylen = len(huff)
            sym_arraysize = len(huff[-1])

            # Armamos el codificado total, los datos en si comprimidos
            codificadoTotal = ''
            while True:
                b = mmp.read(1)
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
            # El largo del archivo comprimido es el largo del symarray por el tamano de cada uno de sus elementos mas
            # el largo del bit stream (que es el codificado total)
            compressedfilelen = (len(codificadoTotal) / 8 + len(
                huff) * 6) + 8  # 8 bytes ocupa el cabezal, cada entrada en
            # huff ocupa 6 bytes y se suma los bytes del codificado
            if not args.force:
                if filelen < compressedfilelen:
                    print("El archivo resultante comprimido es mas grande que el dado.")
                    file.close()
                    return None
            newfile = open(args.file + ".huff", 'wb')

            newfile.write(struct.pack('>ccBBI', numeromagico[0].encode(encoding='ascii'),
                                      numeromagico[1].encode(encoding='ascii'), sym_arraylen - 1, sym_arraysize,
                                      filelen))
            # Ahora se debe agregar un array de elementos de 6 bytes, cada uno de los cuales identifica un símbolo,
            # su tamano y su código Huffman. En nuestro caso estos datos estan en huff
            for elem in huff:
                symb = elem.symbol
                size = len(elem.code)  # .to_bytes(1, byteorder='big')  este se agrega en 1 byte
                code = elem.code  # se agrega en 6 bytes aunque sea mas corto, como lo meto en 6 bytes??
                #        print(symb,size,int(code))
                newfile.write(struct.pack('>cBI', symb, size, int(code)))

            for x in range(0, len(codificadoTotal), 8):
                newfile.write(struct.pack('>B', int(codificadoTotal[x: x + 8], 2)))  # I o x o c? por tamano

            newfile.close()
            file.close()

            return compressedfilelen
    except OSError as err:
        print("El error es " + "OS error: {0}".format(err))
        return


def main():
    parser = argparse.ArgumentParser(description='Comprime archivos usando un arbol de Huffman')
    parser.add_argument('file', help='Nombre del archivo a comprimir')
    parser.add_argument('-f', '--force', help='Fuerza compresion aunque el archivo resultante sea mas grande',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Imprime informacion del avance del proceso', action='store_true')
    args = parser.parse_args()
    try:
        filelen = os.path.getsize(args.file)
        file = open(args.file, 'rb')
        mmp = mmap.mmap(file.fileno(), length=0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
        symb2freq = defaultdict(int)
        while True:
            b = mmp.read(1)
            if not b:
                break
            symb2freq[b] += 1
        huff = encode(symb2freq)
        file.close()
        newLen = compress(huff, args, filelen)
        if newLen is not None:
            if args.verbose:
                print("Symbol\tWeight\tHuffman Code")
                for p in huff:
                    print("%s\t%s\t%s" % (p.symbol, symb2freq[p.symbol], p.code))
            if args.verbose:
                print(f"El tamano viejo del archivo era de: {filelen} bytes")
                print(f"El tamano del archivo comprimido .huff es de: {newLen} bytes")
    except OSError as err:
        print("El error es " + "OS error: {0}".format(err))


if __name__ == '__main__':
    main()
    os._exit(0)
