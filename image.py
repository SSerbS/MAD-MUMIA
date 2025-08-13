import pygame

class set_image:
    def __init__(self, caminho, tamanho_tela):
        """
        caminho: caminho para o arquivo da imagem
        tamanho_tela: tupla (largura, altura) da janela para redimensionar a imagem
        """
        imagem_original = pygame.image.load(caminho)
        self.image = pygame.transform.scale(imagem_original, tamanho_tela)
        self.pos = (0, 0)

    def desenhar(self, tela):
        tela.blit(self.image, self.pos)