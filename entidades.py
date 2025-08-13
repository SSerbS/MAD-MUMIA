import pygame
import math
#imporatndo efeitos sonoros
from mixer import AudioManager

efeitos_sonoros = AudioManager()
efeitos_sonoros.load_sound('tiro', 'songs/tiroprovisorio.wav')
efeitos_sonoros.load_sound('passos', 'songs/step_grass.wav')
  
class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.andando = False

        # --- 1. CARREGAMENTO E ORGANIZAÇÃO DAS ANIMAÇÕES DO JOGADOR ---
        self.animacoes = {}
        escala = (50, 60) # Defina um tamanho padrão para os sprites do jogador

        # Carrega sprites de ANDAR
        self.animacoes['direita_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA P2.png').convert_alpha(), escala)
        ]
        self.animacoes['esquerda_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA P2.png').convert_alpha(), escala)
        ]
        self.animacoes['costas_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS P2.png').convert_alpha(), escala)
        ]
        self.animacoes['frente_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE P2.png').convert_alpha(), escala)
        ]

        # Carrega sprites PARADO (idle)
        self.animacoes['direita_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM DIREITA.png').convert_alpha(), escala)]
        self.animacoes['esquerda_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM ESQUERDA.png').convert_alpha(), escala)]
        self.animacoes['costas_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM COSTAS.png').convert_alpha(), escala)]
        self.animacoes['frente_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE HOMEM FRENTE.png').convert_alpha(), escala)]

        # --- 2. CONTROLE DE ESTADO E ANIMAÇÃO ---
        self.direcao_atual = 'frente'  # Começa olhando para frente
        self.estado_atual = 'parado'
        self.frame_atual = 0
        self.image = self.animacoes[f'{self.direcao_atual}_{self.estado_atual}'][self.frame_atual]
        self.rect = self.image.get_rect(center=(x, y))

        # Timer da animação
        self.velocidade_animacao = 200 # ms
        self.ultimo_update = pygame.time.get_ticks()


        # --- NOVAS VARIÁVEIS E AJUSTES ---
        self.vida_maxima = 50
        self.vida = self.vida_maxima  # Começa com vida cheia
        self.baterias_coletadas = 0

        # Para o dano contínuo, precisamos de um timer
        self.ultimo_dano_tempo = 0
        self.dano_cooldown = 1000 # 1000ms = 1 segundo

        # --- SUAS VARIÁVEIS ANTIGAS ---
        self.velocidade = 5
        self.pos = pygame.math.Vector2(x, y)
        self.cooldown_tiro = 500
        self.ultimo_tiro = 0
        self.balas = 0 

        self.arma = ArmaFlutuante(self)
        self.arma_grupo = pygame.sprite.GroupSingle(self.arma)
        
    def animar(self):

        chave = f'{self.direcao_atual}_{self.estado_atual}'
        lista_frames = self.animacoes[chave]
        
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.velocidade_animacao:
            self.ultimo_update = agora
            self.frame_atual = (self.frame_atual + 1) % len(lista_frames)
            centro_antigo = self.rect.center
            self.image = lista_frames[self.frame_atual]
            self.rect = self.image.get_rect(center=centro_antigo)

    def update(self, paredes, camera):

        self.vel = pygame.math.Vector2(0, 0)
        teclas = pygame.key.get_pressed()

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

        if self.vel.length() == 0:
            self.estado_atual = 'parado'
            self.frame_atual = 0

            if self.andando:
                efeitos_sonoros.play_control('passos', 'stop')
                self.andando = False

        else:
            self.estado_atual = 'andando'
            if self.vel.length() != 0:
                self.vel.normalize_ip()
                self.vel *= self.velocidade

                if not self.andando:
                    efeitos_sonoros.play_control('passos', 'play')
                    self.andando = True
        
        self.animar()
        
        # O resto do seu código de update (som, colisão) continua aqui...
        # ...
        self.pos.x += self.vel.x
        self.rect.centerx = int(self.pos.x)
        self.Colisao('x', paredes)

        self.pos.y += self.vel.y
        self.rect.centery = int(self.pos.y)
        self.Colisao('y', paredes)

        self.arma.update(self.rect.center, camera)
        
    def atirar(self, pos_mouse_mundo): # O argumento já é a posição de mundo correta
        agora = pygame.time.get_ticks()
        if self.balas > 0:
            if agora - self.ultimo_tiro > self.cooldown_tiro:
                self.ultimo_tiro = agora
                self.balas -= 1
                efeitos_sonoros.play_control('tiro', 'play')
                
                # --- CÁLCULO PRECISO DA POSIÇÃO DA "BOCA" DA ARMA ---

                # 1. Pega a posição de MUNDO do jogador.
                pos_jogador_mundo = self.rect.center

                # 2. Calcula o vetor e o ângulo para a mira (em coordenadas de mundo)
                #    Esta lógica é idêntica à da ArmaFlutuante para garantir sincronia.
                vetor_x = pos_mouse_mundo[0] - pos_jogador_mundo[0]
                vetor_y = pos_mouse_mundo[1] - pos_jogador_mundo[1]
                angulo_radianos = math.atan2(-vetor_y, vetor_x)
                
                # 3. Calcula o deslocamento da ponta da arma em relação ao centro do jogador
                #    Usa a mesma distância que a arma flutua do jogador.
                boca_offset_x = math.cos(angulo_radianos) * self.arma.distancia_do_jogador
                boca_offset_y = -math.sin(angulo_radianos) * self.arma.distancia_do_jogador
                
                # 4. Calcula a posição final da "boca" da arma no mundo
                posicao_boca_x = pos_jogador_mundo[0] + boca_offset_x
                posicao_boca_y = pos_jogador_mundo[1] + boca_offset_y
                
                # 5. Cria a nova bala a partir da posição exata da "boca"
                #    A posição do alvo (pos_mouse_mundo) já vem como argumento.
                nova_bala = Bala(posicao_boca_x, posicao_boca_y, pos_mouse_mundo)
                
                return nova_bala
                
        # Se não atirou (sem balas ou em cooldown), retorna None
        return None

    def Colisao(self, direcao, paredes):

        self.colisoes = pygame.sprite.spritecollide(self, paredes.sprites(), False)

        for parede in self.colisoes:
            if direcao == 'x':
                if self.vel.x > 0: 
                    self.rect.right = parede.rect.left

                if self.vel.x < 0: 
                    self.rect.left = parede.rect.right
                self.pos.x = self.rect.centerx
            if direcao == 'y':
                if self.vel.y > 0: 
                    self.rect.bottom = parede.rect.top

                if self.vel.y < 0: 
                    self.rect.top = parede.rect.bottom
                self.pos.y = self.rect.centery

