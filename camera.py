import pygame

class Camera:
    def __init__(self, b_tela, h_tela, b_mundo, h_mundo):
        self.camera_pos = pygame.Rect(0, 0, b_tela, h_tela)
        self.base = b_mundo
        self.altura = h_mundo

    def apply(self, sprite):
        return sprite.rect.move(self.camera_pos.topleft)
    
    def screen_to_world(self, pos_tela):
        #Converte uma coordenada da tela para uma coordenada do mundo.
        x_tela, y_tela = pos_tela
        x_mundo = x_tela - self.camera_pos.x
        y_mundo = y_tela - self.camera_pos.y
        return (x_mundo, y_mundo)
    
    def apply_rect(self, rect):
        """Aplica o deslocamento da câmera a um retângulo qualquer."""
        return rect.move(self.camera_pos.topleft)
    
    def update(self, alvo):
        x = -alvo.rect.centerx + (self.camera_pos.width / 2)
        y = -alvo.rect.centery + (self.camera_pos.height / 2)

        # Limita o scroll para não sair dos limites do mundo
        x = min(0, x) # Impede de ir além da borda esquerda
        x = max(-(self.base - self.camera_pos.width), x) # Impede de ir além da borda direita
        y = min(0, y) # Impede de ir além da borda de cima
        y = max(-(self.altura - self.camera_pos.height), y) # Impede de ir além da borda de baixo

        self.camera_pos.topleft = (x, y)
