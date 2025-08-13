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
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 255, 0)) 
        self.rect = self.image.get_rect(center=(x, y))

        self.vida = 10
        self.velocidade = 4
        self.pos = pygame.math.Vector2(x, y)

        self.cooldown_tiro = 500  # Intervalo em milissegundos (500ms = meio segundo)
        self.ultimo_tiro = 0      # Armazena o tempo em que o último tiro ocorreu
        self.balas = 2

        # --- ATRIBUTOS PARA INVENCIBILIDADE E DANO ---
        self.invencivel = False
        self.tempo_invencibilidade = 1000 # Duração da invencibilidade em milissegundos (1 segundo)
        self.ultimo_dano = 0 # Tempo em que o último dano foi sofrido

        self.arma = ArmaFlutuante(self) # Cria a instância da arma, passando o próprio jogador
        self.arma_grupo = pygame.sprite.GroupSingle(self.arma)


    def atirar(self, pos_alvo):
        # Pega o tempo atual para o cooldown
        agora = pygame.time.get_ticks()

        if self.balas > 0:
            # Verifica se o cooldown do tiro já passou
            if agora - self.ultimo_tiro > self.cooldown_tiro:
                self.ultimo_tiro = agora
                self.balas -= 1
                
                # --- LÓGICA PARA A "BOCA" DA ARMA ---

                # 1. Pega a posição de mundo do jogador e do alvo (mouse)
                pos_jogador_mundo = self.rect.center
                # pos_alvo já é a posição de mundo do mouse, vinda do loop principal

                # 2. Calcula o ângulo exato para a mira
                vetor_x = pos_alvo[0] - pos_jogador_mundo[0]
                vetor_y = pos_alvo[1] - pos_jogador_mundo[1]
                angulo_radianos = math.atan2(-vetor_y, vetor_x)

                # 3. Calcula o deslocamento da ponta da arma em relação ao centro do jogador
                #    Usa a mesma distância que a arma flutua do jogador.
                deslocamento_x = math.cos(angulo_radianos) * self.arma.distancia_do_jogador
                deslocamento_y = -math.sin(angulo_radianos) * self.arma.distancia_do_jogador

                # 4. Calcula a posição final da "boca" da arma no mundo
                posicao_boca_x = pos_jogador_mundo[0] + deslocamento_x
                posicao_boca_y = pos_jogador_mundo[1] + deslocamento_y
                
                # 5. Cria a nova bala a partir da posição calculada
                nova_bala = Bala(posicao_boca_x, posicao_boca_y, pos_alvo)
                
                efeitos_sonoros.play_control('tiro', 'play')
                return nova_bala
                
        # Se não atirou (sem balas ou em cooldown), retorna None
        return None

    def update(self, paredes, camera):

        self.vel = pygame.math.Vector2(0, 0)

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_a]:
            self.vel.x = -self.velocidade
        if teclas[pygame.K_d]:
            self.vel.x = self.velocidade
        if teclas[pygame.K_w]:
            self.vel.y = -self.velocidade
        if teclas[pygame.K_s]:
            self.vel.y = self.velocidade


        if self.vel.length() != 0: 
            self.vel.normalize_ip()
            self.vel *= self.velocidade

            if not hasattr(self, 'passo_channel') or not self.passo_channel.get_busy():
                self.passo_channel = efeitos_sonoros.sounds['passos'].play()
        else:
    # Opcional: parar o som se parar de andar
            if hasattr(self, 'passo_channel') and self.passo_channel.get_busy():
                self.passo_channel.stop()


        self.pos.x += self.vel.x
        self.rect.centerx = int(self.pos.x)
        self.Colisao('x', paredes)


        self.pos.y += self.vel.y
        self.rect.centery = int(self.pos.y)
        self.Colisao('y', paredes)

        self.arma.update(self.rect.center, camera)


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

    inimigos = pygame.sprite.Group()

    def __init__(self, x, y, velocidade, dano, vida):
        super().__init__()

        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect(center=(x, y))

        self.velocidade = velocidade
        self.dano = dano
        self.vida = vida
        self.pos = pygame.math.Vector2(x, y)

        
        self.ultima_posicao_jogador = None
        Inimigo.inimigos.add(self)


    def update(self, alvo, alcance_visao, paredes, checar_ultima_posicao_jogador):

        self.direcao = pygame.math.Vector2(alvo.pos.x - self.pos.x, alvo.pos.y - self.pos.y)

        self.distancia = int(self.direcao.magnitude())
        #distancia = int((dx**2 + dy**2)**0.5)

        if self.distancia <= alcance_visao and self.EstaVendo(alvo, paredes) and alvo.rect.colliderect(self.rect) == False:

            self.ultima_posicao_jogador = pygame.math.Vector2(alvo.pos.x, alvo.pos.y)
            if self.direcao.length() != 0:
                self.direcao.normalize_ip()
                self.direcao *= self.velocidade

            self.pos.x += self.direcao.x
            self.rect.centerx = int(self.pos.x)
            self.Colisao('x', paredes)

            self.pos.y += self.direcao.y
            self.rect.centery = int(self.pos.y)
            self.Colisao('y', paredes)

        elif self.EstaVendo(alvo, paredes) == False or self.distancia > alcance_visao:
            if checar_ultima_posicao_jogador:
                self.VerificarUltimaPosicao(self.ultima_posicao_jogador, paredes)


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
    def __init__(self, pos_x, pos_y, pos_mouse):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        
        # --- A MÁGICA ACONTECE AQUI ---
        # 1. Pega a posição do mouse e a posição inicial da bala
        self.pos_inicial = pygame.math.Vector2(pos_x, pos_y)
        posicao_mouse_vec = pygame.math.Vector2(pos_mouse)
        
        # 2. Calcula o vetor de direção (mouse - jogador) e o normaliza
        try:
            self.direcao = (posicao_mouse_vec - self.pos_inicial).normalize()
        except ValueError:
            # Caso o vetor seja (0,0), o que acontece se o mouse estiver exatamente
            # no mesmo lugar do jogador. A normalização daria erro de divisão por zero.
            self.direcao = pygame.math.Vector2(0, -1) # Atira para cima por padrão
            
        # 3. Define a velocidade da bala
        self.velocidade = 10

    def update(self, tela):
        # Move a bala na direção calculada
        self.pos_inicial += self.direcao * self.velocidade
        self.rect.center = self.pos_inicial

        # Remove a bala se ela sair da tela para não consumir memória
        if not tela.get_rect().colliderect(self.rect):
            self.kill()
    
