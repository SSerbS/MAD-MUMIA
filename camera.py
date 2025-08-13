# Importa a biblioteca principal do Pygame.
import pygame

# --- DEFINIÇÃO DA CLASSE CAMERA ---
# Esta classe gerencia a "visão" do jogador em um mundo que é maior que a tela.
# Ela calcula um deslocamento (offset) para que todos os objetos do jogo
# sejam desenhados em relação à posição da câmera, criando a ilusão de que a câmera se move.
class Camera:
    # O método __init__ é o construtor, executado quando um objeto Camera é criado.
    def __init__(self, b_tela, h_tela, b_mundo, h_mundo):
        """
        Construtor da Câmera.
        b_tela, h_tela: Largura (base) e altura da janela do jogo (a tela visível).
        b_mundo, h_mundo: Largura (base) e altura do mapa completo do jogo (o mundo).
        """
        # Cria um retângulo que representa a própria câmera. Suas dimensões são as da tela.
        # A posição (x, y) deste retângulo será o deslocamento aplicado a todos os objetos.
        self.camera_pos = pygame.Rect(0, 0, b_tela, h_tela)
        # Armazena as dimensões do mundo para limitar o movimento da câmera depois.
        self.base = b_mundo
        self.altura = h_mundo

    def apply(self, sprite):
        """
        Aplica o deslocamento da câmera a um sprite.
        Este método é usado na hora de desenhar os sprites na tela.
        Ele pega a posição absoluta do sprite no mundo e calcula sua posição relativa na tela.
        """
        # 'sprite.rect.move()' cria um NOVO retângulo deslocado.
        # O deslocamento é o canto superior esquerdo da câmera (self.camera_pos.topleft).
        # Este novo retângulo é o que deve ser passado para a função de desenho (tela.blit).
        return sprite.rect.move(self.camera_pos.topleft)
    
    def screen_to_world(self, pos_tela):
        """
        Converte uma coordenada da tela (como a do mouse) para uma coordenada do mundo.
        É a operação inversa do método 'apply'.
        """
        x_tela, y_tela = pos_tela
        # Para obter a coordenada no mundo, subtraímos o deslocamento da câmera da coordenada da tela.
        x_mundo = x_tela - self.camera_pos.x
        y_mundo = y_tela - self.camera_pos.y
        return (x_mundo, y_mundo)
    
    def apply_rect(self, rect):
        """
        Aplica o deslocamento da câmera a um retângulo qualquer (não precisa ser de um sprite).
        Útil para desenhar elementos que não são sprites, como a imagem de fundo do mapa.
        """
        return rect.move(self.camera_pos.topleft)
    
    def update(self, alvo):
        """
        Atualiza a posição da câmera para que ela siga um 'alvo' (geralmente o jogador).
        Este método deve ser chamado a cada quadro do loop do jogo.
        """
        # A lógica para centralizar o alvo na tela:
        # O deslocamento 'x' da câmera deve ser o negativo da posição do centro do alvo,
        # somado à metade da largura da tela para trazê-lo do canto para o centro.
        x = -alvo.rect.centerx + (self.camera_pos.width / 2)
        y = -alvo.rect.centery + (self.camera_pos.height / 2)

        # --- LIMITA O MOVIMENTO DA CÂMERA (SCROLL) ---
        # Impede que a câmera mostre áreas vazias fora do mapa.

        # Garante que a câmera não se mova para a direita além da borda esquerda do mundo (posição 0).
        x = min(0, x)
        # Garante que a câmera não se mova para a esquerda além da borda direita do mundo.
        x = max(-(self.base - self.camera_pos.width), x)
        # Garante que a câmera não se mova para baixo além da borda superior do mundo.
        y = min(0, y)
        # Garante que a câmera não se mova para cima além da borda inferior do mundo.
        y = max(-(self.altura - self.camera_pos.height), y)

        # Aplica a nova posição (x, y) calculada e limitada ao retângulo da câmera.
        self.camera_pos.topleft = (x, y)
