import pygame


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.musics = {}

    # carregar efeito sonoro
    def load_sound(self, name, path):
        self.sounds[name] = pygame.mixer.Sound(path)

    # armazenar caminho da música
    def load_music(self, name, path):
        self.musics[name] = path

    # controle do efeit sonoro
    def play_control(self, name, action, fade=0):
        if name in self.sounds:
            if action == 'play':
                self.sounds[name].play(fade_ms = fade)

            elif action == 'stop':
                self.sounds[name].fadeout(fade)
        else:
            print(f'The sound "{name}" was not found.')

    # tocar música de fundo
    def play_music(self, name, loops=-1):
        if name in self.musics:
            pygame.mixer.music.load(self.musics[name])
            pygame.mixer.music.play(loops)
        else:
            print(f'The music "{name}" was not found.')

    # ajustar volume do efeito sonoro
    def set_sound_volume(self, name, volume):
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
        else:
            print(f'The sound "{name}" was not found.')

    # ajustar volume da música de fundo
    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
