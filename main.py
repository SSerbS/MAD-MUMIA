import pygame
from entidades import *
from paredes import *
from coletaveis import *
from mixer import AudioManager
from menu import set_image

pygame.init()
pygame.mixer.init()
audio = AudioManager()

#imagem do menu
menu = set_image("image/imagem menu.jpeg", (800, 720))


#dando play na música
audio.load_music('music', 'songs/musicas/musica_acao.ogg')
audio.play_music('music')

tela = pygame.display.set_mode((800, 720))
pygame.display.set_caption("Sokoban Simples")
clock = pygame.time.Clock()


todos_os_sprites = pygame.sprite.Group()
paredes = pygame.sprite.Group()
inimigos = pygame.sprite.Group()


todos_coletaveis = pygame.sprite.Group()



jogador = Jogador(150, 150)
inimigo = Inimigo(50, 50, 1, 1, 10)
inimigo2 = Inimigo(150, 150, 1, 1, 10)


posicoes_dos_itens = [(200, 100), (700, 375), (600, 250)]


# Layout do nível
layout = [
    "PPPPPPPPPPPPPPPP",
    "P              P",
    "P      P       P",
    "P      P       P",
    "P  J   P       P",
    "P      P       P",
    "P      PPPPPPPPP",
    "P          E   P",
    "P              P",
    "P              P",
    "P              P",
    "P              P",
    "P              P",
    "P              P",
    "P              P",
    "PPPPPPPPPPPPPPPP",
]

for id_linha, linha in enumerate(layout):
    for id_coluna, char in enumerate(linha):
        x = id_coluna * 50
        y = id_linha * 50
        if char == 'P':
            p = Parede(x, y, 50, 50)
            paredes.add(p)
            todos_os_sprites.add(p)

        if char == 'J':
            jogador.pos = pygame.math.Vector2(x, y)
            jogador.rect.topleft = (x, y)

        if char == 'E':
            inimigo.pos = pygame.math.Vector2(x, y)
            inimigo.rect.topleft = (x, y)


for pos in posicoes_dos_itens:
    item_novo = Coracao(pos[0], pos[1])
    todos_coletaveis.add(item_novo)


todos_os_sprites.add(jogador)
todos_os_sprites.add(inimigo)
todos_os_sprites.add(inimigo2)


todos_os_sprites.add(todos_coletaveis)
score = 0
fonte_score = pygame.font.Font(None, 50)

menu_aq = True
rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if menu_aq and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                menu_aq = False
            
            if event.key == pygame.K_ESCAPE:
                rodando = False

    if menu_aq:
        tela.fill((0, 0, 0))
        menu.desenhar(tela)
    else:
        jogador.update(paredes)
        inimigo.update(jogador, 300, paredes, False)
        inimigo2.update(jogador, 300, paredes, True)

        tela.fill((30, 30, 30))
        todos_os_sprites.draw(tela)

        itens_atingidos = pygame.sprite.spritecollide(jogador, todos_coletaveis, True)
        if itens_atingidos:
            print("coletou")
            score += len(itens_atingidos)

        score_texto = fonte_score.render(f"{score}", True, "green")
        tela.blit(score_texto, (20, 20))

    pygame.display.flip()
    clock.tick(60)
