"""Gera res/sprites/ a partir das folhas de sprites do Mortal Kombat II (SNES).

Todos os lutadores vêm das folhas do MK2 de SNES em res/Char/<base>/sheet.png
(spriters-resource.com), recortadas por tools/mk2_sprites.py: cada animação é
uma tira de frames virados para a direita, alinhados pelos pés, em PNG
paletizado (índice 0 transparente). A paleta é o que permite a segunda cor de
um lutador (os dois lados com o mesmo personagem): em tempo de execução só os
índices da paleta são recoloridos, sem tocar pixel a pixel.

Também gera os efeitos (projéteis, raios, fogo, alma...) e o Toasty!.

Uso: python3 tools/build_sprites.py   (só a biblioteca padrão; sem Pillow)
"""
import mk2_sprites

if __name__ == '__main__':
    for base in mk2_sprites.FRAMES_MK2:
        mk2_sprites.build(base)
    mk2_sprites.build_toasty()
