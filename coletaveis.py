import pygame

class Item_coletavel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = self.image.get_rect(center = (x, y))

# --- Item de Munição ---
class Balas(Item_coletavel):
    def __init__(self, x, y):
        self.image = pygame.image.load('image/SPRITE MUNIÇÃO.png').convert_alpha()
        
        self.image = pygame.transform.scale(self.image, (25, 25))
        
        super().__init__(x, y)

# --- Item de Bateria ---
class Baterias(Item_coletavel):
    def __init__(self, x, y):
        self.image = pygame.image.load('image/SPRITE BATERIA RADIO.png').convert_alpha()

        self.image = pygame.transform.scale(self.image, (25, 30))

        super().__init__(x, y)

# --- Item de Vida ---
class Coracao(Item_coletavel):
    def __init__(self, x, y):

        self.image = pygame.image.load('image/SPRITE VIDA.png').convert_alpha()

        self.image = pygame.transform.scale(self.image, (30, 30))

        super().__init__(x, y)

