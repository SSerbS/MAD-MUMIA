import pygame
import random

from entidades import *
from paredes import *
from coletaveis import *
from camera import *
from mixer import AudioManager
from image import *

#criando a base
pygame.init()
pygame.mixer.init()

largura_tela = 1280
altura_tela = 720
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Sokoban Simples")
clock = pygame.time.Clock()
estado_jogo = "MENU"

todos_os_sprites = pygame.sprite.Group()
balas = pygame.sprite.Group()
paredes = pygame.sprite.Group()
inimigos = pygame.sprite.Group()

todos_coletaveis = pygame.sprite.Group()

jogador = Jogador(150, 150)

#configurando sons
sons = AudioManager()
volume_musica = 0.8
volume_sound = 0.8

sons.load_music('musica menu', 'songs/musicas/musica_menu.ogg')
sons.load_music('musica play', 'songs/musicas/musica_acao.ogg')
sons.load_music('game over', 'songs/musicas/game_overpaezao.mp3')
sons.load_music('zerou game', 'songs/musicas/musica_zerou_game.mp3')
sons.load_sound('coin', 'songs/smw_coin.wav')
sons.load_sound('321', 'songs/01._3_2_1.wav')
sons.load_sound('recuperando vida', 'songs/recuperando_vida.wav')
sons.load_sound('suporte aerio', 'songs/pedindo_apoio_aério.wav')
sons.load_sound('iniciando', 'songs/iniciando_game.wav')
sons.play_music('musica menu')
sons.set_music_volume(1)


# Layout do nível
layout = [
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "P                       E       P",
    "P                               P",
    "P    E             E          E P",
    "P      J                        P",
    "P          E                    P",
    "P                         E     P",
    "P E                  E          P",
    "P           E                   P",
    "P                 E             P",
    "P    E                        E P",
    "P                               P",
    "P          E           E        P",
    "P  E                            P",
    "P                               P",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

largura_mundo = len(layout[0])*100
altura_mundo = len(layout)*100
the_camera = Camera(largura_tela, altura_tela, largura_mundo, altura_mundo)

for id_linha, linha in enumerate(layout):
    for id_coluna, char in enumerate(linha):
        x = id_coluna * 100
        y = id_linha * 100
        if char == 'P':
            p = Parede(x, y, 100, 100)
            paredes.add(p)

        if char == 'J':
            jogador.pos = pygame.math.Vector2(x, y)
            jogador.rect.topleft = (x, y)

        if char == 'E':
            # A velocidade é o 3º argumento. Aumentamos de 1 para 3.
            novo_inimigo = Inimigo(x, y, 2, 1, 10) 
            inimigos.add(novo_inimigo)
            todos_os_sprites.add(novo_inimigo) # Não se esqueça de adicioná-lo ao grupo de desenho

# --- NOVO BLOCO: LÓGICA DE SPAWN ALEATÓRIO ---
TILE_SIZE = 100

#lista de todos os locais válidos para spawn (onde não for parede)
spawn_points = []
for id_linha, linha in enumerate(layout):
    for id_coluna, char in enumerate(linha):
        if char == ' ': # ' ' é um espaço vazio, perfeito para spawn
            x = id_coluna * TILE_SIZE
            y = id_linha * TILE_SIZE
            # Adicionamos um pequeno deslocamento para centralizar o item no tile
            spawn_points.append((x + TILE_SIZE / 2, y + TILE_SIZE / 2))

# n_itens
num_coracoes = 5
num_balas = 5
num_baterias = 10
total_itens = num_coracoes + num_balas + num_baterias


pontos_disponiveis = min(total_itens, len(spawn_points))
posicoes_escolhidas = random.sample(spawn_points, pontos_disponiveis)


for i in range(num_coracoes):
    if not posicoes_escolhidas: break
    item = Coracao(*posicoes_escolhidas.pop())
    todos_coletaveis.add(item)
    todos_os_sprites.add(item)

for i in range(num_balas):
    if not posicoes_escolhidas: break
    item = Balas(*posicoes_escolhidas.pop())
    todos_coletaveis.add(item)
    todos_os_sprites.add(item)
    
for i in range(num_baterias):
    if not posicoes_escolhidas: break
    item = Baterias(*posicoes_escolhidas.pop())
    todos_coletaveis.add(item)
    todos_os_sprites.add(item)


todos_os_sprites.add(jogador)


score = 0
fonte_score = pygame.font.Font(None, 50)
fonte_municao = pygame.font.Font(None, 40)

#setando imagem do menu
initial = True

#setando background
background_img = pygame.image.load('image/MAPA PRONTO.png').convert()
background_img = pygame.transform.scale(background_img, (largura_mundo, altura_mundo))
background_rect = background_img.get_rect() # Cria um rect para o fundo, na posição (0,0)

#configuracoes pra transicao da música
fade_duration = 2000
fade_started = False
rodando = True

#setando imagens
menu = set_image('image/imagem menu.jpeg', (largura_tela, altura_tela))
game_over = set_image('image/TELA DERROTA.png', (largura_tela, altura_tela))
vitoria = set_image('image/TELA VITÓRIA.png', (largura_tela, altura_tela))
background = set_image('image/MAPA PRONTO.png', (largura_tela, altura_tela))


def desenhar_hud(tela, jogador, fonte):
    # Fundo do HUD
    fundo = pygame.Surface((220, 110), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, 150))
    tela.blit(fundo, (5, 5))

    cor_texto = (255, 255, 255)
    verde_barra = (34, 177, 76)

    # --- VIDA ---
    pygame.draw.rect(tela, 'red', (10, 10, 200, 25))
    vida_atual_largura = (jogador.vida / jogador.vida_maxima) * 200
    pygame.draw.rect(tela, verde_barra, (10, 10, vida_atual_largura, 25))
    texto_vida = fonte.render(f"{jogador.vida}/{jogador.vida_maxima}", True, cor_texto)
    tela.blit(texto_vida, (15, 14))

    # --- BATERIAS ---
    texto_baterias = fonte.render(f"Baterias: {jogador.baterias_coletadas} / 10", True, cor_texto)
    tela.blit(texto_baterias, (10, 45))

    # --- MUNIÇÃO ---
    texto_balas = fonte.render(f"Munição: {jogador.balas}", True, cor_texto)
    tela.blit(texto_balas, (10, 80))
    
