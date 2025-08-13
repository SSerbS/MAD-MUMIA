import pygame
import random

from entidades import *
from paredes import *
from coletaveis import *
from camera import *
from mixer import AudioManager
from image import *

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

sons = AudioManager()

sons.load_music('musica menu', 'songs/musicas/musica_menu.ogg')
sons.load_music('musica play', 'songs/musicas/musica_acao.ogg')
sons.play_music('musica menu')
sons.set_music_volume(1)


# Layout do nível
layout = [
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "P E        E                    P",
    "P                               P",
    "P    E                        E P",
    "P      J                        P",
    "P          E                    P",
    "P                               P",
    "P E                  E          P",
    "P                               P",
    "P                               P",
    "P    E                        E P",
    "P                               P",
    "P          E                    P",
    "P                               P",
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

# 1. Defina uma constante para o tamanho do tile. Facilita muito a manutenção!
TILE_SIZE = 100

# 2. Crie uma lista de todos os locais válidos para spawn (onde não for parede)
spawn_points = []
for id_linha, linha in enumerate(layout):
    for id_coluna, char in enumerate(linha):
        if char == ' ': # ' ' é um espaço vazio, perfeito para spawn
            x = id_coluna * TILE_SIZE
            y = id_linha * TILE_SIZE
            # Adicionamos um pequeno deslocamento para centralizar o item no tile
            spawn_points.append((x + TILE_SIZE / 2, y + TILE_SIZE / 2))

# 3. Defina quantos itens de cada tipo você quer
num_coracoes = 5
num_balas = 10
num_baterias = 10
total_itens = num_coracoes + num_balas + num_baterias

# 4. Escolha posições aleatórias da lista de pontos válidos, sem repetição
# Garante que o jogo não quebre se houver menos pontos de spawn que itens
pontos_disponiveis = min(total_itens, len(spawn_points))
posicoes_escolhidas = random.sample(spawn_points, pontos_disponiveis)

# 5. Crie e adicione os itens aos grupos corretos
# Esta é a forma correta de adicionar os itens a múltiplos grupos
for i in range(num_coracoes):
    if not posicoes_escolhidas: break # Para se acabarem as posições
    item = Coracao(*posicoes_escolhidas.pop()) # O '*' desempacota a tupla (x,y)
    todos_coletaveis.add(item)
    todos_os_sprites.add(item) # Adiciona o item individualmente

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
menu = set_image('image/imagem menu.jpeg', (largura_tela, altura_tela))
background_img = pygame.image.load('image/MAPA PRONTO.png').convert()
background_img = pygame.transform.scale(background_img, (largura_mundo, altura_mundo))
background_rect = background_img.get_rect() # Cria um rect para o fundo, na posição (0,0)
#configurações pra tocar a música
fade_duration = 2000
fade_started = False
rodando = True

# Carregue as imagens para as telas de fim de jogo
game_over_img = pygame.image.load('image/TELA DERROTA.png').convert() # Substitua pelo nome do seu arquivo
game_over_img = pygame.transform.scale(game_over_img, (largura_tela, altura_tela))

vitoria_img = pygame.image.load('image/TELA VITÓRIA.png').convert() # Substitua pelo nome do seu arquivo
vitoria_img = pygame.transform.scale(vitoria_img, (largura_tela, altura_tela))

def desenhar_hud(tela, jogador, fonte):
    # --- VIDA ---
    # Barra de vida (opcional, mas visualmente bom)
    pygame.draw.rect(tela, 'red', (10, 10, 200, 25))
    vida_atual_largura = (jogador.vida / jogador.vida_maxima) * 200
    pygame.draw.rect(tela, 'green', (10, 10, vida_atual_largura, 25))
    # Texto da vida
    texto_vida = fonte.render(f"{jogador.vida}/{jogador.vida_maxima}", True, "white")
    tela.blit(texto_vida, (15, 12))

    # --- BATERIAS ---
    texto_baterias = fonte.render(f"Baterias: {jogador.baterias_coletadas} / 10", True, "yellow")
    tela.blit(texto_baterias, (10, 45))

    # --- MUNIÇÃO ---
    texto_balas = fonte.render(f"Munição: {jogador.balas}", True, "cyan")
    tela.blit(texto_balas, (10, 80))
    
def reiniciar_jogo():
    """Reseta o estado do jogo para seus valores iniciais."""
    print("--- REINICIANDO O JOGO ---")

    # 1. Limpa todos os grupos de sprites dinâmicos
    todos_os_sprites.empty()
    inimigos.empty()
    todos_coletaveis.empty()
    balas.empty()

    # 2. Reseta o estado do jogador para os valores iniciais
    jogador.vida = jogador.vida_maxima
    jogador.baterias_coletadas = 0
    jogador.balas = 0 # Ou o valor inicial que preferir

    # 3. Reposiciona o jogador e os inimigos baseados no layout original
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

    # 4. Gera novamente os coletáveis em posições aleatórias
    # (Este código é o mesmo que você já tem, mas agora dentro de uma função)
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

    # 5. Readiciona TODOS os sprites ao grupo principal de desenho
    todos_os_sprites.add(jogador)
    todos_os_sprites.add(inimigos) # Adiciona o grupo de inimigos
    todos_os_sprites.add(todos_coletaveis) # Adiciona o grupo de coletáveis
    
# ====================================================================================
# SUBSTITUA TODO O SEU 'while rodando:' POR ESTE BLOCO COMPLETO
# ====================================================================================
rodando = True
while rodando:
    # --- 1. LOOP DE EVENTOS GERAL ---
    # Este loop agora é mais simples. Ele captura os eventos, e a lógica de
    # o que fazer com eles vai para dentro de cada estado do jogo.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                rodando = False

            # Se estamos no MENU e aperta ENTER, começa o jogo
            if estado_jogo == "MENU" and event.key == pygame.K_RETURN:
                estado_jogo = "JOGANDO"
                pygame.mixer.music.fadeout(fade_duration)
                fade_start_time = pygame.time.get_ticks()
                fade_started = False

            # Se estamos em GAME OVER ou VITORIA e aperta ENTER, volta para o menu
            # (No futuro, isso chamaria uma função para reiniciar o jogo)
            if (estado_jogo == "GAME_OVER" or estado_jogo == "VITORIA") and event.key == pygame.K_RETURN:
                # AGORA CHAMAMOS A NOSSA FUNÇÃO DE RESET!
                reiniciar_jogo()
                
                # E então, voltamos para o menu
                estado_jogo = "MENU"
                sons.play_music('musica menu')
        
        # Evento de atirar com o mouse, que só funciona quando estamos jogando
        if estado_jogo == "JOGANDO" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Botão esquerdo do mouse
                bala = jogador.atirar()
                if bala:
                    todos_os_sprites.add(bala)
                    balas.add(bala)

    # --- 2. LÓGICA E DESENHO DE CADA ESTADO ---

    if estado_jogo == "MENU":
        menu.desenhar(tela)

    elif estado_jogo == "JOGANDO":
        # --- Lógica de Música ---
        if not fade_started:
            now = pygame.time.get_ticks()
            if now - fade_start_time >= fade_duration:
                sons.play_music('musica play')
                sons.set_music_volume(0)
                fade_in_start = pygame.time.get_ticks()
                fade_started = True
        else: # Lógica de fade in
            now = pygame.time.get_ticks()
            elapsed = now - fade_in_start
            fade_in_duration = 3000
            if elapsed < fade_in_duration:
                volume = elapsed / fade_in_duration
                sons.set_music_volume(volume)
            else:
                sons.set_music_volume(1)

        # --- Lógica de Update dos Sprites ---
        jogador.update(paredes)
        inimigos.update(jogador, 300, paredes, True)
        the_camera.update(jogador)
        balas.update(tela)

        # --- Lógica de Colisões e Regras do Jogo ---
        # Colisão de balas
        pygame.sprite.groupcollide(balas, paredes, True, False)
        pygame.sprite.groupcollide(balas, inimigos, True, True)

        # Coleta de itens
        itens_atingidos = pygame.sprite.spritecollide(jogador, todos_coletaveis, True)
        for item in itens_atingidos:
            if isinstance(item, Coracao):
                jogador.vida = min(jogador.vida_maxima, jogador.vida + 10)
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
            estado_jogo = "VITORIA"
        if jogador.vida <= 0:
            jogador.vida = 0 # Garante que a vida não fique negativa no HUD
            estado_jogo = "GAME_OVER"

        # --- Desenho de Todos os Elementos do Jogo ---
        tela.fill((0, 0, 0))
        tela.blit(background_img, the_camera.apply_rect(background_rect))
        for sprite in todos_os_sprites:
            tela.blit(sprite.image, the_camera.apply(sprite))
        desenhar_hud(tela, jogador, fonte_municao)

    elif estado_jogo == "GAME_OVER":
        tela.blit(game_over_img, (0, 0))

    elif estado_jogo == "VITORIA":
        tela.blit(vitoria_img, (0, 0))

    # --- 3. ATUALIZAÇÃO FINAL DA TELA ---
    # Isso acontece uma vez por frame, independente do estado do jogo
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
