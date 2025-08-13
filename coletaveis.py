# Importa a biblioteca principal do Pygame para ter acesso às suas funcionalidades.
import pygame

# --- CLASSE BASE PARA TODOS OS ITENS COLETÁVEIS ---
# Esta classe serve como um "molde" para todos os itens que podem ser coletados no jogo.
# Ela herda de pygame.sprite.Sprite, o que a torna um objeto de jogo padrão do Pygame,
# permitindo que seja facilmente adicionada a grupos de sprites para gerenciamento e desenho.
class Item_coletavel(pygame.sprite.Sprite):
    # O método __init__ é o construtor da classe, executado quando um novo item é criado.
    def __init__(self, x, y):
        # Chama o construtor da classe pai (pygame.sprite.Sprite). É uma etapa necessária.
        super().__init__()
        
        # Esta é a parte principal da classe base:
        # Ela assume que uma 'self.image' já foi definida pela classe filha (como Balas, Baterias, etc.).
        # A partir dessa imagem, ela cria o 'self.rect', que é o retângulo usado para
        # posicionamento e detecção de colisão do item.
        # O item é posicionado com seu centro nas coordenadas (x, y) fornecidas.
        self.rect = self.image.get_rect(center = (x, y))

# --- ITEM DE MUNIÇÃO (BALAS) ---
# A classe 'Balas' define o item coletável de munição.
# Ela herda tudo da classe 'Item_coletavel'.
class Balas(Item_coletavel):
    def __init__(self, x, y):
        # 1. Define a imagem específica para este item.
        #    'pygame.image.load' carrega o arquivo de imagem.
        #    '.convert_alpha()' otimiza a imagem para desenho e lida corretamente com transparências.
        self.image = pygame.image.load('image/SPRITE MUNIÇÃO.png').convert_alpha()
        
        # 2. (Opcional) Ajusta a escala da imagem para o tamanho desejado (25x25 pixels).
        self.image = pygame.transform.scale(self.image, (25, 25))
        
        # 3. Chama o construtor da classe pai ('Item_coletavel').
        #    Neste ponto, a 'self.image' já existe, então o construtor pai
        #    pode usá-la para criar o 'self.rect' na posição correta.
        super().__init__(x, y)

# --- ITEM DE BATERIA ---
# A classe 'Baterias' define o item coletável de bateria para o rádio.
# Ela também herda da classe 'Item_coletavel'.
class Baterias(Item_coletavel):
    def __init__(self, x, y):
        # 1. Define a imagem específica para a bateria.
        self.image = pygame.image.load('image/SPRITE BATERIA RADIO.png').convert_alpha()

        # 2. (Opcional) Ajusta a escala da imagem para o tamanho desejado (25x30 pixels).
        self.image = pygame.transform.scale(self.image, (25, 30))

        # 3. Chama o construtor da classe pai para finalizar a criação do objeto.
        super().__init__(x, y)

# --- ITEM DE VIDA (CORAÇÃO) ---
# A classe 'Coracao' define o item coletável que recupera a vida do jogador.
# Herda da classe 'Item_coletavel'.
class Coracao(Item_coletavel):
    def __init__(self, x, y):
        # 1. Define a imagem específica para o coração.
        self.image = pygame.image.load('image/SPRITE VIDA.png').convert_alpha()

        # 2. (Opcional) Ajusta a escala da imagem para o tamanho desejado (30x30 pixels).
        self.image = pygame.transform.scale(self.image, (30, 30))

        # 3. Chama o construtor da classe pai, que usará esta imagem para criar o 'rect'.
        super().__init__(x, y)
