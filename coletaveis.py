import pygame

class Item_coletavel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # A classe base usa a 'self.image' definida na classe filha para criar o rect.
        # Isso funciona perfeitamente!
        self.rect = self.image.get_rect(center = (x, y))

# --- Item de Munição ---
class Balas(Item_coletavel):
    def __init__(self, x, y):
        # Define a imagem específica para este item
        self.image = pygame.image.load('image/SPRITE MUNIÇÃO.png').convert_alpha()
        
        # Opcional: ajuste a escala se necessário
        self.image = pygame.transform.scale(self.image, (25, 25))
        
        # Chama o __init__ da classe pai para criar o rect a partir da imagem
        super().__init__(x, y)

# --- Item de Bateria ---
class Baterias(Item_coletavel):
    def __init__(self, x, y):
        # Define a imagem específica para este item
        self.image = pygame.image.load('image/SPRITE BATERIA RADIO.png').convert_alpha()

        # Opcional: ajuste a escala se necessário
        self.image = pygame.transform.scale(self.image, (25, 30))

        # Chama o __init__ da classe pai para criar o rect a partir da imagem
        super().__init__(x, y)

# --- Item de Vida ---
class Coracao(Item_coletavel):
    def __init__(self, x, y):
        # Define a imagem específica para este item
        self.image = pygame.image.load('image/SPRITE VIDA.png').convert_alpha()

        # Opcional: ajuste a escala se necessário
        self.image = pygame.transform.scale(self.image, (30, 30))

        # Chama o __init__ da classe pai para criar o rect a partir da imagem
        super().__init__(x, y)

