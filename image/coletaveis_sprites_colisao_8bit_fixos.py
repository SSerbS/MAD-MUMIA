# -*- coding: utf-8 -*-
import pygame
import math
import random
import os

"""
Versão 8-bit com nomes de arquivos FIXOS em PT-BR e posições ajustadas.
Coloque os PNGs na mesma pasta do script com estes nomes exatos:

- escopeta.png  (arma)
- bala.png      (munição)
- coracao.png   (vida/comida)
- bateria.png   (peça/energia)

Rode: python coletaveis_sprites_colisao_8bit_fixos.py
"""

# ---------- NOMES FIXOS ----------
PATH_SHOTGUN = "escopeta.png"
PATH_BULLET  = "bala.png"
PATH_HEART   = "coracao.png"
PATH_BATTERY = "bateria.png"

# ---------- JANELA ----------
WIDTH, HEIGHT = 960, 540
FPS = 60

# ---------- CORES ----------
SAND      = (230, 214, 170)
INK       = (24, 24, 24)
WHITE     = (250, 250, 250)
YELLOW    = (251, 231, 76)
ORANGE    = (247, 168, 47)
RED       = (236, 64, 74)
CYAN      = (119, 221, 231)

# ---------- UTILS ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def make_pixel_surface(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)

def draw_pixel(surf, x, y, color, size=4):
    pygame.draw.rect(surf, color, (x, y, size, size))

def load_img_required(path, max_w=180, max_h=120):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {path}")
    img = pygame.image.load(path).convert_alpha()
    # Reduz gentilmente se for gigante (mantém o 'look' pixelado)
    w, h = img.get_width(), img.get_height()
    if w > max_w or h > max_h:
        ratio = min(max_w / w, max_h / h)
        new_w, new_h = max(1, int(w * ratio)), max(1, int(h * ratio))
        img = pygame.transform.scale(img, (new_w, new_h))
    return img

# ---------- CLASSES ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = make_pixel_surface(40, 40)
        pygame.draw.rect(self.image, (255, 80, 80), (0, 0, 40, 40))
        pygame.draw.rect(self.image, INK, (0, 0, 40, 40), 3)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 7

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if dx and dy:
            inv = 1 / math.sqrt(2)
            dx *= inv; dy *= inv
        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)

class Effect(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.frames = []
        self.i = 0
        self.pos = pos

    def update(self):
        self.i += 1
        if self.i >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[self.i]
            self.rect = self.image.get_rect(center=self.pos)

class PixelBurst(Effect):   # munição (bala.png)
    def __init__(self, pos, pixels=24, steps=14, speed=3.3, size=4, colors=(YELLOW, ORANGE)):
        super().__init__(pos)
        self.frames = []
        w = h = 96
        dirs = []
        for _ in range(pixels):
            ang = random.random() * math.tau
            dirs.append((math.cos(ang), math.sin(ang), random.choice(colors)))
        for t in range(steps):
            surf = make_pixel_surface(w, h)
            for cx, cy, col in dirs:
                r = (t + 1) * speed
                x = w//2 + int(cx * r)
                y = h//2 + int(cy * r)
                draw_pixel(surf, x, y, col, size=size)
            self.frames.append(surf)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

class PixelPop(Effect):     # coração (coracao.png)
    def __init__(self, pos, steps=16, base=6, grow=3, color=RED):
        super().__init__(pos)
        self.frames = []
        w = h = 96
        for t in range(steps):
            surf = make_pixel_surface(w, h)
            radius = base + t * grow
            for k in range(0, radius, 2):
                pygame.draw.rect(surf, color, (w//2 - k, h//2 - k, 2*k, 2*k), 2)
            self.frames.append(surf)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

class PixelScan(Effect):    # bateria (bateria.png)
    def __init__(self, pos, steps=14, width=100, height=40):
        super().__init__(pos)
        self.frames = []
        W, H = width, height
        for t in range(steps):
            surf = make_pixel_surface(W, H)
            span = int(8 + t * 6)
            y = H//2 - 2
            for x in range(W//2 - span, W//2 + span, 6):
                draw_pixel(surf, x, y, YELLOW, size=6)
                draw_pixel(surf, x, y+8, ORANGE, size=6)
            self.frames.append(surf)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

class PixelRing(Effect):    # escopeta (escopeta.png)
    def __init__(self, pos, steps=14, start=6, step=4, color=CYAN):
        super().__init__(pos)
        self.frames = []
        w = h = 120
        for t in range(steps):
            surf = make_pixel_surface(w, h)
            side = start + t * step
            pygame.draw.rect(surf, color, (w//2 - side, h//2 - side, 2*side, 2*side), 3)
            self.frames.append(surf)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

class Collectible(pygame.sprite.Sprite):
    def __init__(self, kind, image, pos, effect_cls):
        super().__init__()
        self.kind = kind
        self.base_image = image
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.effect_cls = effect_cls
        self.hover = 0

    def update(self):
        # flutuação discreta
        self.hover += 1
        if self.hover % 18 == 0: self.rect.y -= 1
        if self.hover % 36 == 0: self.rect.y += 1

    def on_collect(self, effects_group):
        effects_group.add(self.effect_cls(self.rect.center))
        self.kill()

# ---------- MAIN ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Coletáveis 8-bit - Nomes Fixos (PT-BR)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)

    # Carrega imagens com nomes fixos
    img_shotgun = load_img_required(PATH_SHOTGUN)
    img_bullet  = load_img_required(PATH_BULLET)
    img_heart   = load_img_required(PATH_HEART)
    img_battery = load_img_required(PATH_BATTERY)

    all_sprites  = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    effects      = pygame.sprite.Group()
    player_group = pygame.sprite.GroupSingle()

    player = Player((WIDTH//2, HEIGHT//2))
    all_sprites.add(player); player_group.add(player)

    # ---- POSIÇÕES EM GRADE (mais organizado) ----
    #     [escopeta]  [bala]
    #     [coracao]   [bateria]
    grid = {
        "arma":    (WIDTH*0.30, HEIGHT*0.35),
        "municao": (WIDTH*0.70, HEIGHT*0.35),
        "comida":  (WIDTH*0.30, HEIGHT*0.65),
        "peca":    (WIDTH*0.70, HEIGHT*0.65),
    }

    SPAWNS = [
        ("arma",    img_shotgun, grid["arma"],    PixelRing),
        ("municao", img_bullet,  grid["municao"], PixelBurst),
        ("comida",  img_heart,   grid["comida"],  PixelPop),
        ("peca",    img_battery, grid["peca"],    PixelScan),
    ]

    for kind, img, pos, effect in SPAWNS:
        c = Collectible(kind, img, (int(pos[0]), int(pos[1])), effect)
        collectibles.add(c); all_sprites.add(c)

    running = True
    while running:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        player_group.update(); collectibles.update(); effects.update()

        for c in pygame.sprite.spritecollide(player, collectibles, False):
            c.on_collect(effects)

        screen.fill(SAND)
        all_sprites.draw(screen); effects.draw(screen)

        pygame.draw.rect(screen, (0,0,0,120), (0,0,WIDTH,30))
        msg = "Nomes fixos: escopeta.png, bala.png, coracao.png, bateria.png — Colete os itens!"
        screen.blit(font.render(msg, True, WHITE), (10, 5))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
