# Elenco de lutadores.
#
# Só existem spritesheets de dois ninjas (Sub-Zero e Scorpion). Os outros oito
# são feitos como o próprio Mortal Kombat fazia: troca de paleta (palette swap)
# sobre um dos dois corpos-base + golpes especiais e fatalities próprios.
#
#   base       -> qual conjunto de sprites usar (res/sprites/<base>/)
#   costume    -> (matiz, mult. saturação, mult. brilho) aplicados à roupa
#   skin       -> idem para a pele (None = mantém)
#   special    -> especial 1 (projétil)  : ice | spear | acid | shadow | soul | bolt | rock | shard | mimic
#   special2   -> especial 2             : slide | teleport
#   fatality   -> anim (animação original da sheet) | melt | bomb | slice | slam | thunder | quake | shatter | random
#   color      -> cor de destaque na interface
#   voice      -> som de vitória (res/Sound/<voice>.ogg)


class Character:
    def __init__(self, name, base, special, special2, fatality, color, costume=None,
                 skin=None, voice='Excellent', ghost=False, specialName='', special2Name='',
                 fatalityName=''):
        self.name = name
        self.base = base
        self.special = special
        self.special2 = special2
        self.fatality = fatality
        self.color = color
        self.costume = costume
        self.skin = skin
        self.voice = voice
        self.ghost = ghost  # desenhado translúcido (Chameleon)
        self.specialName = specialName
        self.special2Name = special2Name
        self.fatalityName = fatalityName

    def paletteKey(self, alt=False):
        return (self.name, alt)


ROSTER = [
    Character('SUB-ZERO', 'Sub-Zero', 'ice', 'slide', 'anim', (90, 180, 255),
              voice='SubZeroWins', specialName='ICE BLAST', special2Name='SLIDE',
              fatalityName='SPINE SPLITTER'),
    Character('SCORPION', 'Scorpion', 'spear', 'teleport', 'anim', (255, 200, 40),
              voice='ScorpionWins', specialName='SPEAR', special2Name='TELEPORT PUNCH',
              fatalityName='SPEAR SPLITTER'),
    Character('REPTILE', 'Sub-Zero', 'acid', 'slide', 'melt', (90, 230, 70),
              costume=(112, 1.0, 0.85), specialName='ACID SPIT', special2Name='SLIDE',
              fatalityName='ACID BATH'),
    Character('SMOKE', 'Scorpion', 'spear', 'teleport', 'bomb', (200, 200, 205),
              costume=(210, 0.08, 0.80), specialName='HARPOON', special2Name='TELEPORT PUNCH',
              fatalityName='SMOKE BOMB'),
    Character('NOOB SAIBOT', 'Sub-Zero', 'shadow', 'teleport', 'slice', (120, 120, 140),
              costume=(230, 0.25, 0.30), skin=(230, 0.15, 0.35), specialName='SHADOW DISC',
              special2Name='SHADOW TELEPORT', fatalityName='SHADOW SLICE'),
    Character('ERMAC', 'Scorpion', 'soul', 'teleport', 'slam', (230, 40, 40),
              costume=(356, 1.10, 0.78), specialName='SOUL BALL', special2Name='TELEPORT PUNCH',
              fatalityName='TELEKINETIC SLAM'),
    Character('RAIN', 'Sub-Zero', 'bolt', 'slide', 'thunder', (190, 110, 255),
              costume=(276, 0.95, 0.92), specialName='LIGHTNING ORB', special2Name='SLIDE',
              fatalityName='THUNDERSTRIKE'),
    Character('TREMOR', 'Scorpion', 'rock', 'slide', 'quake', (190, 130, 70),
              costume=(26, 0.70, 0.58), specialName='ROCK THROW', special2Name='SLIDE',
              fatalityName='EARTHQUAKE'),
    Character('FROST', 'Sub-Zero', 'shard', 'slide', 'shatter', (200, 245, 255),
              costume=(188, 0.30, 1.08), specialName='ICE SHARD', special2Name='SLIDE',
              fatalityName='DEEP FREEZE'),
    Character('CHAMELEON', 'Scorpion', 'mimic', 'teleport', 'random', (230, 120, 230),
              costume=(300, 0.85, 0.95), ghost=True, specialName='MIMIC',
              special2Name='TELEPORT PUNCH', fatalityName='ANY OF THEM'),
]

# fatalities "procedurais" (sorteio do Chameleon)
PROCEDURAL_FATALITIES = ['melt', 'bomb', 'slice', 'slam', 'thunder', 'quake', 'shatter']
FATALITY_TITLES = {
    'melt': 'ACID BATH', 'bomb': 'SMOKE BOMB', 'slice': 'SHADOW SLICE',
    'slam': 'TELEKINETIC SLAM', 'thunder': 'THUNDERSTRIKE', 'quake': 'EARTHQUAKE',
    'shatter': 'DEEP FREEZE',
}
MIMIC_SPECIALS = ['ice', 'acid', 'shadow', 'soul', 'bolt', 'rock', 'shard']


def byName(name):
    for i, c in enumerate(ROSTER):
        if c.name == name:
            return i
    return 0
