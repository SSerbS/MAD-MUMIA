# Importa a biblioteca principal do Pygame.
import pygame
# Importa a biblioteca de matemática para cálculos, como ângulos e vetores.
import math
# Importa o gerenciador de áudio de outro arquivo para tocar sons.
from mixer import AudioManager

# --- INICIALIZAÇÃO DO GERENCIADOR DE SOM ---
# Cria uma instância do AudioManager para carregar e controlar os efeitos sonoros.
efeitos_sonoros = AudioManager()
# Carrega os arquivos de som, associando-os a nomes fáceis de usar.
efeitos_sonoros.load_sound('tiro', 'songs/tiroprovisorio.wav')
efeitos_sonoros.load_sound('passos', 'songs/step_grass.wav')

# --- DEFINIÇÃO DA CLASSE JOGADOR ---
# A classe Jogador herda de pygame.sprite.Sprite, o que a torna um objeto de jogo gerenciável.
class Jogador(pygame.sprite.Sprite):
    # O método __init__ é o construtor da classe, executado quando um novo jogador é criado.
    def __init__(self, x, y):
        # Chama o construtor da classe pai (Sprite).
        super().__init__()

        # Variável para controlar o som dos passos.
        self.andando = False

        # --- 1. CARREGAMENTO E ORGANIZAÇÃO DAS ANIMAÇÕES DO JOGADOR ---
        # Cria um dicionário para armazenar todas as listas de animações.
        self.animacoes = {}
        # Define uma escala padrão para redimensionar todas as imagens do jogador.
        escala = (50, 60) 

        # Carrega as imagens para a animação de "andar para a direita".
        self.animacoes['direita_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA P2.png').convert_alpha(), escala)
        ]
        # Carrega as imagens para a animação de "andar para a esquerda".
        self.animacoes['esquerda_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA P2.png').convert_alpha(), escala)
        ]
        # Carrega as imagens para a animação de "andar para cima" (costas).
        self.animacoes['costas_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS P2.png').convert_alpha(), escala)
        ]
        # Carrega as imagens para a animação de "andar para baixo" (frente).
        self.animacoes['frente_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE P2.png').convert_alpha(), escala)
        ]

        # Carrega a imagem única para o estado "parado olhando para a direita".
        self.animacoes['direita_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA.png').convert_alpha(), escala)]
        # Repete para as outras direções quando parado.
        self.animacoes['esquerda_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA.png').convert_alpha(), escala)]
        self.animacoes['costas_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS.png').convert_alpha(), escala)]
        self.animacoes['frente_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE.png').convert_alpha(), escala)]

        # --- 2. CONTROLE DE ESTADO E ANIMAÇÃO ---
        self.direcao_atual = 'frente'  # O jogador começa olhando para frente.
        self.estado_atual = 'parado'   # O jogador começa parado.
        self.frame_atual = 0           # O índice do frame atual na lista de animação.
        # Define a imagem inicial do jogador baseada na direção e estado iniciais.
        self.image = self.animacoes[f'{self.direcao_atual}_{self.estado_atual}'][self.frame_atual]
        # Cria o retângulo de colisão para o jogador, centralizado nas coordenadas iniciais (x, y).
        self.rect = self.image.get_rect(center=(x, y))

        # Configura um timer para controlar a velocidade da troca de frames da animação.
        self.velocidade_animacao = 200 # Tempo em milissegundos entre cada frame.
        self.ultimo_update = pygame.time.get_ticks() # Registra o tempo do último update.

        # --- ATRIBUTOS DE JOGO ---
        self.vida_maxima = 50
        self.vida = self.vida_maxima  # Começa com a vida cheia.
        self.baterias_coletadas = 0

        # Timer para controlar o intervalo entre danos recebidos.
        self.ultimo_dano_tempo = 0
        self.dano_cooldown = 100 # Cooldown de 100ms para receber dano.
        self.ultimo_flash_tempo = 0

        # --- ATRIBUTOS DE MOVIMENTO E AÇÃO ---
        self.velocidade = 5 # Velocidade de movimento do jogador.
        self.pos = pygame.math.Vector2(x, y) # Posição como um vetor para cálculos precisos.
        self.cooldown_tiro = 500 # Intervalo mínimo de 500ms entre tiros.
        self.ultimo_tiro = 0 # Registra o tempo do último tiro.
        self.balas = 0 # Munição inicial.

        # Cria a arma flutuante que segue o jogador.
        self.arma = ArmaFlutuante(self)
        # Coloca a arma em um grupo próprio para gerenciamento.
        self.arma_grupo = pygame.sprite.GroupSingle(self.arma)
        
    def animar(self):
        """Atualiza o frame da animação do jogador baseado no tempo."""
        # Cria a chave para acessar a lista de animação correta no dicionário.
        chave = f'{self.direcao_atual}_{self.estado_atual}'
        lista_frames = self.animacoes[chave]
        
        # Pega o tempo atual.
        agora = pygame.time.get_ticks()
        # Se o tempo decorrido desde o último update for maior que a velocidade da animação...
        if agora - self.ultimo_update > self.velocidade_animacao:
            self.ultimo_update = agora # Reseta o timer.
            # Avança para o próximo frame, voltando ao início se chegar ao fim da lista.
            self.frame_atual = (self.frame_atual + 1) % len(lista_frames)
            # Salva o centro do retângulo atual para evitar que o sprite "pule" ao trocar de frame.
            centro_antigo = self.rect.center
            # Atualiza a imagem do sprite para o novo frame.
            self.image = lista_frames[self.frame_atual].copy()
            # Recria o retângulo com a nova imagem, mas no mesmo centro de antes.
            self.rect = self.image.get_rect(center=centro_antigo)

    def update(self, paredes, camera):
        """Atualiza a lógica do jogador a cada quadro (movimento, estado, animação, colisão)."""
        # Cria um vetor de velocidade zerado.
        self.vel = pygame.math.Vector2(0, 0)
        # Pega o estado de todas as teclas do teclado.
        teclas = pygame.key.get_pressed()

        # Verifica as teclas de movimento e ajusta o vetor de velocidade e a direção.
        if teclas[pygame.K_a]:
            self.vel.x = -self.velocidade
            self.direcao_atual = 'esquerda'
        if teclas[pygame.K_d]:
            self.vel.x = self.velocidade
            self.direcao_atual = 'direita'
        if teclas[pygame.K_w]:
            self.vel.y = -self.velocidade
            self.direcao_atual = 'costas'
        if teclas[pygame.K_s]:
            self.vel.y = self.velocidade
            self.direcao_atual = 'frente'

        # Verifica se o jogador está se movendo ou parado.
        if self.vel.length() == 0:
            self.estado_atual = 'parado'
            self.frame_atual = 0 # Reseta a animação para o primeiro frame de "parado".
            # Se o jogador estava andando e parou, para o som de passos.
            if self.andando:
                efeitos_sonoros.play_control('passos', 'stop')
                self.andando = False
        else:
            self.estado_atual = 'andando'
            # Normaliza o vetor de velocidade para evitar movimento mais rápido na diagonal.
            if self.vel.length() != 0:
                self.vel.normalize_ip()
                self.vel *= self.velocidade
                # Se o jogador começou a andar, toca o som de passos em loop.
                if not self.andando:
                    efeitos_sonoros.play_control('passos', 'play')
                    self.andando = True
        
        # Chama o método de animação para atualizar a imagem do jogador.
        self.animar()
        
        # Aplica o movimento e verifica colisões.
        self.pos.x += self.vel.x
        self.rect.centerx = int(self.pos.x)
        self.Colisao('x', paredes) # Verifica colisão no eixo X.

        self.pos.y += self.vel.y
        self.rect.centery = int(self.pos.y)
        self.Colisao('y', paredes) # Verifica colisão no eixo Y.

        # Atualiza a posição da arma flutuante.
        self.arma.update(self.rect.center, camera)

        agora = pygame.time.get_ticks()
        
        # Se faz menos de 150ms que o flash começou...
        if agora - self.ultimo_flash_tempo < 150:
            # ... aplica o filtro vermelho.
            self.image.fill((100, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
    def atirar(self, pos_mouse_mundo):
        """Cria e retorna um objeto Bala se o jogador puder atirar."""
        agora = pygame.time.get_ticks()
        # Verifica se o jogador tem munição.
        if self.balas > 0:
            # Verifica se o cooldown do tiro já passou.
            if agora - self.ultimo_tiro > self.cooldown_tiro:
                self.ultimo_tiro = agora # Reseta o timer do tiro.
                self.balas -= 1 # Diminui a munição.
                efeitos_sonoros.play_control('tiro', 'play') # Toca o som do tiro.
                
                # --- CÁLCULO PRECISO DA POSIÇÃO DA "BOCA" DA ARMA ---
                # Pega a posição central do jogador no mundo.
                pos_jogador_mundo = self.rect.center
                # Calcula o vetor do jogador até o mouse para obter o ângulo.
                vetor_x = pos_mouse_mundo[0] - pos_jogador_mundo[0]
                vetor_y = pos_mouse_mundo[1] - pos_jogador_mundo[1]
                angulo_radianos = math.atan2(-vetor_y, vetor_x)
                
                # Calcula o deslocamento da ponta da arma usando trigonometria.
                distancia = self.arma.distancia_do_jogador
                boca_offset_x = math.cos(angulo_radianos) * distancia
                boca_offset_y = -math.sin(angulo_radianos) * distancia
                
                # Calcula a posição final exata de onde a bala deve ser criada.
                posicao_boca_x = pos_jogador_mundo[0] + boca_offset_x
                posicao_boca_y = pos_jogador_mundo[1] + boca_offset_y
                
                # Cria a nova bala, passando sua posição inicial e o alvo (mouse).
                nova_bala = Bala(posicao_boca_x, posicao_boca_y, pos_mouse_mundo)
                return nova_bala
                
        # Se não atirou (sem balas ou em cooldown), retorna None.
        return None

    def Colisao(self, direcao, paredes):
        """Verifica e resolve colisões com as paredes."""
        # Detecta todas as paredes com as quais o jogador está colidindo.
        self.colisoes = pygame.sprite.spritecollide(self, paredes.sprites(), False)

        # Itera sobre cada parede colidida para ajustar a posição do jogador.
        for parede in self.colisoes:
            if direcao == 'x': # Se a colisão ocorreu no movimento horizontal...
                if self.vel.x > 0: # Movendo para a direita...
                    self.rect.right = parede.rect.left # Encosta o lado direito do jogador no lado esquerdo da parede.
                if self.vel.x < 0: # Movendo para a esquerda...
                    self.rect.left = parede.rect.right # Encosta o lado esquerdo do jogador no lado direito da parede.
                self.pos.x = self.rect.centerx # Atualiza a posição vetorial precisa.
            if direcao == 'y': # Se a colisão ocorreu no movimento vertical...
                if self.vel.y > 0: # Movendo para baixo...
                    self.rect.bottom = parede.rect.top
                if self.vel.y < 0: # Movendo para cima...
                    self.rect.top = parede.rect.bottom
                self.pos.y = self.rect.centery # Atualiza a posição vetorial precisa.

# --- DEFINIÇÃO DA CLASSE INIMIGO ---
class Inimigo(pygame.sprite.Sprite):
    # Cria um grupo de sprites como uma variável de classe para que todos os inimigos se conheçam.
    inimigos = pygame.sprite.Group()

    def __init__(self, x, y, velocidade, dano, vida):
        super().__init__()

        # --- ANIMAÇÕES DA MÚMIA (idêntico ao sistema do jogador) ---
        self.animacoes = {}
        escala = (60, 70) 
        self.animacoes['direita_andando'] = [pygame.transform.scale(pygame.image.load(f'image/SPRITE MUMIA DIREITA P{i}.png').convert_alpha(), escala) for i in range(1,3)]
        self.animacoes['esquerda_andando'] = [pygame.transform.scale(pygame.image.load(f'image/SPRITE MUMIA ESQUERDA P{i}.png').convert_alpha(), escala) for i in range(1,3)]
        self.animacoes['costas_andando'] = [pygame.transform.scale(pygame.image.load(f'image/SPRITE MUMIA COSTAS P{i}.png').convert_alpha(), escala) for i in range(1,3)]
        self.animacoes['frente_andando'] = [pygame.transform.scale(pygame.image.load(f'image/SPRITE MUMIA FRENTE P{i}.png').convert_alpha(), escala) for i in range(1,3)]
        self.animacoes['direita_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA DIREITA.png').convert_alpha(), escala)]
        self.animacoes['esquerda_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA ESQUERDA.png').convert_alpha(), escala)]
        self.animacoes['costas_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA COSTAS.png').convert_alpha(), escala)]
        self.animacoes['frente_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA FRENTE.png').convert_alpha(), escala)]

        # --- CONTROLE DE ESTADO E ANIMAÇÃO (idêntico ao do jogador) ---
        self.direcao_atual = 'frente'
        self.estado_atual = 'parado'
        self.frame_atual = 0
        self.image = self.animacoes[f'{self.direcao_atual}_{self.estado_atual}'][self.frame_atual]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade_animacao = 200 # ms
        self.ultimo_update = pygame.time.get_ticks()

        # --- ATRIBUTOS DE JOGO E IA ---
        self.velocidade = velocidade
        self.dano = dano
        self.vida = vida
        self.pos = pygame.math.Vector2(x, y)
        self.ultima_posicao_jogador = None # Armazena a última posição conhecida do jogador.
        Inimigo.inimigos.add(self) # Adiciona a si mesmo ao grupo de inimigos da classe.

    def animar(self):
        """Atualiza a animação do inimigo (código idêntico ao do jogador)."""
        chave = f'{self.direcao_atual}_{self.estado_atual}'
        lista_frames = self.animacoes[chave]
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.velocidade_animacao:
            self.ultimo_update = agora
            self.frame_atual = (self.frame_atual + 1) % len(lista_frames)
            centro_antigo = self.rect.center
            self.image = lista_frames[self.frame_atual]
            self.rect = self.image.get_rect(center=centro_antigo)

    def definir_direcao_visual(self):
        """Define a direção da animação (direita, esquerda, etc.) com base no vetor de movimento."""
        if self.direcao.length() == 0:
            return
        # Compara o movimento nos eixos X e Y para decidir a direção principal.
        if abs(self.direcao.x) > abs(self.direcao.y):
            self.direcao_atual = 'direita' if self.direcao.x > 0 else 'esquerda'
        else:
            self.direcao_atual = 'frente' if self.direcao.y > 0 else 'costas'

    def update(self, alvo, alcance_visao, paredes, checar_ultima_posicao_jogador):
        """Atualiza a IA, movimento e animação do inimigo."""
        # Calcula o vetor e a distância até o alvo (jogador).
        self.direcao = pygame.math.Vector2(alvo.pos.x - self.pos.x, alvo.pos.y - self.pos.y)
        self.distancia = self.direcao.magnitude() if self.direcao.magnitude() != 0 else 0

        movendo = False
        # Se o alvo está no alcance e visível, e não está colidindo...
        if self.distancia <= alcance_visao and self.EstaVendo(alvo, paredes) and not alvo.rect.colliderect(self.rect):
            self.ultima_posicao_jogador = pygame.math.Vector2(alvo.pos.x, alvo.pos.y) # Atualiza a última posição vista.
            movendo = True
        # Se perdeu o alvo de vista...
        elif self.EstaVendo(alvo, paredes) == False or self.distancia > alcance_visao:
            # Se a opção está ativa, vai até a última posição conhecida.
            if checar_ultima_posicao_jogador and self.ultima_posicao_jogador is not None:
                self.direcao = self.ultima_posicao_jogador - self.pos
                if self.direcao.magnitude() < self.velocidade:
                    self.ultima_posicao_jogador = None # Chegou ao local, esquece a posição.
                movendo = True

        # Aplica o movimento e atualiza o estado de animação.
        if movendo and self.direcao.length() != 0:
            self.estado_atual = 'andando'
            self.definir_direcao_visual() # Define qual animação usar.
            
            # Normaliza e aplica a velocidade.
            self.direcao.normalize_ip()
            self.direcao *= self.velocidade
            
            # Move e checa colisão, eixo por eixo.
            self.pos.x += self.direcao.x
            self.rect.centerx = int(self.pos.x)
            self.Colisao('x', paredes)
            self.pos.y += self.direcao.y
            self.rect.centery = int(self.pos.y)
            self.Colisao('y', paredes)
        else:
            self.estado_atual = 'parado' # Se não estiver se movendo, fica parado.
            self.frame_atual = 0

        self.animar() # Chama o método de animação.
        
    def EstaVendo(self, alvo, paredes):
        """Verifica se há uma linha de visão livre até o alvo (sem paredes no caminho)."""
        for parede in paredes:
            # `clipline` verifica se uma linha entre dois pontos cruza um retângulo.
            if parede.rect.clipline(self.rect.center, alvo.rect.center):
                return False # Há uma parede no caminho.
        return True # Linha de visão livre.

    def Colisao(self, direcao, paredes):
        """Verifica e resolve colisões com paredes e outros inimigos."""
        # Verifica colisão com paredes.
        self.colisoes = pygame.sprite.spritecollide(self, paredes.sprites(), False)
        # Verifica colisão com outros inimigos.
        self.colisoes_inimigos = pygame.sprite.spritecollide(self, Inimigo.inimigos.sprites(), False)

        # Lógica de colisão com paredes (idêntica à do jogador).
        for parede in self.colisoes:
            if direcao == 'x':
                if self.direcao.x > 0: self.rect.right = parede.rect.left
                elif self.direcao.x < 0: self.rect.left = parede.rect.right
                self.pos.x = self.rect.centerx
            elif direcao == 'y':
                if self.direcao.y > 0: self.rect.bottom = parede.rect.top
                elif self.direcao.y < 0: self.rect.top = parede.rect.bottom
                self.pos.y = self.rect.centery

        # Lógica de colisão com outros inimigos para evitar que fiquem sobrepostos.
        for outro_inimigo in self.colisoes_inimigos:
            if outro_inimigo != self: # Garante que não está checando colisão consigo mesmo.
                if direcao == 'x':
                    if self.direcao.x > 0: self.rect.right = outro_inimigo.rect.left
                    elif self.direcao.x < 0: self.rect.left = outro_inimigo.rect.right
                    self.pos.x = self.rect.centerx
                elif direcao == 'y':
                    if self.direcao.y > 0: self.rect.bottom = outro_inimigo.rect.top
                    elif self.direcao.y < 0: self.rect.top = outro_inimigo.rect.bottom
                    self.pos.y = self.rect.centery
    
    # Este método parece ser uma versão antiga ou alternativa do movimento da IA,
    # pode ser removido se não estiver em uso no loop principal.
    def VerificarUltimaPosicao(self, ultima_posicao, paredes):
        # ... (código de movimento para a última posição) ...
        pass


