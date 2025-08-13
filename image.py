# Importa a biblioteca principal do Pygame, que contém todas as funções
# necessárias para criar jogos, incluindo o carregamento e desenho de imagens.
import pygame

# --- DEFINIÇÃO DA CLASSE set_image ---
# Esta classe foi criada como um "facilitador" para carregar, redimensionar
# e desenhar imagens que ocupam a tela inteira, como menus, telas de game over ou fundos.
class set_image:
    # O método __init__ é o construtor. Ele é executado automaticamente
    # quando um novo objeto desta classe é criado.
    # Exemplo: menu_principal = set_image('caminho/para/imagem.png', (1280, 720))
    def __init__(self, caminho, tamanho_tela):
        """
        Construtor da classe.
        caminho: O caminho (string) para o arquivo da imagem no seu computador.
        tamanho_tela: Uma tupla (largura, altura) para a qual a imagem será redimensionada.
                      Normalmente, são as dimensões da janela do jogo.
        """
        # Carrega a imagem a partir do caminho fornecido. O resultado é uma
        # "Superfície" (Surface) do Pygame, que é como o Pygame representa imagens.
        imagem_original = pygame.image.load(caminho)

        # Redimensiona a imagem original para que ela se ajuste exatamente ao tamanho da tela.
        # Isso garante que a imagem não fique nem pequena demais, nem grande demais.
        # A nova imagem, já redimensionada, é armazenada no atributo 'self.image'.
        self.image = pygame.transform.scale(imagem_original, tamanho_tela)

        # Define a posição padrão onde a imagem será desenhada.
        # A tupla (0, 0) representa o canto superior esquerdo da tela.
        self.pos = (0, 0)

    # Este método é responsável por desenhar a imagem na tela.
    def desenhar(self, tela):
        # O parâmetro 'tela' é a superfície principal da janela do jogo onde tudo é desenhado.
        # O método 'blit' é o comando do Pygame para desenhar uma superfície em outra.
        # Aqui, ele desenha a imagem armazenada (self.image) na tela,
        # na posição definida (self.pos).
        tela.blit(self.image, self.pos)
