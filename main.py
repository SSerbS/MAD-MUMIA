# Importa a biblioteca principal do Pygame para funcionalidades de jogo.
import pygame
# Importa a biblioteca random para gerar números e escolhas aleatórias.
import random

# Importa as classes e funções de outros arquivos do projeto.
# Isso mantém o código organizado.
from entidades import * # Contém as classes Jogador, Inimigo, Bala, etc.
from paredes import * # Contém a classe Parede.
from coletaveis import * # Contém as classes dos itens coletáveis (Coração, Baterias).
from camera import * # Contém a classe Camera para seguir o jogador.
from mixer import AudioManager # Contém uma classe para gerenciar áudio (músicas e sons).
from image import * # Contém funções para carregar e configurar imagens.

# --- INICIALIZAÇÃO DO PYGAME ---
# Inicia todos os módulos do Pygame que foram importados.
pygame.init()
# Inicia o módulo de áudio do Pygame.
pygame.mixer.init()

# --- CONFIGURAÇÕES DA TELA E JANELA ---
# Define a largura da janela do jogo em pixels.
largura_tela = 1280
# Define a altura da janela do jogo em pixels.
altura_tela = 720
# Cria a superfície principal da tela com as dimensões definidas.
tela = pygame.display.set_mode((largura_tela, altura_tela))
# Define o título que aparecerá na barra da janela.
pygame.display.set_caption("Sokoban Simples")
# Cria um objeto Clock para controlar a taxa de quadros por segundo (FPS).
clock = pygame.time.Clock()
# Define o estado inicial do jogo. Isso controla qual lógica e tela são mostradas.
estado_jogo = "MENU"

# --- GRUPOS DE SPRITES ---
# Grupos são "listas especiais" do Pygame para gerenciar e desenhar objetos do jogo (sprites).
todos_os_sprites = pygame.sprite.Group() # Grupo para desenhar todos os sprites de uma vez.
balas = pygame.sprite.Group()              # Grupo para gerenciar apenas as balas (colisões, etc.).
paredes = pygame.sprite.Group()            # Grupo para gerenciar as paredes (colisões).
inimigos = pygame.sprite.Group()           # Grupo para gerenciar os inimigos.
todos_coletaveis = pygame.sprite.Group() # Grupo para gerenciar todos os itens coletáveis.

# --- CRIAÇÃO DE OBJETOS PRINCIPAIS ---
# Cria uma instância da classe Jogador. As posições iniciais (150, 150) são temporárias.
jogador = Jogador(150, 150)

# Cria uma instância do gerenciador de áudio.
sons = AudioManager()

# Define os volumes iniciais para música e efeitos sonoros.
volume_musica = 0.8
volume_sound = 0.8

# --- CARREGAMENTO DE ÁUDIO ---
# Carrega os arquivos de música, associando-os a um nome fácil de usar.
sons.load_music('musica menu', 'songs/musicas/musica_menu.ogg')
sons.load_music('musica play', 'songs/musicas/musica_acao.ogg')
sons.load_music('game over', 'songs/musicas/game_overpaezao.mp3')
sons.load_music('zerou game', 'songs/musicas/musica_zerou_game.mp3')
# Toca a música do menu assim que o jogo começa.
sons.play_music('musica menu')

# Carrega os arquivos de efeitos sonoros.
sons.load_sound('coin', 'songs/smw_coin.wav')
sons.load_sound('321', 'songs/01._3_2_1.wav')
sons.load_sound('recuperando vida', 'songs/recuperando_vida.wav')
sons.load_sound('suporte aerio', 'songs/pedindo_apoio_aério.wav')
sons.load_sound('iniciando', 'songs/iniciando_game.wav')
sons.load_sound('carregando arma', 'songs/carregando_arma.wav')
sons.load_sound('dano', 'songs/steve_dano.wav')


