"""Leitura/escrita de PNG só com a biblioteca padrão (zlib), sem Pillow.

Usado por tools/mk2_sprites.py para recortar as sheets do MK2 (SNES): elas têm
poucas cores, então não precisam de quantização — basta montar a paleta.

Imagens em memória: (w, h, px), onde px é uma lista de linhas e cada linha uma
lista de tuplas RGBA (ou None para transparente).
"""
import struct
import zlib


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def read(path):
    """PNG (8 bits; tons de cinza, RGB, paleta, RGBA, sem entrelaçamento) -> (w, h, linhas RGBA)."""
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    pos = 8
    idat = []
    pal = None
    trns = None
    while pos < len(data):
        n, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b'IHDR':
            w, h, depth, ctype, _, _, inter = struct.unpack('>IIBBBBB', body)
            assert depth == 8 and inter == 0, 'PNG não suportado: %s' % path
        elif kind == b'PLTE':
            pal = [tuple(body[i:i + 3]) for i in range(0, n, 3)]
        elif kind == b'tRNS':
            trns = body
        elif kind == b'IDAT':
            idat.append(body)
        elif kind == b'IEND':
            break
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b''.join(idat))
    stride = w * bpp
    prev = bytearray(stride)
    rows = []
    i = 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, prev))
        elif f == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                up_left = prev[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + _paeth(left, prev[x], up_left)) & 255
        rows.append(line)
        prev = line
    px = []
    for line in rows:
        if ctype == 2:
            row = [(line[x], line[x + 1], line[x + 2], 255) for x in range(0, stride, 3)]
        elif ctype == 6:
            row = [tuple(line[x:x + 4]) for x in range(0, stride, 4)]
        elif ctype == 3:
            row = [pal[v] + ((trns[v] if trns and v < len(trns) else 255),) for v in line]
        elif ctype == 0:
            row = [(v, v, v, 255) for v in line]
        else:
            row = [(line[x], line[x], line[x], line[x + 1]) for x in range(0, stride, 2)]
        px.append([None if c[3] < 110 else c[:3] for c in row])
    return w, h, px


def _chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)


def write_indexed(path, w, h, idx, palette):
    """Grava PNG paletizado (8 bits). idx: linhas de índices; índice 0 = transparente."""
    pal = list(palette) + [(0, 0, 0)] * (256 - len(palette))
    raw = b''.join(b'\x00' + bytes(row) for row in idx)
    out = b'\x89PNG\r\n\x1a\n'
    out += _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 3, 0, 0, 0))
    out += _chunk(b'PLTE', bytes(v for c in pal for v in c))
    out += _chunk(b'tRNS', b'\x00')
    out += _chunk(b'IDAT', zlib.compress(raw, 9))
    out += _chunk(b'IEND', b'')
    with open(path, 'wb') as fh:
        fh.write(out)


def write_rgba(path, w, h, px):
    """Grava PNG RGBA (para conferência/visualização)."""
    raw = b''.join(b'\x00' + bytes(v for c in row for v in ((*c, 255) if c else (0, 0, 0, 0))) for row in px)
    out = b'\x89PNG\r\n\x1a\n'
    out += _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    out += _chunk(b'IDAT', zlib.compress(raw, 6))
    out += _chunk(b'IEND', b'')
    with open(path, 'wb') as fh:
        fh.write(out)