# --- DEFINIÇÃO DA CLASSE BALA ---
class Bala(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pos_mouse_mundo):
        super().__init__()
        
        # Cria uma imagem circular para a bala.
        raio_bala = 6
        tamanho_surface = raio_bala * 2
        # Cria uma superfície com canal alfa para permitir fundo transparente.
        self.image = pygame.Surface((tamanho_surface, tamanho_surface), pygame.SRCALPHA)
        # Desenha o círculo na superfície.
        pygame.draw.circle(self.image, 'black', (raio_bala, raio_bala), raio_bala)

        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        
        # --- LÓGICA DE DIREÇÃO E MOVIMENTO ---
        self.pos_inicial = pygame.math.Vector2(pos_x, pos_y)
        posicao_mouse_vec = pygame.math.Vector2(pos_mouse_mundo)
        
        # Calcula a direção normalizada (vetor de comprimento 1) da bala.
        try:
            self.direcao = (posicao_mouse_vec - self.pos_inicial).normalize()
        except ValueError: # Caso o mouse esteja exatamente na mesma posição da bala.
            self.direcao = pygame.math.Vector2(0, -1) # Define uma direção padrão para cima.
            
        self.velocidade = 15
        self.spawn_time = pygame.time.get_ticks() # Registra o tempo de criação.
        self.vida_util = 3000 # Tempo em ms que a bala existe antes de se autodestruir.

    def update(self):
        """Move a bala e verifica seu tempo de vida."""
        # Move a bala na direção definida com a velocidade definida.
        self.pos_inicial += self.direcao * self.velocidade
        self.rect.center = self.pos_inicial

        # Se a bala exceder seu tempo de vida, ela é removida do jogo.
        if pygame.time.get_ticks() - self.spawn_time > self.vida_util:
            self.kill()

