import pygame

from entidades import *
from paredes import *
from coletaveis import *
from camera import *

pygame.init()
largura_tela = 960
altura_tela = 960
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Sokoban Simples")
clock = pygame.time.Clock()

todos_os_sprites = pygame.sprite.Group()
balas = pygame.sprite.Group()
paredes = pygame.sprite.Group()
inimigos = pygame.sprite.Group()

todos_coletaveis = pygame.sprite.Group()

# --- Instanciando Objetos ---
jogador = Jogador(150, 150)
inimigo = Inimigo(50, 50, 1, 1, 10)
inimigo2 = Inimigo(150, 150, 1, 1, 10)
inimigos.add(inimigo, inimigo2)


posicoes_dos_itens = [(200, 100), (700, 375), (600, 250)]

# Layout do nível
layout = [
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "P              PPPPPPP         P",
    "P      P       PPPPPPP         P",
    "P      P       PPPPPPP         P",
    "P  J   P       PPPPPPP         P",
    "P      P       PPPPPPP         P",
    "P      PPPPPPPPPPPPPPP         P",
    "P          E   PPPPPPP         P",
    "P              PPPPPPP         P",
    "P              PPPPPPP         P",
    "P              PPPPPPP         P",
    "P              PPPPPPP         P",
    "P              PPPPPPP         P",
    "P                              P",
    "P                              P",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

largura_mundo = len(layout[0])*50
altura_mundo = len(layout)*50
the_camera = Camera(largura_tela, altura_tela, largura_mundo, altura_mundo)

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
fonte_municao = pygame.font.Font(None, 40)


rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

    jogador.update(paredes)
    inimigo.update(jogador, 300, paredes, False)
    inimigo2.update(jogador, 300, paredes, True)
    the_camera.update(jogador)

    itens_atingidos = pygame.sprite.spritecollide(jogador, todos_coletaveis, True)
    if itens_atingidos != []:
        print("coletou")
        score += len(itens_atingidos) 
    teclas_mouse = pygame.mouse.get_pressed()
    if teclas_mouse[0]:
        pos_mouse = pygame.mouse.get_pos()
        bala = jogador.atirar()
        if bala:
            todos_os_sprites.add(bala)
            balas.add(bala)

    balas.update(tela)
    pygame.sprite.groupcollide(balas, paredes, True, False)
    pygame.sprite.groupcollide(balas, inimigos, True, True)
    
    tela.fill("darkgreen")
    for sprite in todos_os_sprites:
        tela.blit(sprite.image, the_camera.apply(sprite))
   
    score_texto = fonte_score.render(f"{score}", True, "green")
    tela.blit(score_texto, (20, 20))
    municao_texto = fonte_municao.render(f"Balas: {jogador.balas}", True, "yellow")
    tela.blit(municao_texto, (10, 670))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()