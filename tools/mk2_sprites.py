"""Recorta as folhas de sprites do Mortal Kombat II (SNES) em tiras no formato do jogo.

As folhas vêm de https://www.spriters-resource.com/snes/mortalkombat2/ (rip de
ant19831983) e ficam em res/Char/<base>/sheet.png. Cada folha é um mosaico de
sprites soltos sobre um fundo liso; aqui:

  1. cada sprite é achado sozinho (componentes conexos sobre o fundo) — a ordem
     é estável: por linha da folha, da esquerda para a direita, então os
     índices abaixo (FRAMES_MK2) apontam sempre para o mesmo desenho;
  2. as tiras são montadas com os índices escolhidos para cada animação,
     ampliadas com Scale2x e na proporção 8:7 do pixel do SNES, e alinhadas
     pelos pés na última linha e pelo quadril no centro do frame;
  3. cada tira é gravada como PNG paletizado (índice 0 transparente) — a
     segunda cor de um lutador é só uma troca dessa paleta.

Não usa Pillow (só zlib, via tools/pngio.py): as folhas do SNES têm poucas
cores, então não é preciso quantizar.

Uso: python3 tools/mk2_sprites.py   (ou via tools/build_sprites.py)
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pngio  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'res', 'Char')
DST = os.path.join(ROOT, 'res', 'sprites')

CELL_W = 200
CELL_H = 164
# Margem transparente abaixo da linha do chão em todos os frames dos lutadores.
# Nas poses deitadas do SNES uma mão/pé fica mais baixa que o corpo (o chão é
# visto um pouco de cima); alinhar pelo pixel mais baixo deixava o corpo
# "flutuando". Essas poses descem até SINK pixels (ver ground_dip) e a mão
# entra um pouco no chão, como no console. Mesmo valor de assets.FOOT.
SINK = 20
SCALE = 1.36   # altura: Liu Kang parado tem ~99 px no SNES -> ~135 px no jogo
# O pixel do SNES não é quadrado: a TV o mostrava 8/7 mais largo que alto. Sem
# essa correção os lutadores ficam espremidos (mais magros que no console).
SCALE_X = SCALE * 8 / 7

# Tiras: nome -> lista de frames. Cada frame é o índice de um sprite da folha
# (ou uma tupla (índice, dx) para corrigir o alinhamento na mão, em pixels já
# ampliados; ou uma lista [i, j] de pedaços que o detector separou e que
# formam um desenho só). As tiras usam os mesmos nomes e a mesma quantidade de frames das
# do Sub-Zero/Scorpion, para as animações comuns (fighter.COMMON_ANIMS) valerem
# para todos; o que falta no MK2 repete um frame vizinho.
# Opções por tira (dict em ALIGN): 'center' = alinha pelo centro da caixa
# (cambalhotas, quedas), 'left' = pela borda de trás.
FRAMES_MK2 = {
    'Sub-Zero': {
        'dance': [1, 2, 3, 4, 5, 6],
        'walk': list(range(20, 29)),
        'jump': [15, 31, 30],
        'spin': [31] + list(range(32, 39)),
        'crouch': [15, 16, 16],
        'Apunch': [1, 54, 55],
        'Bpunch': [44, 44, 44, 41, 42, 43, 44, 45, 46, 45, 44],
        'Cpunch': [96, 96, 97],
        'Dpunch': [90, 91, 92, 92, 93],
        'Akick': [72, 72, 73, 73, 70, 70, 74],
        'Bkick': [66, 66, 67, 67, 68, 69, 69, 68, 67],
        'Ckick': [16, 16, 98, 103, 104, 104, 104],
        'Dkick': [85, 86, 87, 88, 88, 89],
        'Ekick': [109, 110, 110],
        'Epunch': [111, 112, 112],
        'Ahit': [113, 113, 114],
        'Bhit': [115, 116, 116],
        'Groin': [115, 146],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [117, 118, 119, 119, 120, 121],
        'Ehit': [122, 123, 123],
        'Fhit': [131, 132, 133, 133, 134, 135, 135, 59, 60, 62, 63, 64, 65, 1],
        'Ghit': [56, 57, 58, 134, 135, 135, 59, 61, 63, 65, 1],
        'Ablock': [11, 12, 12],
        'Bblock': [17, 18, 18],
        'dizzy': [148, 149, 150, 151, 152],
        'win': [39, 40, 40],
        'Special': [1, 154, 155, 156, 155, 1],      # rajada de gelo (as duas mãos)
        'Fkick': [187, 188],                       # slide
        'Special3': [170, 171, 172, 174, 175, 178],   # ground freeze (spray no chão no índice 3)
        # deep freeze: forma a bola de gelo (0-7), arremessa (8-10, congela), uppercut (14-18, estilhaça no 16)
        'fatality': [189, 190, 191, 192, 193, 194, 195, 195, 196, 197, 198, 198, 198, 1, 90, 91, 92, 93, 93],
        'fatalityhit': [227, 227, 228, 229, 230, 230, 231, 232, 232, 232],
    },
    'Scorpion': {
        'dance': [1, 2, 3, 4, 5, 6],
        'walk': list(range(16, 25)),
        'jump': [11, 27, 26],
        'spin': [27] + list(range(28, 35)),
        'crouch': [11, 12, 12],
        'Apunch': [1, 50, 51],
        'Bpunch': [44, 44, 44, 40, 41, 42, 37, 38, 39, 38, 44],
        'Cpunch': [92, 92, 93],
        'Dpunch': [86, 86, 87, 88, 88],
        'Akick': [67, 67, 68, 68, 69, 69, 70],
        'Bkick': [63, 63, 64, 64, 64, 65, 65, 66, 63],
        'Ckick': [12, 12, 98, 99, 100, 100, 100],
        'Dkick': [81, 82, 83, 84, 85, 81],
        'Ekick': [27, 108, 108],
        'Epunch': [27, 104, 104],
        'Ahit': [109, 109, 110],
        'Bhit': [111, 112, 112],
        'Groin': [111, 142],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [113, 114, 115, 115, 114, 113],
        'Ehit': [118, 119, 119],
        'Fhit': [127, 128, 129, 130, 130, 131, 131, 54, 55, 56, 58, 59, 61, 62],
        'Ghit': [52, 53, 54, 54, 54, 54, 55, 57, 59, 61, 62],
        'Ablock': [7, 8, 8],
        'Bblock': [13, 14, 14],
        'dizzy': [144, 145, 146, 147, 148],
        'win': [9, 35, 36, 36],
        'Special': [1, 149, 150, 151, 151, 151],    # arremesso do arpão (segura o braço esticado)
        # toasty: vira de frente e tira a máscara (1-3), caveira (4-6), volta de lado (7) e cospe fogo (8+)
        'fatality': [1, 167, 168, 169, 170, 170, 170, 171, 172, 172, 172, 172, 172, 172],
        'fatalityhit': [227, 228, 229, 230, 231, 232, 232, 232, 232, 232],
    },
    'LiuKang': {
        'dance': [1, 2, 3, 4, 5, 6],
        'walk': list(range(17, 26)),
        'jump': [11, 28, 27],                      # agachado, esticado, encolhido
        'spin': [28] + list(range(29, 36)),
        'crouch': [11, 12, 12],
        'Apunch': [1, 42, 43],
        # soco forte: 3-5 e 6-8 (um braço de cada vez, alternando)
        'Bpunch': [44, 44, 44, 51, 52, 53, 44, 45, 46, 45, 44],
        'Cpunch': [89, 89, 90],
        'Dpunch': [85, 86, 87, 88, 88],
        'Akick': [69, 69, 70, 70, 71, 71, 72],
        'Bkick': [65, 65, 66, 66, 67, 68, 68, 67, 66],
        'Ckick': [12, 12, 99, 99, 100, 100, 100],
        'Dkick': [80, 81, 82, 83, 84, 80],
        'Ekick': [28, 98, 98],
        'Epunch': [28, 26, 26],
        'Ahit': [101, 101, 102],
        'Bhit': [107, 109, 110],
        'Groin': [107, 135],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [101, 105, 106, 106, 105, 101],
        'Ehit': [111, 112, 112],
        # queda (0-6, o último deitado) + levantar com rolamento para trás (7-13)
        'Fhit': [121, 122, 123, 124, 125, 126, 126, 57, 58, 59, 60, 61, 62, 64],
        'Ghit': [54, 55, 56, 57, 57, 57, 58, 59, 61, 62, 64],
        'Ablock': [7, 8, 8],
        'Bblock': [13, 14, 14],
        'dizzy': list(range(136, 142)),
        'win': [36, 37, 38, 39],
        'Special': [1, 142, 143, 143, 142, 1],      # bola de fogo (em pé)
        'Special3': [1, 144, 145, 145, 144, 1],     # bola de fogo baixa (ajoelhado)
        'Fkick2': [170, 171, 172, 173, 174, 175],   # bicycle kick (pedalando no ar)
        'Fkick': [96, 97],                         # voadora (flying kick)
        'fatality': list(range(189, 201)),         # vira dragão e morde
        'fatalityhit': [218, 219, 220, 221, 222, 223, 223, 223, 223, 223],
    },
    'Kitana': {
        'dance': [1, 2, 3, 4, 5],
        'walk': list(range(16, 24)),
        'jump': [10, 24, 25],
        'spin': [24] + list(range(27, 34)),
        'crouch': [10, 11, 11],
        'Apunch': [1, 49, 50],
        'Bpunch': [56, 56, 56, 53, 54, 55, 56, 57, 58, 57, 56],
        'Cpunch': [92, 92, 93],
        'Dpunch': [87, 88, 89, 90, 90],
        'Akick': [69, 69, 70, 71, 72, 72, 73],
        'Bkick': [64, 64, 65, 66, 67, 68, 68, 67, 65],
        'Ckick': [10, 10, 99, 99, 100, 100, 100],
        'Dkick': [82, 83, 86, 84, 85, 82],
        'Ekick': [25, 102, 102],
        'Epunch': [25, 26, 26],
        'Ahit': [105, 106, 106],
        'Bhit': [110, 112, 113],
        'Chit': [105, 107, 108, 108, 107, 105],
        'Ehit': [115, 116, 116],
        'Fhit': [125, 126, 127, 128, 129, 129, 129, 136, 136, 137, 137, 138, 138, 139],
        'Ghit': [130, 131, 132, 133, 134, 135, 136, 137, 138, 138, 139],
        'Ablock': [6, 7, 7],
        'Bblock': [12, 13, 13],
        'dizzy': list(range(141, 146)),
        'win': [34, 36, 37, 38],
        'Special': [1, 168, 168, 146, 147, 1],     # arremesso do leque
        'Special2': [1, 40, 41, 41, 40, 1],        # leque que levanta (fan lift)
        'Swipe': [1, 171, 172, 172, 171, 1],        # fan swipe
        'Fkick': [170, 92, 93],                    # square wave punch (substituto: soco no ar)
        'fatality': [1, 168, 169, 170, 171, 172, 173, 173],  # leque corta a cabeça
        'fatalityhit': [202, 203, 204, 205, 206, 207, 208, 209, 210, 210],
    },
    'Raiden': {
        'dance': list(range(1, 9)),
        'walk': list(range(19, 27)),
        'jump': [13, 27, 28],
        'spin': [27] + list(range(30, 37)),
        'crouch': [13, 14, 14],
        'Apunch': [1, 61, 62],
        'Bpunch': [63, 63, 63, 70, 71, 72, 63, 64, 65, 64, 63],
        'Cpunch': [114, 114, 115],
        'Dpunch': [108, 109, 110, 111, 111],
        'Akick': [87, 87, 88, 89, 90, 90, 91],
        'Bkick': [82, 82, 83, 84, 85, 86, 86, 85, 83],
        'Ckick': [13, 13, 118, 118, 119, 119, 119],
        'Dkick': [102, 103, 104, 105, 106, 102],
        'Ekick': [28, 123, 123],
        'Epunch': [28, 29, 29],
        'Ahit': [126, 127, 127],
        'Bhit': [130, 131, 131],
        'Groin': [130, 161],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [126, 128, 129, 129, 128, 126],
        'Ehit': [138, 139, 139],
        'Fhit': [145, 146, 146, 147, 148, 149, 149, 149, 13, 13, 14, 173, 174, 1],
        'Ghit': [150, 151, 152, 153, 154, 155, 13, 14, 173, 174, 1],
        'Ablock': [9, 10, 10],
        'Bblock': [15, 16, 16],
        'dizzy': list(range(161, 168)),
        'win': [37, 38, 39, 40, 41],
        'Special': [1, 173, 174, 168, 169, 174],   # raio
        'Fkick': [170, 171],                       # torpedo
        'fatality': [1, 204, 205],                 # chama o raio do céu
        'fatalityhit': [226, 227, 228, 229, 230, 231, 232, 233, 234, 234],
    },
    'KungLao': {
        'dance': list(range(1, 7)),
        'walk': list(range(16, 25)),
        'jump': [11, 25, 26],
        'spin': [27] + list(range(28, 35)),
        'crouch': [11, 12, 12],
        'Apunch': [1, 42, 43],
        'Bpunch': [44, 44, 44, 47, 48, 49, 44, 45, 46, 45, 44],
        'Cpunch': [91, 91, 92],
        'Dpunch': [86, 87, 88, 89, 89],
        'Akick': [69, 69, 70, 70, 71, 71, 72],
        'Bkick': [65, 65, 66, 66, 67, 68, 68, 67, 66],
        'Ckick': [11, 11, 96, 96, 97, 98, 98],
        'Dkick': [80, 81, 82, 83, 82, 80],
        'Ekick': [27, 101, 101],
        'Epunch': [27, 99, 99],
        'Ahit': [104, 104, 105],
        'Bhit': [108, 109, 110],
        'Groin': [108, 139],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [104, 106, 107, 107, 106, 104],
        'Ehit': [116, 117, 117],
        # queda + levanta pelo mesmo caminho da rasteira (deitado -> agachado -> em pé)
        'Fhit': [126, 127, 128, 129, 130, 131, 131, 122, 123, 123, 124, 124, 125, 1],
        'Ghit': [118, 119, 120, 121, 122, 122, 123, 124, 124, 125, 1],
        'Ablock': [7, 8, 8],
        'Bblock': [13, 14, 14],
        'dizzy': list(range(142, 148)),
        'win': [35, 36, 37, 38, 39, 40],
        'Special': [1, 148, 149, 150, 151, 157],     # arremesso do chapéu
        'Fkick': [161, 162, 163, 164, 165, 166],    # spin (girando)
        'fatality': [148, 149, 150, 151, 152, 153, 154, 155, 156, 157],  # o chapéu corta a vítima
        'fatalityhit': [208, 209, 210, 211, 212, 213, 214, 215, 215, 215],
    },
    'JohnnyCage': {
        'dance': list(range(1, 6)),
        'walk': list(range(16, 24)),
        'jump': [11, 26, 25],
        'spin': [26] + list(range(27, 34)),
        'crouch': [11, 12, 12],
        'Apunch': [44, 45, 46],
        'Bpunch': [44, 44, 44, 47, 48, 49, 44, 55, 57, 55, 44],
        'Cpunch': [90, 90, 91],
        'Dpunch': [85, 86, 87, 88, 88],
        'Akick': [67, 67, 68, 68, 69, 69, 70],
        'Bkick': [63, 63, 64, 64, 65, 66, 66, 65, 64],
        'Ckick': [11, 11, 97, 97, 98, 98, 98],
        'Dkick': [80, 81, 82, 82, 81, 80],
        'Ekick': [26, 100, 100],
        'Epunch': [26, 99, 99],
        'Ahit': [104, 104, 105],
        'Bhit': [108, 109, 110],
        'Groin': [108, 142],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [104, 106, 107, 107, 106, 104],
        'Ehit': [115, 116, 116],
        'Fhit': [126, 127, 128, 129, 130, 131, 131, 138, 139, 140, 141, 141, 142, 1],
        'Ghit': [118, 119, 120, 121, 121, 121, 122, 123, 124, 125, 1],
        'Ablock': [6, 7, 7],
        'Bblock': [13, 14, 14],
        'dizzy': list(range(144, 150)),
        'win': [34, 37, 38, 39, 40],
        'Special': [1, 150, 151, 151, 152, 1],       # bola de fogo verde (baixa)
        'Fkick': [174, 179],                       # shadow kick
        'Upper2': [85, 86, 87, 174],               # shadow uppercut
        'Split': [1, 184, 185, 186, 185, 184],      # split punch
        'fatality': [1, 189, 190, 191, 192, 193, 193],   # uppercut que arranca a cabeça
        'fatalityhit': [240, 241, 242, 243, 244, 245, 246, 247, 248, 248],
    },
    'Baraka': {
        'dance': [0, 1, 2, 3, 2, 1],
        'walk': list(range(4, 13)),
        'jump': [71, 70, 74],
        'spin': [70] + list(range(74, 81)),
        'crouch': [13, 14, 14],
        'Apunch': [0, 63, 64],
        'Bpunch': [55, 55, 55, 55, 56, 57, 58, 59, 60, 59, 55],
        'Cpunch': [25, 25, 26],
        'Dpunch': [14, 22, 22, 23, 23],
        'Akick': [43, 43, 44, 44, 46, 46, 45],
        'Bkick': [39, 39, 40, 40, 42, 41, 41, 42, 40],
        'Ckick': [14, 14, 30, 30, 31, 32, 32],
        'Dkick': [34, 35, 36, 36, 35, 38],
        'Ekick': [83, 84, 84],
        'Epunch': [85, 86, 86],
        'Ahit': [131, 131, 132],
        'Bhit': [129, 129, 130],
        'Groin': [129, 139],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [131, 136, 137, 137, 136, 131],
        'Ehit': [138, 139, 139],
        'Fhit': [119, 120, 121, 122, 123, 123, 123, 124, 125, 126, 127, 128, 128, 0],
        'Ghit': [145, 146, 147, 148, 123, 123, 124, 125, 126, 127, 128],
        'Ablock': [17, 18, 18],
        'Bblock': [15, 16, 16],
        'dizzy': [140, 141, 142, 143, 144],
        'win': [20, 111, 112, 112],
        'Special': [100, 104, 105, 106, 106, 100],   # cruza as lâminas no alto: sai a faísca
        'Fkick': [99, 102, 103, 104],              # blade fury (lâminas girando para a frente)
        'Swipe': [100, 104, 103, 102, 99, 100],     # double blade swipe
        # gira com a lâmina esticada: corta a cabeça no índice 4
        'fatality': [100, 101, 87, 88, 89, 90, 87, 88, 89, 101, 100],
        'fatalityhit': [176, 176, 177, 178, 179, 180, 181, 181, 181, 181],
    },
    'Mileena': {
        'dance': list(range(1, 11)),
        'walk': list(range(21, 29)),
        'jump': [15, 29, 30],
        'spin': [31] + list(range(32, 39)),
        'crouch': [15, 16, 16],
        'Apunch': [1, 58, 59],
        'Bpunch': [49, 49, 49, 49, 50, 51, 52, 53, 54, 53, 49],
        'Cpunch': [96, 96, 97],
        'Dpunch': [91, 92, 93, 94, 94],
        'Akick': [73, 74, 75, 75, 76, 76, 77],
        'Bkick': [68, 69, 70, 70, 71, 72, 72, 71, 70],
        'Ckick': [16, 98, 98, 99, 99, 100, 100],
        'Dkick': [86, 87, 88, 88, 87, 86],
        'Ekick': [31, 108, 108],
        'Epunch': [31, 152, 152],
        'Ahit': [111, 111, 112],
        'Bhit': [109, 110, 110],
        'Chit': [111, 114, 115, 115, 114, 111],
        'Ehit': [119, 120, 120],
        'Fhit': [129, 130, 131, 132, 133, 133, 133, 140, 140, 141, 141, 142, 142, 143],
        'Ghit': [129, 130, 131, 132, 133, 133, 140, 141, 142, 143, 143],
        'Ablock': [11, 12, 12],
        'Bblock': [17, 18, 18],
        'dizzy': [145, 146, 147, 148, 149],
        'win': [39, 40, 42, 44, 46, 48],
        'Special': [1, 150, 151, 152, 152, 1],     # arremesso do sai
        'Fkick': [15] + list(range(32, 39)),       # rolamento pelo chão (bola)
        'Telekick': [29, 31, 32, 107, 108],        # teleport kick: some (0-2), cai chutando (3-4)
        # crava os sais várias vezes e ergue um deles
        'fatality': [174, 175, 176, 175, 174, 175, 176, 175, 174, 177, 178, 179, 179, 179],
        'fatalityhit': [212, 213, 214, 215, 216, 217, 217, 217, 217, 217],
    },
    'ShangTsung': {
        'dance': [1, 2, 3, 4, 5],
        'walk': list(range(16, 25)),
        'jump': [10, 25, 26],
        'spin': [25] + list(range(28, 35)),
        'crouch': [10, 11, 11],
        'Apunch': [1, 39, 40],
        'Bpunch': [36, 36, 36, 45, 46, 47, 36, 37, 37, 36, 36],
        'Cpunch': [78, 78, 79],
        'Dpunch': [73, 74, 75, 76, 76],
        'Akick': [57, 57, 58, 58, 59, 59, 60],
        'Bkick': [53, 53, 54, 54, 55, 56, 56, 55, 54],
        'Ckick': [11, 11, 92, 92, 93, 93, 93],
        'Dkick': [68, 69, 70, 70, 71, 72],
        'Ekick': [25, 90, 90],
        'Epunch': [25, 27, 27],
        'Ahit': [94, 94, 95],
        'Bhit': [99, 102, 103],
        'Groin': [99, 132],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [94, 104, 105, 105, 104, 94],
        'Ehit': [106, 107, 107],
        'Fhit': [117, 118, 119, 120, 121, 122, 122, 111, 110, 113, 114, 114, 115, 116],
        'Ghit': [108, 109, 109, 110, 111, 111, 110, 113, 114, 115, 116],
        'Ablock': [6, 7, 7],
        'Bblock': [12, 13, 13],
        'dizzy': [134, 135, 136, 137, 138],
        'win': [294, 295, 296, 297],
        'Special': [1, 139, 140, 140, 139, 1],      # caveira de fogo
        'Special2': [1, 190, 190, 190, 190, 1],     # abre os braços: o fogo sobe do chão
        # estende a mão para a vítima e puxa a alma (fatalfx desenha a alma)
        'fatality': [206, 207, 208, 209, 210],
        'fatalityhit': [251, 251, 252, 253, 254, 255, 256, 256, 256, 256],
    },
    'Jax': {
        'dance': [1, 2, 3, 4, 5],
        'walk': list(range(15, 24)),
        'jump': [10, 24, 25],
        'spin': [26] + list(range(27, 34)),
        'crouch': [10, 11, 11],
        'Apunch': [1, 47, 48],
        'Bpunch': [40, 40, 40, 41, 42, 42, 43, 44, 45, 44, 40],
        'Cpunch': [91, 91, 92],
        'Dpunch': [86, 87, 88, 89, 90],
        'Akick': [68, 68, 69, 69, 70, 70, 71],
        'Bkick': [64, 64, 65, 66, 66, 67, 67, 66, 65],
        'Ckick': [11, 11, 98, 98, 99, 99, 99],
        'Dkick': [80, 81, 82, 83, 84, 85],
        'Ekick': [102, 103, 103],
        'Epunch': [100, 101, 101],
        'Ahit': [106, 107, 107],
        'Bhit': [108, 109, 109],
        'Groin': [108, 145],   # golpe no saco (split punch do Johnny Cage)
        'Chit': [111, 112, 113, 113, 114, 115],
        'Ehit': [118, 119, 119],
        'Fhit': [120, 121, 122, 122, 123, 124, 124, 139, 140, 140, 141, 142, 143, 143],
        'Ghit': [133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143],
        'Ablock': [6, 7, 7],
        'Bblock': [12, 13, 13],
        'dizzy': [146, 147, 148, 149, 150],
        'win': [34, 35, 36, 37, 38, 39],
        'Special': [155, 156, 157, 158, 159, 160],  # onda de energia (sai no índice 3)
        'Special2': [167, 168, 169, 170, 171, 172], # soco no chão (o punho bate no índice 3)
        'Grab': [151, 152, 153, 154, 153, 154],     # gotcha grab
        # agarra os braços da vítima, puxa e ergue os braços
        'fatality': [174, 175, 176, 177, 178, 179, 180, 181, 182, 183],
        'fatalityhit': [204, 205, 206, 207, 208, 209, 209, 209, 209, 209],
    },
}
ALIGN = {
    'spin': 'center', 'Fhit': 'center', 'Ghit': 'center', 'fatalityhit': 'center',
    ('LiuKang', 'fatality'): 'left',   # o dragão cresce para a frente; a cauda fica no lugar
    ('Mileena', 'Fkick'): 'center',    # a bola do rolamento gira em torno do centro
    ('KungLao', 'Fkick'): 'center',    # o spin gira em torno do centro
    ('Sub-Zero', 'Special3'): 'left',  # o spray de gelo cresce para a frente
}
# efeitos (sem troca de paleta): nome -> (base, frames); âncora = frente do efeito
FX_MK2 = {
    'ice': ('Sub-Zero', [157, 158, 159, [161, 162], [163, 164], [165, 166], 167, 168, 169]),  # 0-2 sai, 3-4 voa, 5-8 estoura
    'freezefx': ('Sub-Zero', [199, 200]),
    'icepuddle': ('Sub-Zero', [176, 179, 180, 181, 182, 183, 184, 185, 186]),   # poça do ground freeze                         # bola de gelo da fatality
    'spearhead': ('Scorpion', [155]),                              # kunai do arpão (a corda é desenhada no código)
    'firebreath': ('Scorpion', [173, 174, 175, 176]),              # fogo saindo da boca (faísca -> labareda)
    'fireburn': ('Scorpion', [177, 178, 179, 180, 181, 183]),      # fogo na vítima (bola -> coluna -> caveira)
    'fireball': ('LiuKang', [146, 147, 150, 151, 152, 153, 154, 155]),   # 0-1 saindo, 2-3 voando, 4-7 explosão
    'fan': ('Kitana', list(range(148, 158))),                          # leque girando
    'fanwind': ('Kitana', [158, 159, 160, 161, 162, 163, 164, 165]),   # vento do fan lift
    'lightning': ('Raiden', [175, 177, 179, 181, 182, 183, 184, 186, 188, 193]),  # 0-2 forma, 3-6 voa, 7-9 estoura
    'raidenbolt': ('Raiden', [206, 207]),                              # raio do céu (fatality)
    'hat': ('KungLao', [158, 159, 160]),                               # chapéu girando (visto de lado)
    'greenball': ('JohnnyCage', [153, 154, 155, 156, 157, 158, 159, 160, 161]),  # 0-2 forma, 3-6 voa, 7-8 estoura
    'spark': ('Baraka', [222, 218, 215, 216, 213, 214, 209, 210, 211, 219, 212]),  # 0-3 sai, 4-5 voa, 6-10 estoura
    'sai': ('Mileena', [153, 155, 154, 156, 163, 164, 165, 166, 167]),  # 0-1 sai, 2-3 voa, 4-8 estoura
    'skull': ('ShangTsung', [141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]),  # 0-3 acende, 4-6 voa, 7-10 estoura
    'firerise': ('ShangTsung', [191, 192, 193, 194, 195, 197]),    # fogo saindo do chão (cresce e apaga)
    'soul': ('ShangTsung', list(range(211, 221))),                 # 0-2 alma sobe, 3-4 voa, 5-9 é absorvida
    'wave': ('Jax', [163, 162, 161, 162, 163]),                    # 0-1 sai, 2 voa, 3-4 estoura
}


def find_sprites(w, h, px, bg, gap=2, minPixels=12):
    """Caixas [x0, y0, x1, y1] dos sprites, em ordem de leitura (linhas da folha)."""
    m = [[c is not None and c != bg for c in row] for row in px]
    seen = [[False] * w for _ in range(h)]
    found = []
    for y in range(h):
        for x in range(w):
            if m[y][x] and not seen[y][x]:
                stack = [(x, y)]
                seen[y][x] = True
                x0 = x1 = x
                y0 = y1 = y
                n = 0
                while stack:
                    cx, cy = stack.pop()
                    n += 1
                    x0, x1 = min(x0, cx), max(x1, cx)
                    y0, y1 = min(y0, cy), max(y1, cy)
                    for yy in range(max(0, cy - gap), min(h, cy + gap + 1)):
                        for xx in range(max(0, cx - gap), min(w, cx + gap + 1)):
                            if m[yy][xx] and not seen[yy][xx]:
                                seen[yy][xx] = True
                                stack.append((xx, yy))
                if n >= minPixels:
                    found.append([x0, y0, x1 + 1, y1 + 1])
    # agrupa em linhas pelo centro vertical
    found.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in found:
        cy = (b[1] + b[3]) / 2
        for r in rows:
            if r[0] - 4 <= cy <= r[1] + 4:
                r[2].append(b)
                r[0], r[1] = min(r[0], b[1]), max(r[1], b[3])
                break
        else:
            rows.append([b[1], b[3], [b]])
    rows.sort(key=lambda r: r[0])
    out = []
    for r in rows:
        out += sorted(r[2], key=lambda b: b[0])
    return out


def scale2x(img):
    """Scale2x (EPX): dobra o sprite suavizando as diagonais, sem criar cores novas
    (a paleta continua a mesma, o que a troca de cores precisa). O transparente
    (None) conta como uma cor, então o contorno também fica suave."""
    h, w = len(img), len(img[0])
    out = [[None] * (2 * w) for _ in range(2 * h)]
    for y in range(h):
        up = img[y - 1] if y > 0 else img[y]
        row = img[y]
        down = img[y + 1] if y + 1 < h else img[y]
        o0, o1 = out[2 * y], out[2 * y + 1]
        for x in range(w):
            p = row[x]
            a = up[x]
            d = down[x]
            c = row[x - 1] if x > 0 else p
            b = row[x + 1] if x + 1 < w else p
            if c == a and c != d and a != b:
                o0[2 * x] = a
            else:
                o0[2 * x] = p
            o0[2 * x + 1] = b if (a == b and a != c and b != d) else p
            o1[2 * x] = c if (d == c and d != b and c != a) else p
            o1[2 * x + 1] = d if (b == d and b != a and d != c) else p
    return out


class Sheet:
    def __init__(self, base):
        self.w, self.h, self.px = pngio.read(os.path.join(SRC, base, 'sheet.png'))
        self.bg = Counter(c for row in self.px[:40] for c in row).most_common(1)[0][0]
        self.boxes = find_sprites(self.w, self.h, self.px, self.bg)
        self._cache = {}
        stand = self.boxes[FRAMES_MK2[base]['dance'][0]]
        self.standH = stand[3] - stand[1]

    def sprite(self, i):
        """(largura, altura, pixels) do sprite i, já ampliado (ver scale2x)."""
        cached = self._cache.get(tuple(i) if isinstance(i, list) else i)
        if cached is not None:
            return cached
        if isinstance(i, list):   # desenho que o detector separou em pedaços: junta as caixas
            bs = [self.boxes[k] for k in i]
            x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
            x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
        else:
            x0, y0, x1, y1 = self.boxes[i]
        bg = self.bg
        raw = [[None if c == bg else c for c in row[x0:x1]] for row in self.px[y0:y1]]
        big = scale2x(raw)                      # 2x suavizado
        bh, bw = len(big), len(big[0])
        sw, sh = int(round((x1 - x0) * SCALE_X)), int(round((y1 - y0) * SCALE))
        # 2x -> tamanho final (fatores < 2): amostra o pixel mais próximo
        out = [[big[min(bh - 1, int(y * 2 / SCALE))][min(bw - 1, int(x * 2 / SCALE_X))]
                for x in range(sw)] for y in range(sh)]
        key = tuple(i) if isinstance(i, list) else i
        self._cache[key] = (sw, sh, out)
        return self._cache[key]

    def hip(self, sw, sh, spx):
        """x do quadril: mediana dos pixels na faixa da cintura (ou o centro da caixa)."""
        H = self.standH * SCALE
        ys = range(max(0, int(sh - 0.56 * H)), max(0, int(sh - 0.44 * H)))
        xs = sorted(x for y in ys for x in range(sw) if spx[y][x])
        return xs[len(xs) // 2] if len(xs) > 20 else sw // 2


def ground_dip(sheet, sw, sh, spx):
    """Quanto descer um frame abaixo do chão. Só para poses deitadas (bem mais
    baixas que o lutador em pé): a base é onde o corpo apoia (a quarta parte das
    colunas mais baixas), não a mão/pé que pende mais."""
    if sh > 0.45 * sheet.standH * SCALE:
        return 0
    gaps = sorted(sh - 1 - max(y for y in range(sh) if spx[y][x] is not None)
                  for x in range(sw) if any(spx[y][x] is not None for y in range(sh)))
    if not gaps:
        return 0
    return min(SINK, gaps[len(gaps) // 4])


def build_strip(sheet, frames, align):
    sprites = []
    for f in frames:
        i, dx = (f if isinstance(f, tuple) else (f, 0))
        sprites.append((sheet.sprite(i), dx))
    # ponto de referência de cada frame (fica no centro do frame da tira)
    refs = []
    for (sw, sh, spx), dx in sprites:
        if align == 'center':
            refs.append(sw // 2 - dx)
        elif align == 'left':
            refs.append(-dx)
        else:
            refs.append(sheet.hip(sw, sh, spx) - dx)
    if align == 'left':  # o primeiro frame (corpo parado) define onde fica a borda de trás
        (sw0, sh0, spx0), _ = sprites[0]
        shift = sheet.hip(sw0, sh0, spx0)
        refs = [r + shift for r in refs]
    cw = max(CELL_W, max(2 * max(r, sw - r) for ((sw, _, _), _), r in zip(sprites, refs)) + 4)
    gy = max(CELL_H, max(sh for ((_, sh, _), _) in sprites))   # linha do chão
    ch = gy + SINK
    cw += cw % 2
    n = len(frames)
    img = [[None] * (cw * n) for _ in range(ch)]
    for k, (((sw, sh, spx), _), r) in enumerate(zip(sprites, refs)):
        ox = k * cw + cw // 2 - r
        oy = gy - sh + ground_dip(sheet, sw, sh, spx)
        for y in range(sh):
            line = img[oy + y]
            for x, c in enumerate(spx[y]):
                if c is not None and 0 <= ox + x - k * cw < cw:
                    line[ox + x] = c
    return cw * n, ch, img


def build_fx(sheet, frames):
    """Efeito (bola de fogo...): frames alinhados pela frente (borda direita) e pelo centro vertical.
    Um frame pode ser uma lista de pedaços (ver FRAMES_MK2)."""
    sprites = [sheet.sprite(i) for i in frames]
    cw = max(sw for sw, _, _ in sprites) + 4
    ch = max(sh for _, sh, _ in sprites) + 4
    img = [[None] * (cw * len(frames)) for _ in range(ch)]
    for k, (sw, sh, spx) in enumerate(sprites):
        ox = (k + 1) * cw - 2 - sw
        oy = (ch - sh) // 2
        for y in range(sh):
            for x, c in enumerate(spx[y]):
                if c is not None:
                    img[oy + y][ox + x] = c
    return cw * len(frames), ch, img


def build_toasty():
    """Toasty! do MK2: rosto do Dan Forden + o texto, sem fundo (res/sprites/toasty.png).
    Vem da folha de menus do MK2 (res/Char/MK2/menu.png)."""
    w, h, px = pngio.read(os.path.join(SRC, 'MK2', 'menu.png'))
    bg = Counter(c for row in px[:5] for c in row[600:]).most_common(1)[0][0]

    def cut(x0, y0, x1, y1, k):
        return [[None if px[y0 + y // k][x0 + x // k] == bg else px[y0 + y // k][x0 + x // k]
                 for x in range((x1 - x0) * k)] for y in range((y1 - y0) * k)]
    face = cut(1053, 628, 1095, 684, 2)     # 84 x 112
    text = cut(841, 770, 898, 784, 2)       # "TOASTY!!" (laranja), 114 x 28
    W = max(len(face[0]), len(text[0]))
    img = [[None] * W for _ in range(len(face) + 4 + len(text))]
    for y, row in enumerate(face):
        for x, c in enumerate(row):
            img[y][(W - len(face[0])) // 2 + x] = c
    for y, row in enumerate(text):
        for x, c in enumerate(row):
            img[len(face) + 4 + y][(W - len(text[0])) // 2 + x] = c
    save_indexed(os.path.join(DST, 'toasty.png'), W, len(img), img)
    print('ok toasty', W, 'x', len(img))


def save_indexed(path, w, h, img):
    colors = Counter(c for row in img for c in row if c is not None)
    pal = [c for c, _ in colors.most_common()]
    if len(pal) > 255:  # junta as cores raras na mais próxima
        keep = pal[:255]
        near = {}
        for c in pal[255:]:
            near[c] = min(keep, key=lambda k: sum((a - b) ** 2 for a, b in zip(k, c)))
        img = [[near.get(c, c) if c is not None else None for c in row] for row in img]
        pal = keep
    index = {c: i + 1 for i, c in enumerate(pal)}
    idx = [[index[c] if c is not None else 0 for c in row] for row in img]
    pngio.write_indexed(path, w, h, idx, [(255, 0, 255)] + pal)


def build(base):
    sheet = Sheet(base)
    os.makedirs(os.path.join(DST, base), exist_ok=True)
    counts = {}
    for name, frames in FRAMES_MK2[base].items():
        w, h, img = build_strip(sheet, frames, ALIGN.get((base, name), ALIGN.get(name, 'waist')))
        save_indexed(os.path.join(DST, base, name + '.png'), w, h, img)
        counts[name] = len(frames)
        print('ok', base, name, len(frames), 'frames de', w // len(frames), 'x', h)
    for name, (fxBase, frames) in FX_MK2.items():
        if fxBase == base:
            w, h, img = build_fx(sheet, frames)
            save_indexed(os.path.join(DST, name + '.png'), w, h, img)
            print('ok fx', name, len(frames), 'frames de', w // len(frames), 'x', h)
    return counts


if __name__ == '__main__':
    for base in (sys.argv[1:] or FRAMES_MK2):
        build(base)
    if not sys.argv[1:]:
        build_toasty()