class Inimigo(pygame.sprite.Sprite):

    # Mantém o grupo de inimigos como uma variável de classe
    inimigos = pygame.sprite.Group()

    def __init__(self, x, y, velocidade, dano, vida):
        super().__init__()

        # --- 1. CARREGAMENTO E ORGANIZAÇÃO DAS ANIMAÇÕES DA MÚMIA ---
        self.animacoes = {}
        escala = (50, 60) # Defina um tamanho padrão para os sprites do inimigo

        # Carrega sprites de ANDAR
        self.animacoes['direita_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA DIREITA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA DIREITA P2.png').convert_alpha(), escala)
        ]
        self.animacoes['esquerda_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA ESQUERDA P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA ESQUERDA P2.png').convert_alpha(), escala)
        ]
        self.animacoes['costas_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA COSTAS P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA COSTAS P2.png').convert_alpha(), escala)
        ]
        self.animacoes['frente_andando'] = [
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA FRENTE P1.png').convert_alpha(), escala),
            pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA FRENTE P2.png').convert_alpha(), escala)
        ]

        # Carrega sprites PARADO (idle)
        self.animacoes['direita_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA DIREITA.png').convert_alpha(), escala)]
        self.animacoes['esquerda_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA ESQUERDA.png').convert_alpha(), escala)]
        self.animacoes['costas_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA COSTAS.png').convert_alpha(), escala)]
        self.animacoes['frente_parado'] = [pygame.transform.scale(pygame.image.load('image/SPRITE MUMIA FRENTE.png').convert_alpha(), escala)]

        # --- 2. CONTROLE DE ESTADO E ANIMAÇÃO ---
        self.direcao_atual = 'frente'
        self.estado_atual = 'parado'
        self.frame_atual = 0
        self.image = self.animacoes[f'{self.direcao_atual}_{self.estado_atual}'][self.frame_atual]
        self.rect = self.image.get_rect(center=(x, y))

        # Timer da animação
        self.velocidade_animacao = 200 # ms
        self.ultimo_update = pygame.time.get_ticks()

        # --- Suas variáveis originais ---
        self.velocidade = velocidade
        self.dano = dano
        self.vida = vida
        self.pos = pygame.math.Vector2(x, y)
        self.ultima_posicao_jogador = None
        Inimigo.inimigos.add(self)

    def animar(self):
        # Este método é idêntico ao do jogador!
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
        # Se não há movimento, não mude a direção visual
        if self.direcao.length() == 0:
            return

        # Compara o movimento horizontal e vertical para decidir a direção principal
        if abs(self.direcao.x) > abs(self.direcao.y):
            if self.direcao.x > 0:
                self.direcao_atual = 'direita'
            else:
                self.direcao_atual = 'esquerda'
        else:
            if self.direcao.y > 0:
                self.direcao_atual = 'frente'
            else:
                self.direcao_atual = 'costas'

    def update(self, alvo, alcance_visao, paredes, checar_ultima_posicao_jogador):
        # A lógica de IA para decidir para onde se mover continua a mesma
        self.direcao = pygame.math.Vector2(alvo.pos.x - self.pos.x, alvo.pos.y - self.pos.y)
        self.distancia = self.direcao.magnitude() if self.direcao.magnitude() != 0 else 0

        movendo = False
        if self.distancia <= alcance_visao and self.EstaVendo(alvo, paredes) and not alvo.rect.colliderect(self.rect):
            self.ultima_posicao_jogador = pygame.math.Vector2(alvo.pos.x, alvo.pos.y)
            movendo = True
        elif self.EstaVendo(alvo, paredes) == False or self.distancia > alcance_visao:
            if checar_ultima_posicao_jogador and self.ultima_posicao_jogador is not None:
                # Lógica para ir até a última posição vista
                # (Esta parte pode precisar ser adaptada da sua lógica original)
                self.direcao = self.ultima_posicao_jogador - self.pos
                if self.direcao.magnitude() < self.velocidade:
                    self.ultima_posicao_jogador = None
                movendo = True

        # Atualiza estado e move o inimigo
        if movendo and self.direcao.length() != 0:
            self.estado_atual = 'andando'
            self.definir_direcao_visual() # Define a direção da animação
            
            self.direcao.normalize_ip()
            self.direcao *= self.velocidade
            
            self.pos.x += self.direcao.x
            self.rect.centerx = int(self.pos.x)
            self.Colisao('x', paredes)

            self.pos.y += self.direcao.y
            self.rect.centery = int(self.pos.y)
            self.Colisao('y', paredes)
        else:
            self.estado_atual = 'parado'
            self.frame_atual = 0

        self.animar() # Chama o método de animação no final do update
        
    def EstaVendo(self, alvo, paredes):
        for parede in paredes:
            if parede.rect.clipline(self.rect.center, alvo.rect.center):
                return False
        return True

    def Colisao(self, direcao, paredes):

        self.colisoes = pygame.sprite.spritecollide(self, paredes.sprites(), False)
        self.colisoes_inimigos = pygame.sprite.spritecollide(self, Inimigo.inimigos.sprites(), False)

        for parede in self.colisoes:

            if direcao == 'x':
                if self.direcao.x > 0:
                    self.rect.right = parede.rect.left

                elif self.direcao.x < 0:
                    self.rect.left = parede.rect.right

                self.pos.x = self.rect.centerx

            elif direcao == 'y':
                if self.direcao.y > 0:
                    self.rect.bottom = parede.rect.top
                elif self.direcao.y < 0:
                    self.rect.top = parede.rect.bottom

                self.pos.y = self.rect.centery

        for outro_inimigo in self.colisoes_inimigos:
            if outro_inimigo != self:
                if direcao == 'x':
                    if self.direcao.x > 0:
                        self.rect.right = outro_inimigo.rect.left

                    elif self.direcao.x < 0:
                        self.rect.left = outro_inimigo.rect.right

                    self.pos.x = self.rect.centerx

                elif direcao == 'y':
                    if self.direcao.y > 0:
                        self.rect.bottom = outro_inimigo.rect.top
                    elif self.direcao.y < 0:
                        self.rect.top = outro_inimigo.rect.bottom

                    self.pos.y = self.rect.centery
                    self.pos.y = self.rect.centery

    def VerificarUltimaPosicao(self, ultima_posicao, paredes):
        if ultima_posicao == None:
            return
        
        self.direcao = pygame.math.Vector2(ultima_posicao.x - self.pos.x, ultima_posicao.y - self.pos.y)
        self.distancia = int(self.direcao.magnitude())

        if self.direcao.length() != 0:
                self.direcao.normalize_ip()
                self.direcao *= self.velocidade
            
        self.pos.x += self.direcao.x
        self.rect.centerx = int(self.pos.x)
        self.Colisao('x', paredes)

        self.pos.y += self.direcao.y
        self.rect.centery = int(self.pos.y)
        self.Colisao('y', paredes)

        if self.pos == ultima_posicao:
            ultima_posicao = None