# Não se esqueça de ter 'import math' no início do seu arquivo!

# Não se esqueça de ter 'import math' e 'import pygame' no início do seu arquivo

class ArmaFlutuante(pygame.sprite.Sprite):
    def __init__(self, jogador):
        super().__init__()
        
        self.jogador = jogador # Referência ao jogador que a arma seguirá

        # --- PARÂMETROS DE CUSTOMIZAÇÃO ---
        # Define a que distância do centro do jogador a arma deve ficar
        self.distancia_do_jogador = 40  # << NOVO! Distância fixa para a translação

        # --- LÓGICA DA IMAGEM ---
        try:
            # É IMPORTANTE que a imagem da sua arma aponte para a DIREITA por padrão.
            # A matemática dos ângulos em pygame assume 0 graus para a direita.
            self.imagem_original = pygame.image.load('image/arma.png').convert_alpha()
            self.imagem_original = pygame.transform.scale(self.imagem_original, (75, 75))
        except pygame.error:
            print("Erro: Imagem 'arma.png' não encontrada. Criando um substituto.")
            self.imagem_original = pygame.Surface((50, 20), pygame.SRCALPHA)
            # Desenhando uma arma substituta que aponta para a direita ->
            pygame.draw.rect(self.imagem_original, (200, 200, 200), (0, 5, 40, 10)) # Corpo da arma
            pygame.draw.rect(self.imagem_original, (150, 150, 150), (40, 3, 10, 14)) # Ponta da arma

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