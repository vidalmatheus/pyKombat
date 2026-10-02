# Elenco de lutadores.
#
# Cada lutador tem os próprios sprites, todos das folhas do Mortal Kombat II de
# SNES (recortadas por tools/mk2_sprites.py), e os especiais e fatalities do MK2.
#
#   base       -> qual conjunto de sprites usar (res/sprites/<base>/)
#   special    -> especial 1 (projétil)  : ice | spear | fireball | fan | lightning | hat | greenball |
#                                          sai | spark | wave | skull
#   special2   -> especial 2             : slide | teleport | flykick | torpedo | shadowkick |
#                                          bladefury | roll | fanlift | quake | firerise
#   extra      -> especiais 3 e 4 [(tipo, nome)]: um dos tipos acima ou
#                 lowfireball | groundice | skull3 | telekick | bicycle | squarewave | spin |
#                 fanswipe | bladeswipe | splitpunch | gotcha | shadowup
#   fatality   -> anim (animação da própria sheet) | electro | hatsplit | soulsteal | deepfreeze |
#                 firebreath
#   color      -> cor de destaque na interface
#   voice      -> som de vitória (res/Sound/<voice>.ogg); padrão: '<base>Wins',
#                 o locutor do MK2 dizendo "<NOME> WINS"
#   female     -> o locutor diz "FINISH HER" em vez de "FINISH HIM"


class Character:
    def __init__(self, name, base, special, special2, fatality, color, voice=None,
                 specialName='', special2Name='', fatalityName='', extra=(), female=False):
        self.name = name
        self.base = base
        self.special = special
        self.special2 = special2
        self.fatality = fatality
        self.color = color
        self.voice = voice or base.replace('-', '') + 'Wins'
        self.nameSound = 'Name' + base.replace('-', '')   # locutor dizendo o nome (seleção)
        self.female = female
        self.specialName = specialName
        self.special2Name = special2Name
        self.fatalityName = fatalityName
        self.extra = list(extra)   # especiais 3 e 4: [(tipo, nome), ...]

    def paletteKey(self, alt=False):
        return (self.name, alt)


ROSTER = [
    Character('SUB-ZERO', 'Sub-Zero', 'ice', 'slide', 'deepfreeze', (90, 180, 255),
              specialName='ICE BLAST', special2Name='SLIDE',
              fatalityName='DEEP FREEZE',
              extra=[('groundice', 'GROUND FREEZE')]),
    Character('SCORPION', 'Scorpion', 'spear', 'teleport', 'firebreath', (255, 200, 40),
              specialName='SPEAR', special2Name='TELEPORT PUNCH',
              fatalityName='TOASTY'),
    Character('LIU KANG', 'LiuKang', 'fireball', 'flykick', 'anim', (235, 70, 40),
              specialName='FIREBALL', special2Name='FLYING KICK', fatalityName='DRAGON BITE',
              extra=[('lowfireball', 'LOW FIREBALL'), ('bicycle', 'BICYCLE KICK')]),
    Character('KITANA', 'Kitana', 'fan', 'fanlift', 'anim', (80, 130, 255),
              specialName='FAN THROW', special2Name='FAN LIFT', fatalityName='FAN DECAPITATION',
              extra=[('fanswipe', 'FAN SWIPE'), ('squarewave', 'SQUARE WAVE PUNCH')], female=True),
    Character('RAIDEN', 'Raiden', 'lightning', 'torpedo', 'electro', (130, 220, 255),
              specialName='LIGHTNING', special2Name='TORPEDO', fatalityName='ELECTROCUTION',
              extra=[('teleport', 'TELEPORT')]),
    Character('KUNG LAO', 'KungLao', 'hat', 'teleport', 'hatsplit', (70, 170, 200),
              specialName='HAT THROW', special2Name='TELEPORT', fatalityName='HAT SLICE',
              extra=[('spin', 'SPIN')]),
    Character('JOHNNY CAGE', 'JohnnyCage', 'greenball', 'shadowkick', 'anim', (120, 230, 90),
              specialName='GREEN BOLT', special2Name='SHADOW KICK', fatalityName='UPPERCUT DECAPITATION',
              extra=[('shadowup', 'SHADOW UPPERCUT'), ('splitpunch', 'SPLIT PUNCH')]),
    Character('BARAKA', 'Baraka', 'spark', 'bladefury', 'anim', (230, 200, 120),
              specialName='BLADE SPARK', special2Name='BLADE FURY', fatalityName='BLADE DECAPITATION',
              extra=[('bladeswipe', 'DOUBLE BLADE SWIPE')]),
    Character('MILEENA', 'Mileena', 'sai', 'roll', 'anim', (200, 90, 230),
              specialName='SAI THROW', special2Name='ROLL', fatalityName='SAI FRENZY',
              extra=[('telekick', 'TELEPORT KICK')], female=True),
    Character('JAX', 'Jax', 'wave', 'quake', 'anim', (230, 160, 90),
              specialName='ENERGY WAVE', special2Name='GROUND SMASH', fatalityName='ARM RIP',
              extra=[('gotcha', 'GOTCHA GRAB')]),
    Character('SHANG TSUNG', 'ShangTsung', 'skull', 'firerise', 'soulsteal', (255, 110, 40),
              specialName='FLAMING SKULL', special2Name='GROUND FIRE', fatalityName='SOUL STEAL',
              extra=[('skull3', 'TRIPLE SKULL')]),
    Character('REPTILE', 'Reptile', 'acid', 'forceball', 'anim', (90, 220, 70),
              specialName='ACID SPIT', special2Name='FORCE BALL', fatalityName='TONGUE LASH',
              extra=[('slide', 'SLIDE'), ('invisible', 'INVISIBILITY')]),
]


def byName(name):
    for i, c in enumerate(ROSTER):
        if c.name == name:
            return i
    return 0