# --- LAYOUT DO NÍVEL ---
# Uma lista de strings que representa o mapa do jogo.
# 'P' = Parede, 'J' = Jogador, 'E' = Inimigo, ' ' = Espaço vazio.
layout = [
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "P                               P",
    "P      E         E         E    P",
    "P    E               E        E P",
    "P      J       E         E      P",
    "P         E             E       P",
    "P               E               P",
    "P E       E           E      E  P",
    "P                               P",
    "P                 E       E     P",
    "P    E     E         E        E P",
    "P                               P",
    "P          E             E      P",
    "P     E         E               P",
    "P                               P",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

# --- CONFIGURAÇÃO DO MUNDO E CÂMERA ---
# Calcula a largura total do mundo do jogo baseado no layout e no tamanho de cada tile.
largura_mundo = len(layout[0]) * 100
# Calcula a altura total do mundo do jogo.
altura_mundo = len(layout) * 100
# Cria a câmera, passando as dimensões da tela e do mundo.
the_camera = Camera(largura_tela, altura_tela, largura_mundo, altura_mundo)

# --- GERAÇÃO DO NÍVEL A PARTIR DO LAYOUT ---
# Itera sobre cada linha do layout com seu índice.
for id_linha, linha in enumerate(layout):
    # Itera sobre cada caractere da linha com seu índice.
    for id_coluna, char in enumerate(linha):
        # Calcula a posição x e y no mundo do jogo.
        x = id_coluna * 100
        y = id_linha * 100
        # Se o caractere for 'P', cria uma parede naquela posição.
        if char == 'P':
            p = Parede(x, y, 100, 100)
            paredes.add(p) # Adiciona a parede ao grupo de paredes.

        # Se o caractere for 'J', define a posição inicial do jogador.
        if char == 'J':
            jogador.pos = pygame.math.Vector2(x, y)
            jogador.rect.topleft = (x, y)

        # Se o caractere for 'E', cria um inimigo naquela posição.
        if char == 'E':
            # Cria uma instância de Inimigo com posição, velocidade, dano e vida.
            novo_inimigo = Inimigo(x, y, 2, 1, 10) 
            inimigos.add(novo_inimigo) # Adiciona ao grupo de inimigos.
            todos_os_sprites.add(novo_inimigo) # Adiciona também ao grupo de desenho.

# --- LÓGICA DE SPAWN ALEATÓRIO DE ITENS ---
# Define o tamanho de cada "bloco" do mapa para facilitar cálculos.
TILE_SIZE = 100

# Cria uma lista para armazenar todas as coordenadas válidas para spawn (espaços vazios).
spawn_points = []
for id_linha, linha in enumerate(layout):
    for id_coluna, char in enumerate(linha):
        # Se o caractere for um espaço vazio...
        if char == ' ':
            x = id_coluna * TILE_SIZE
            y = id_linha * TILE_SIZE
            # Adiciona a coordenada do centro do tile à lista de pontos de spawn.
            spawn_points.append((x + TILE_SIZE / 2, y + TILE_SIZE / 2))

# Define a quantidade de cada tipo de item a ser gerado.
num_coracoes = 5
num_balas = 5
num_baterias = 10
total_itens = num_coracoes + num_balas + num_baterias

# Escolhe posições aleatórias da lista de pontos válidos, sem repetir.
# Garante que não tentemos criar mais itens do que espaços disponíveis.
pontos_disponiveis = min(total_itens, len(spawn_points))
posicoes_escolhidas = random.sample(spawn_points, pontos_disponiveis)

# Cria e posiciona os itens coletáveis no mapa.
# Para cada coração a ser criado...
for i in range(num_coracoes):
    if not posicoes_escolhidas: break # Para o loop se não houver mais posições.
    # O '*' desempacota a tupla (x,y) e a passa como argumentos para a classe Coracao.
    item = Coracao(*posicoes_escolhidas.pop()) 
    todos_coletaveis.add(item) # Adiciona ao grupo de coletáveis.
    todos_os_sprites.add(item)   # Adiciona ao grupo de desenho.

# Repete o processo para as balas.
for i in range(num_balas):
    if not posicoes_escolhidas: break
    item = Balas(*posicoes_escolhidas.pop())
    todos_coletaveis.add(item)
    todos_os_sprites.add(item)
    
# Repete o processo para as baterias.
for i in range(num_baterias):
    if not posicoes_escolhidas: break
    item = Baterias(*posicoes_escolhidas.pop())
    todos_coletaveis.add(item)
    todos_os_sprites.add(item)

# Adiciona o jogador ao grupo principal de desenho.
todos_os_sprites.add(jogador)

# --- VARIÁVEIS DE UI (INTERFACE DO USUÁRIO) E FONTES ---
score = 0
fonte_score = pygame.font.SysFont('Lucida Console', 20) # Fonte para o score (não usado atualmente).
fonte_municao = pygame.font.SysFont('Lucida Console', 20) # Fonte para a HUD do jogo.
fonte_countdown = pygame.font.SysFont('Lucida Console', 250) # Fonte grande para a contagem regressiva.
fonte_indicador_volume = pygame.font.SysFont('Lucida Console', 40) # Fonte para o indicador de volume.

# Variáveis para controlar a exibição do indicador de volume na tela.
indicador_volume_texto = "" # O texto a ser mostrado (ex: "Música: 80%").
indicador_volume_timer = 0  # Timer para controlar por quanto tempo o indicador fica visível.
DURACAO_INDICADOR_MS = 2000 # Duração em milissegundos (2 segundos).

# Variável para registrar o momento em que a contagem regressiva começa.
countdown_start_time = 0 

# Carrega a imagem de fundo do mapa.
background_img = pygame.image.load('image/MAPA PRONTO.png').convert()
background_img = pygame.transform.scale(background_img, (largura_mundo, altura_mundo))
background_rect = background_img.get_rect()

# Variáveis para o controle de fade (transição suave) da música.
fade_duration = 2000
fade_started = False
rodando = True

# --- CARREGAMENTO DE IMAGENS DE TELA ---
# Usa a função `set_image` para carregar e escalar as imagens das telas de estado.
menu = set_image('image/imagem menu.jpeg', (largura_tela, altura_tela))
game_over = set_image('image/TELA DERROTA.png', (largura_tela, altura_tela))
vitoria = set_image('image/TELA VITÓRIA.png', (largura_tela, altura_tela))
background = set_image('image/MAPA PRONTO.png', (largura_tela, altura_tela))

# --- FUNÇÕES AUXILIARES ---
def desenhar_hud(tela, jogador, fonte):
    # Fundo do HUD
    fundo = pygame.Surface((220, 110), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, 150))
    tela.blit(fundo, (5, 5))

    cor_texto = (255, 255, 255)
    verde_barra = (34, 177, 76)
    vemelho_barra = (128, 0, 0)

    # --- VIDA ---
    pygame.draw.rect(tela, vemelho_barra, (10, 10, 200, 25))
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
    """Reseta o estado do jogo para seus valores iniciais para uma nova partida."""
    print("--- REINICIANDO O JOGO ---")

    # 1. Limpa todos os grupos de sprites que são criados dinamicamente.
    todos_os_sprites.empty()
    inimigos.empty()
    todos_coletaveis.empty()
    balas.empty()

    # 2. Reseta os atributos do jogador para os valores padrão.
    jogador.vida = jogador.vida_maxima
    jogador.baterias_coletadas = 0
    jogador.balas = 0 # Define a munição inicial.

    # 3. Reposiciona o jogador e recria os inimigos a partir do layout original.
    for id_linha, linha in enumerate(layout):
        for id_coluna, char in enumerate(linha):
            x = id_coluna * TILE_SIZE
            y = id_linha * TILE_SIZE
            if char == 'J':
                jogador.pos = pygame.math.Vector2(x, y)
                jogador.rect.topleft = (x, y)
            if char == 'E':
                # Recria os inimigos para garantir que eles "revivam".
                inimigo_novo = Inimigo(x, y, 2, 1, 10)
                inimigos.add(inimigo_novo)

    # 4. Gera novamente os itens coletáveis em posições aleatórias.
    spawn_points.clear() # Limpa a lista de pontos de spawn antiga.
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

    # 5. Readiciona todos os objetos recriados ao grupo principal de desenho.
    todos_os_sprites.add(jogador)
    todos_os_sprites.add(inimigos)
    todos_os_sprites.add(todos_coletaveis)