def reiniciar_jogo():
    """Reseta o estado do jogo para seus valores iniciais."""
    print("--- REINICIANDO O JOGO ---")

    # Limpa todos os grupos de sprites dinâmicos
    todos_os_sprites.empty()
    inimigos.empty()
    todos_coletaveis.empty()
    balas.empty()

    # Reseta o estado do jogador para os valores iniciais
    jogador.vida = jogador.vida_maxima
    jogador.baterias_coletadas = 0
    jogador.balas = 0

    #Reposiciona o jogador e os inimigos baseados no layout original
    for id_linha, linha in enumerate(layout):
        for id_coluna, char in enumerate(linha):
            x = id_coluna * TILE_SIZE
            y = id_linha * TILE_SIZE
            if char == 'J':
                jogador.pos = pygame.math.Vector2(x, y)
                jogador.rect.topleft = (x, y)
            if char == 'E':
                # Precisamos recriar os inimigos para garantir que eles "revivam"
                inimigo_novo = Inimigo(x, y, 2, 1, 10)
                inimigos.add(inimigo_novo)

    # Gera novamente os coletáveis em posições aleatórias
    spawn_points.clear()
    for id_linha, linha in enumerate(layout):
        for id_coluna, char in enumerate(linha):
            if char == ' ':
                x = id_coluna * TILE_SIZE
                y = id_linha * TILE_SIZE
                spawn_points.append((x + TILE_SIZE / 2, y + TILE_SIZE / 2))
    
    posicoes_escolhidas = random.sample(spawn_points, min(total_itens, len(spawn_points)))

    for i in range(num_coracoes):
        if not posicoes_escolhidas: break
        item = Coracao(*posicoes_escolhidas.pop())
        todos_coletaveis.add(item)

    for i in range(num_balas):
        if not posicoes_escolhidas: break
        item = Balas(*posicoes_escolhidas.pop())
        todos_coletaveis.add(item)
        
    for i in range(num_baterias):
        if not posicoes_escolhidas: break
        item = Baterias(*posicoes_escolhidas.pop())
        todos_coletaveis.add(item)

    #Readiciona TODOS os sprites ao grupo principal de desenho
    todos_os_sprites.add(jogador)
    todos_os_sprites.add(inimigos) # Adiciona o grupo de inimigos
    todos_os_sprites.add(todos_coletaveis) # Adiciona o grupo de coletáveis
    

font = pygame.font.SysFont('Press Start 2P', 30, True, True)