# --- DEFINIÇÃO DA CLASSE ARMA FLUTUANTE ---
class ArmaFlutuante(pygame.sprite.Sprite):
    def __init__(self, jogador):
        super().__init__()
        self.jogador = jogador 
        self.distancia_do_jogador = 40 # Distância que a arma flutua ao redor do jogador.

        # Carrega e escala a imagem da arma.
        self.imagem_original = pygame.image.load('image/arma.png').convert_alpha()
        self.imagem_original = pygame.transform.scale(self.imagem_original, (75, 75))
        self.image = self.imagem_original.copy() # `image` é a que será rotacionada.
        self.rect = self.image.get_rect(center=self.jogador.rect.center)

    def update(self, pos_jogador_mundo, camera):
        """Atualiza a rotação e a posição da arma para mirar no mouse."""
        # 1. Converte a posição do mouse da tela para as coordenadas do mundo do jogo.
        pos_mouse_tela = pygame.mouse.get_pos()
        pos_mouse_mundo = camera.screen_to_world(pos_mouse_tela)
        pos_jogador = pos_jogador_mundo

        # 2. Calcula o vetor do jogador para o mouse.
        vetor_x = pos_mouse_mundo[0] - pos_jogador[0]
        vetor_y = pos_mouse_mundo[1] - pos_jogador[1]

        # 3. Calcula o ângulo em graus a partir do vetor.
        angulo_radianos = math.atan2(-vetor_y, vetor_x)
        angulo_graus = math.degrees(angulo_radianos)

        # 4. Decide se a imagem da arma deve ser espelhada.
        if -90 <= angulo_graus <= 90: # Se a mira está à direita do jogador...
            imagem_para_rotacionar = self.imagem_original # Usa a imagem normal.
            angulo_final = angulo_graus
        else: # Se a mira está à esquerda...
            # Espelha a imagem horizontalmente.
            imagem_para_rotacionar = pygame.transform.flip(self.imagem_original, True, False)
            # Ajusta o ângulo para compensar o espelhamento.
            angulo_final = angulo_graus + 180

        # 5. Aplica a rotação final na imagem escolhida.
        self.image = pygame.transform.rotate(imagem_para_rotacionar, angulo_final)

        # 6. Calcula a posição da arma ao redor do jogador usando trigonometria.
        deslocamento_x = math.cos(angulo_radianos) * self.distancia_do_jogador
        deslocamento_y = -math.sin(angulo_radianos) * self.distancia_do_jogador
        pos_final_x = pos_jogador[0] + deslocamento_x
        pos_final_y = pos_jogador[1] + deslocamento_y

        # 7. Atualiza o retângulo da arma com a nova imagem rotacionada e a posição final.
        self.rect = self.image.get_rect(center=(pos_final_x, pos_final_y))
