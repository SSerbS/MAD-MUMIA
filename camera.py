import pygame

class Camera:
    def __init__(self, b_tela, h_tela, b_mundo, h_mundo):
        self.camera_pos = pygame.Rect(0, 0, b_tela, h_tela)
        self.base = b_mundo
        self.altura = h_mundo

    def apply(self, sprite):
        return sprite.rect.move(self.camera_pos.topleft)
    
    def update(self, alvo):
        x = -alvo.rect.centerx + (self.camera_pos.width / 2)
        y = -alvo.rect.centery + (self.camera_pos.height / 2)

        x = min(0, x)
        x = max(-(self.base - self.camera_pos.width), x)
        y = min(0, y)
        y = max(-(self.altura - self.camera_pos.height), y)

        self.camera_pos.topleft = (x, y)

        