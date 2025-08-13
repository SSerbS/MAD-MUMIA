import pygame

class Item_coletavel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = self.image.get_rect(center = (x, y))

class Balas(Item_coletavel):
    def __init__(self, x, y):
        self.image = pygame.Surface((20,20))
        self.image.fill("green")
        super().__init__(x, y)

class Baterias(Item_coletavel):
    def __init__(self, x, y):
        self.image = pygame.Surface((20,20))
        self.image.fill("gold")
        super().__init__(x, y)

class Coracao(Item_coletavel):
    def __init__(self, x, y):
        self.image = pygame.Surface((20,20))
        self.image.fill("red")
        super().__init__(x, y)
