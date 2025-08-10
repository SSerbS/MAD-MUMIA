import pygame
from entidades import Jogador, Inimigo
from paredes import Parede

pygame.init()
tela = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sokoban Simples")
clock = pygame.time.Clock()

# --- Grupos de Sprites ---
todos_os_sprites = pygame.sprite.Group()
paredes = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
# --- Instanciando Objetos ---
jogador = Jogador(150, 150)
inimigo = Inimigo(50, 50, 1, 1, 10)
inimigo2 = Inimigo(150, 150, 1, 1, 10)
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

todos_os_sprites.add(jogador)
todos_os_sprites.add(inimigo)
todos_os_sprites.add(inimigo2)
rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False


    jogador.update(paredes)
    inimigo.update(jogador, 300, paredes, False)
    inimigo2.update(jogador, 300, paredes, True)
    tela.fill((30, 30, 30))
    todos_os_sprites.draw(tela)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()