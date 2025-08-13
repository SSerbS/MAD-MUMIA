import pygame

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

    def atirar(self):
        # Pega o tempo atual
        agora = pygame.time.get_ticks()
        if(self.balas > 0):
            # Verifica se já passou tempo suficiente desde o último tiro
            if agora - self.ultimo_tiro > self.cooldown_tiro:
                # Se passou, atualiza o tempo do último tiro para o momento atual
                self.ultimo_tiro = agora
                self.balas -= 1
                # Pega a posição do mouse e cria a bala
                pos_mouse = pygame.mouse.get_pos()
                nova_bala = Bala(self.rect.centerx, self.rect.centery, pos_mouse)
                efeitos_sonoros.play_control('tiro', 'play')
                # Retorna a bala criada para que o loop principal possa adicioná-la aos grupos
                return nova_bala
            
        # Se não passou tempo suficiente, não faz nada (retorna None implicitamente)
        return None

    def update(self, paredes):

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