rodando = True
while rodando:
    # --- 1. LOOP DE EVENTOS GERAL ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                rodando = False

            # Se estamos no MENU e aperta ENTER, começa o jogo
            if estado_jogo == "MENU" and event.key == pygame.K_RETURN:
                sons.play_control('321', 'play')
                sons.play_control('iniciando', 'play')

                estado_jogo = "JOGANDO"
                pygame.mixer.music.fadeout(fade_duration)
                fade_start_time = pygame.time.get_ticks()
                fade_started = False

            # Se estamos em GAME OVER ou VITORIA e aperta ENTER, volta para o menu
            if (estado_jogo == "GAME_OVER" or estado_jogo == "VITORIA") and event.key == pygame.K_RETURN:
                reiniciar_jogo()
                
                estado_jogo = "MENU"
                sons.play_music('musica menu')

            #controle de volume
            # em resposta a um evento teclado:
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                volume_musica += 0.1 if volume_musica < 1 else 0
                sons.set_music_volume(volume_musica)

            if event.key == pygame.K_DOWN :
                volume_musica -= 0.1 if volume_musica >= 0.1 else 0
                sons.set_music_volume(volume_musica)

            if event.key == pygame.K_LEFT:  # exemplo para efeitos sonoros
                volume_sound -= 0.1 if volume_sound >= 0.1 else 0
                sons.set_sound_volume(volume_sound)

            if event.key == pygame.K_RIGHT:
                volume_sound += 0.1 if volume_sound < 1 else 0
                sons.set_sound_volume(volume_sound)

        
        # Evento de atirar com o mouse, que só funciona quando estamos jogando
        if estado_jogo == "JOGANDO" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos_mouse_tela = pygame.mouse.get_pos()
                pos_mouse_mundo = (pos_mouse_tela[0] - the_camera.camera_pos.x, 
                                   pos_mouse_tela[1] - the_camera.camera_pos.y)

                bala = jogador.atirar(pos_mouse_mundo)
                if bala:
                    todos_os_sprites.add(bala)
                    balas.add(bala)

    # ---  LÓGICA E DESENHO DE CADA ESTADO ---
    if estado_jogo == "MENU":
        menu.desenhar(tela)
        mensage = f'musica: {int(volume_musica * 100)}'
        mesage2 = f'efeitos sonoros: {int(volume_sound * 100)}'
        txt1 = font.render(mensage, False, (255, 255, 255))
        txt2 = font.render(mesage2, False, (255, 255, 255))

        tela.blit(txt2, (5, 10))
        tela.blit(txt1, (5, 30))
        pygame.display.flip()

    elif estado_jogo == "JOGANDO":
        # --- Lógica de Música ---
        if not fade_started:
            now = pygame.time.get_ticks()
            if now - fade_start_time >= fade_duration:
                sons.play_music('musica play')
                sons.set_music_volume(0)
                fade_in_start = pygame.time.get_ticks()
                fade_started = True
        else: 
            now = pygame.time.get_ticks()
            elapsed = now - fade_in_start
            fade_in_duration = 3000
            if elapsed < fade_in_duration:
                volume = elapsed / fade_in_duration
                sons.set_music_volume(volume_musica)

        # --- Lógica de Update dos Sprites ---
        jogador.update(paredes, the_camera)
        inimigos.update(jogador, 300, paredes, True)
        the_camera.update(jogador)
        balas.update()

        # --- Lógica de Colisões e Regras do Jogo ---
        # Colisão de balas
        pygame.sprite.groupcollide(balas, paredes, True, False)
        pygame.sprite.groupcollide(balas, inimigos, True, True)

        # Coleta de itens
        itens_atingidos = pygame.sprite.spritecollide(jogador, todos_coletaveis, True)
        for item in itens_atingidos:
            if isinstance(item, Coracao):
                jogador.vida = min(jogador.vida_maxima, jogador.vida + 10)
                sons.play_control('recuperando vida', 'play')
            elif isinstance(item, Balas):
                jogador.balas += 5
                sons.play_control('coin', 'play')
            elif isinstance(item, Baterias):
                jogador.baterias_coletadas += 1
                sons.play_control('coin', 'play')
            elif isinstance(item, Balas):
                jogador.balas += 5
            elif isinstance(item, Baterias):
                jogador.baterias_coletadas += 1
        
        # Dano contínuo ao jogador
        inimigos_em_contato = pygame.sprite.spritecollide(jogador, inimigos, False)
        if inimigos_em_contato:
            agora = pygame.time.get_ticks()
            if agora - jogador.ultimo_dano_tempo > jogador.dano_cooldown:
                jogador.ultimo_dano_tempo = agora
                jogador.vida -= 5
        
        # --- Checagem de Vitória/Derrota ---
        if jogador.baterias_coletadas >= 10:
            sons.play_music('zerou game')
            sons.play_control('suporte aerio', 'play')
            estado_jogo = "VITORIA"
        if jogador.vida <= 0:
            jogador.vida = 0 
            sons.play_music('game over', 1)

            estado_jogo = "VITORIA"
        if jogador.vida <= 0:
            jogador.vida = 0 
            estado_jogo = "GAME_OVER"

        # --- Desenho de Todos os Elementos do Jogo ---
        tela.fill((0, 0, 0))
        tela.blit(background_img, the_camera.apply_rect(background_rect))
        for sprite in todos_os_sprites:
            tela.blit(sprite.image, the_camera.apply(sprite))
        desenhar_hud(tela, jogador, font)
        tela.blit(jogador.arma.image, the_camera.apply(jogador.arma))
    elif estado_jogo == "GAME_OVER":
        game_over.desenhar(tela)

    elif estado_jogo == "VITORIA":
        vitoria.desenhar(tela)

    # ---  ATUALIZAÇÃO FINAL DA TELA ---
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