#logica do tiro
class Bala(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pos_mouse_mundo):
        super().__init__()
        
        # 1. Define o tamanho e o raio da bala
        raio_bala = 6
        tamanho_surface = raio_bala * 2

        # 2. Cria uma superfície quadrada e transparente para desenhar o círculo
        #    pygame.SRCALPHA é fundamental para o fundo ser transparente
        self.image = pygame.Surface((tamanho_surface, tamanho_surface), pygame.SRCALPHA)

        # 3. Desenha o círculo preto no centro da superfície transparente
        pygame.draw.circle(self.image, 'black', (raio_bala, raio_bala), raio_bala)
        # --------------------------------------------------------

        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        
        # Lógica de direção
        self.pos_inicial = pygame.math.Vector2(pos_x, pos_y)
        posicao_mouse_vec = pygame.math.Vector2(pos_mouse_mundo)
        
        try:
            self.direcao = (posicao_mouse_vec - self.pos_inicial).normalize()
        except ValueError:
            self.direcao = pygame.math.Vector2(0, -1)
            
        self.velocidade = 15
        self.spawn_time = pygame.time.get_ticks()
        self.vida_util = 3000

    def update(self):
        self.pos_inicial += self.direcao * self.velocidade
        self.rect.center = self.pos_inicial

        if pygame.time.get_ticks() - self.spawn_time > self.vida_util:
            self.kill()

