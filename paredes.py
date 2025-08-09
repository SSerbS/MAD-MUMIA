import pygame

class Parede(pygame.sprite.Sprite):

    def __init__(self, x, y, largura, altura):
        super().__init__()

        self.image = pygame.Surface([largura, altura])
        self.image.fill((0, 0, 255)) 
        self.rect = self.image.get_rect(topleft=(x, y))