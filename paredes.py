import pygame

class Parede(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        # Cria uma superfície completamente transparente do tamanho certo
        self.image = pygame.Surface([largura, altura], pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
