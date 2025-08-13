import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(82)

        self.sounds = {}
        self.musics = {}

        
        # Define os volumes iniciais
        self.set_music_volume(0.8)
        self.set_sound_volume(0.8)

    def load_sound(self, name, path):
        self.sounds[name] = pygame.mixer.Sound(path)

    def load_music(self, name, path):
        self.musics[name] = path

    def play_control(self, name, action, fade=0):
        if name in self.sounds:
            if action == 'play':
                self.sounds[name].play(fade_ms=fade)
            elif action == 'stop':
                self.sounds[name].fadeout(fade)
        else:
            print(f'The sound "{name}" was not found.')

    def play_music(self, name, loops=-1):
        if name in self.musics:
            pygame.mixer.music.load(self.musics[name])
            pygame.mixer.music.play(loops)
        else:
            print(f'The music "{name}" was not found.')

    def set_sound_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)
        print(f"Volume do efeito sonoro ajustado para {volume}")

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
        print(f"Volume da música ajustado para {volume}")