# --- LOOP PRINCIPAL DO JOGO ---
rodando = True
while rodando:
    # --- 1. LOOP DE PROCESSAMENTO DE EVENTOS ---
    # Captura todas as ações do usuário (teclado, mouse, fechar janela).
    for event in pygame.event.get():
        # Se o usuário clicar no botão de fechar a janela.
        if event.type == pygame.QUIT:
            rodando = False
        # Se uma tecla for pressionada.
        if event.type == pygame.KEYDOWN:
            # Se a tecla for ESC, fecha o jogo.
            if event.key == pygame.K_ESCAPE:
                rodando = False

            # Se estiver no MENU e a tecla ENTER for pressionada, inicia a contagem.
            if estado_jogo == "MENU" and event.key == pygame.K_RETURN:
                the_camera.update(jogador) # Atualiza a câmera para a posição do jogador.
                estado_jogo = "COUNTDOWN"  # Muda o estado do jogo.
                countdown_start_time = pygame.time.get_ticks() # Registra o tempo de início.
                sons.play_control('321', 'play') # Toca o som "3, 2, 1".

            # Se estiver na tela de GAME OVER ou VITÓRIA e ENTER for pressionado, reinicia.
            if (estado_jogo == "GAME_OVER" or estado_jogo == "VITORIA") and event.key == pygame.K_RETURN:
                reiniciar_jogo() # Chama a função para resetar tudo.
                estado_jogo = "MENU" # Volta para o estado de menu.
                sons.play_music('musica menu') # Toca a música do menu.

        # Se uma tecla for solta (ideal para ações que não devem se repetir rapidamente).
        if event.type == pygame.KEYUP:
            # Aumenta o volume da música (limitado a 1.0).
            if event.key == pygame.K_UP:
                volume_musica = min(1.0, round(volume_musica + 0.1, 1))
                sons.set_music_volume(volume_musica)
                # Ativa o indicador de volume na tela.
                indicador_volume_texto = f"Música: {int(volume_musica * 100)}%"
                indicador_volume_timer = pygame.time.get_ticks()

            # Diminui o volume da música (limitado a 0.0).
            if event.key == pygame.K_DOWN:
                volume_musica = max(0.0, round(volume_musica - 0.1, 1))
                sons.set_music_volume(volume_musica)
                indicador_volume_texto = f"Música: {int(volume_musica * 100)}%"
                indicador_volume_timer = pygame.time.get_ticks()

            # Aumenta o volume dos efeitos sonoros.
            if event.key == pygame.K_RIGHT:
                volume_sound = min(1.0, round(volume_sound + 0.1, 1))
                sons.set_sound_volume(volume_sound)
                indicador_volume_texto = f"Efeitos: {int(volume_sound * 100)}%"
                indicador_volume_timer = pygame.time.get_ticks()

            # Diminui o volume dos efeitos sonoros.
            if event.key == pygame.K_LEFT:
                volume_sound = max(0.0, round(volume_sound - 0.1, 1))
                sons.set_sound_volume(volume_sound)
                indicador_volume_texto = f"Efeitos: {int(volume_sound * 100)}%"
                indicador_volume_timer = pygame.time.get_ticks()
                
        # Evento de atirar com o mouse (só funciona durante o jogo).
        if estado_jogo == "JOGANDO" and event.type == pygame.MOUSEBUTTONDOWN:
            # Se o botão esquerdo do mouse (botão 1) for clicado.
            if event.button == 1:
                # Pega a posição (x,y) do mouse na tela.
                pos_mouse_tela = pygame.mouse.get_pos()
                # Converte a posição da tela para a posição no mundo do jogo, considerando o deslocamento da câmera.
                pos_mouse_mundo = (pos_mouse_tela[0] - the_camera.camera_pos.x, 
                                   pos_mouse_tela[1] - the_camera.camera_pos.y)
                # Chama o método de atirar do jogador.
                bala = jogador.atirar(pos_mouse_mundo)
                # Se uma bala foi realmente criada (ex: se houver munição).
                if bala:
                    todos_os_sprites.add(bala) # Adiciona a bala para ser desenhada.
                    balas.add(bala)            # Adiciona a bala ao grupo de balas para colisões.

    # --- 2. LÓGICA E DESENHO BASEADOS NO ESTADO DO JOGO ---
    # Esta seção está fora do loop de eventos, mas dentro do loop principal.
    # O código aqui executa a cada quadro.

    if estado_jogo == "MENU":
        # Desenha a imagem da tela de menu.
        menu.desenhar(tela)

    elif estado_jogo == "COUNTDOWN":
        # Desenha o fundo do jogo durante a contagem.
        tela.fill((0, 0, 0)) # Limpa a tela.
        # Desenha a imagem de fundo do mapa, aplicando o deslocamento da câmera.
        tela.blit(background_img, the_camera.apply_rect(background_rect))
        
        # Lógica da contagem regressiva.
        tempo_passado = pygame.time.get_ticks() - countdown_start_time
        texto_contagem = ""
        if tempo_passado < 1000: # Primeiro segundo
            texto_contagem = "3"
        elif tempo_passado < 2000: # Segundo segundo
            texto_contagem = "2"
        elif tempo_passado < 3000: # Terceiro segundo
            texto_contagem = "1"
        else: # Após 3 segundos
            estado_jogo = "JOGANDO" # Muda para o estado de jogo.
            sons.play_control('iniciando', 'play') # Toca som "iniciando".
            pygame.mixer.music.fadeout(fade_duration) # Começa a diminuir o volume da música do menu.
            fade_start_time = pygame.time.get_ticks()
            fade_started = False
        
        # Desenha o número da contagem na tela.
        if texto_contagem:
            numero_renderizado = fonte_countdown.render(texto_contagem, True, "white")
            rect_numero = numero_renderizado.get_rect(center=(largura_tela / 2, altura_tela / 2))
            # Desenha uma sombra para o número para melhor visibilidade.
            sombra = fonte_countdown.render(texto_contagem, True, "black")
            rect_sombra = sombra.get_rect(center=(largura_tela / 2 + 5, altura_tela / 2 + 5))
            tela.blit(sombra, rect_sombra)
            tela.blit(numero_renderizado, rect_numero)

    elif estado_jogo == "JOGANDO":
        # --- Lógica de Música ---
        # Controla a transição da música do menu para a música de ação.
        if not fade_started:
            now = pygame.time.get_ticks()
            if now - fade_start_time >= fade_duration:
                sons.play_music('musica play') # Toca a música de ação.
                sons.set_music_volume(0) # Começa com volume 0 para fazer fade in.
                fade_in_start = pygame.time.get_ticks()
                fade_started = True
        else: # Lógica de fade in (aumento gradual do volume).
            now = pygame.time.get_ticks()
            elapsed = now - fade_in_start
            fade_in_duration = 3000
            if elapsed < fade_in_duration:
                volume = elapsed / fade_in_duration
                sons.set_music_volume(volume * volume_musica) # Aumenta até o volume definido pelo usuário.

        # --- Lógica de Atualização dos Sprites ---
        # Chama o método `update` de cada objeto/grupo para atualizar sua lógica (movimento, etc.).
        jogador.update(paredes, the_camera)
        inimigos.update(jogador, 500, paredes, True)
        the_camera.update(jogador) # A câmera segue o jogador.
        balas.update() # As balas se movem.

        # --- Lógica de Colisões e Regras do Jogo ---
        # Verifica colisão entre balas e paredes. `True` destrói a bala, `False` não destrói a parede.
        pygame.sprite.groupcollide(balas, paredes, True, False)
        # Verifica colisão entre balas e inimigos. `True, True` destrói ambos.
        pygame.sprite.groupcollide(balas, inimigos, True, True)

        # Verifica colisão entre o jogador e os itens coletáveis. `True` remove o item do grupo.
        itens_atingidos = pygame.sprite.spritecollide(jogador, todos_coletaveis, True)
        for item in itens_atingidos:
            if isinstance(item, Coracao): # Se o item for um coração...
                jogador.vida = min(jogador.vida_maxima, jogador.vida + 10) # Recupera vida.
                sons.play_control('recuperando vida', 'play')
            elif isinstance(item, Balas): # Se for munição...
                jogador.balas += 5 # Adiciona balas.
                sons.play_control('carregando arma', 'play')
            elif isinstance(item, Baterias): # Se for uma bateria...
                jogador.baterias_coletadas += 1 # Incrementa o contador.
                sons.play_control('coin', 'play')
        
        # Dano contínuo se o jogador estiver em contato com inimigos.
        
        inimigos_em_contato = pygame.sprite.spritecollide(jogador, inimigos, False)
        if inimigos_em_contato:
            agora = pygame.time.get_ticks()
            # Verifica se já passou o tempo de cooldown para tomar dano de novo.
            if agora - jogador.ultimo_dano_tempo > jogador.dano_cooldown:
                jogador.ultimo_dano_tempo = agora # Reseta o timer do dano.
                jogador.ultimo_flash_tempo = agora
                jogador.vida -= 1 # Causa dano ao jogador
                if jogador.vida % 2 == 0:
                    sons.play_control('dano', 'play')
        
        # --- Checagem de Condições de Vitória/Derrota ---
        if jogador.baterias_coletadas >= 10: # Se coletou todas as baterias...
            sons.play_music('zerou game') # Toca música de vitória.
            sons.play_control('suporte aerio', 'play')
            estado_jogo = "VITORIA" # Muda o estado para vitória.
        if jogador.vida <= 0: # Se a vida do jogador chegar a zero...
            jogador.vida = 0 # Garante que a vida não fique negativa na HUD.
            sons.play_music('game over', 1) # Toca música de game over.
            estado_jogo = "GAME_OVER" # Muda o estado para derrota.

        # --- Desenho de Todos os Elementos do Jogo ---
        tela.fill((0, 0, 0)) # Limpa a tela.
        tela.blit(background_img, the_camera.apply_rect(background_rect)) # Desenha o fundo.
        # Itera e desenha cada sprite na tela, aplicando o deslocamento da câmera.
        for sprite in todos_os_sprites:
            tela.blit(sprite.image, the_camera.apply(sprite))
        # Desenha a arma do jogador por cima dele.
        tela.blit(jogador.arma.image, the_camera.apply(jogador.arma))
        # Desenha a interface do usuário (HUD) por cima de tudo.
        desenhar_hud(tela, jogador, fonte_municao)
        
    elif estado_jogo == "GAME_OVER":
        # Desenha a imagem da tela de derrota.
        game_over.desenhar(tela)

    elif estado_jogo == "VITORIA":
        # Desenha a imagem da tela de vitória.
        vitoria.desenhar(tela)

    # --- DESENHA O INDICADOR DE VOLUME TEMPORÁRIO (POR CIMA DE TUDO) ---
    agora = pygame.time.get_ticks()
    # Verifica se o tempo de exibição do indicador ainda não acabou.
    if agora - indicador_volume_timer < DURACAO_INDICADOR_MS:
        # Cria uma superfície semi-transparente para servir de fundo para o texto.
        fundo_surf = pygame.Surface((300, 60), pygame.SRCALPHA)
        fundo_surf.fill((0, 0, 0, 150)) # Cor preta com 150 de alfa (transparência).
        fundo_rect = fundo_surf.get_rect(center=(largura_tela / 2, 60))
        tela.blit(fundo_surf, fundo_rect)

        # Renderiza e desenha o texto do volume.
        texto_renderizado = fonte_indicador_volume.render(indicador_volume_texto, True, "white")
        rect_texto = texto_renderizado.get_rect(center=(largura_tela / 2, 60))
        tela.blit(texto_renderizado, rect_texto)


    # --- ATUALIZAÇÃO FINAL DA TELA ---
    # Mostra tudo o que foi desenhado neste quadro na tela.
    pygame.display.flip()
    # Limita o jogo a rodar a no máximo 60 quadros por segundo.
    clock.tick(60)

# --- FIM DO JOGO ---
# Sai do Pygame de forma limpa.
pygame.quit()