class ArmaFlutuante(pygame.sprite.Sprite):
    def __init__(self, jogador):
        super().__init__()
        self.jogador = jogador 

        self.distancia_do_jogador = 40 #Distância fixa para a translação

        self.imagem_original = pygame.image.load('image/arma.png').convert_alpha()
        self.imagem_original = pygame.transform.scale(self.imagem_original, (75, 75))
        self.image = self.imagem_original.copy()
        self.rect = self.image.get_rect(center=self.jogador.rect.center)


    # Na classe ArmaFlutuante

    def update(self, pos_jogador_mundo, camera):
        # Etapa 1: Converter coordenadas do mouse para o mundo
        pos_mouse_tela = pygame.mouse.get_pos()
        pos_mouse_mundo = camera.screen_to_world(pos_mouse_tela)
        pos_jogador = pos_jogador_mundo

        # Etapa 2: Calcular o vetor para o mouse
        vetor_x = pos_mouse_mundo[0] - pos_jogador[0]
        vetor_y = pos_mouse_mundo[1] - pos_jogador[1]

        # Etapa 3: Calcular o ângulo original da direção
        # Usamos -vetor_y para alinhar com o sistema de ângulos do Pygame (90° = para cima)
        angulo_radianos = math.atan2(-vetor_y, vetor_x)
        angulo_graus = math.degrees(angulo_radianos)

        # Etapa 4: Decidir se espelha e qual ângulo final usar
        if -90 <= angulo_graus <= 90:
            # A arma aponta para a direita: não precisa espelhar.
            # Usamos a imagem e o ângulo originais.
            imagem_para_rotacionar = self.imagem_original
            angulo_final = angulo_graus
        else:
            # A arma aponta para a esquerda: precisa espelhar e ajustar o ângulo.
            # 1. Usa a imagem espelhada horizontalmente.
            imagem_para_rotacionar = pygame.transform.flip(self.imagem_original, True, False)
            # 2. Ajusta o ângulo para compensar o espelhamento.
            angulo_final = angulo_graus + 180

        # Etapa 5: Aplicar a rotação final
        self.image = pygame.transform.rotate(imagem_para_rotacionar, angulo_final)

        # Etapa 6: Calcular a translação (posição da arma)
        # A posição ainda usa o ângulo original (angulo_radianos) para ser correta.
        deslocamento_x = math.cos(angulo_radianos) * self.distancia_do_jogador
        deslocamento_y = -math.sin(angulo_radianos) * self.distancia_do_jogador
        pos_final_x = pos_jogador[0] + deslocamento_x
        pos_final_y = pos_jogador[1] + deslocamento_y

        # Etapa 7: Atualizar o rect com a posição e o tamanho da imagem rotacionada
        self.rect = self.image.get_rect(center=(pos_final_x, pos_final_y))