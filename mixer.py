# Importa a biblioteca principal do Pygame.
import pygame

# --- DEFINIÇÃO DA CLASSE AudioManager ---
# Esta classe serve como um centro de controle para todo o áudio do jogo.
# Ela encapsula a lógica de carregar, tocar e ajustar o volume de
# efeitos sonoros e músicas, mantendo o código principal do jogo mais limpo.
class AudioManager:
    # O método __init__ é o construtor da classe, executado quando um objeto AudioManager é criado.
    def __init__(self):
        # Inicializa o módulo 'mixer' do Pygame, que é responsável por todo o áudio.
        pygame.mixer.init()
        # Define o número de canais de áudio disponíveis para tocar efeitos sonoros simultaneamente.
        # O padrão é 8. Um número alto como 82 garante que muitos sons possam tocar ao mesmo tempo
        # sem que um corte o outro.
        pygame.mixer.set_num_channels(82)

        # Cria um dicionário para armazenar os efeitos sonoros já carregados na memória.
        # A chave será um nome amigável (ex: 'tiro') e o valor será o objeto de som do Pygame.
        self.sounds = {}
        # Cria um dicionário para armazenar os caminhos das músicas.
        # A chave será um nome amigável (ex: 'musica_menu') e o valor será o caminho do arquivo.
        # Músicas não são pré-carregadas para economizar memória; elas são tocadas via streaming.
        self.musics = {}

        # Define os volumes iniciais para música e efeitos sonoros ao criar o objeto.
        self.set_music_volume(0.8)  # Volume da música em 80%
        self.set_sound_volume(0.8)  # Volume dos efeitos em 80%

    def load_sound(self, name, path):
        """
        Carrega um efeito sonoro na memória e o armazena no dicionário 'self.sounds'.
        name: Um nome (string) para identificar o som.
        path: O caminho do arquivo de áudio (.wav, .ogg).
        """
        # Cria um objeto de som do Pygame a partir do arquivo e o associa ao nome fornecido.
        self.sounds[name] = pygame.mixer.Sound(path)

    def load_music(self, name, path):
        """
        Registra o caminho de um arquivo de música no dicionário 'self.musics'.
        name: Um nome (string) para identificar a música.
        path: O caminho do arquivo de áudio (.mp3, .ogg).
        """
        # Apenas armazena o caminho do arquivo para ser usado depois, não carrega o áudio.
        self.musics[name] = path

    def play_control(self, name, action, fade=0):
        """
        Controla a reprodução de um efeito sonoro (tocar ou parar).
        name: O nome do som a ser controlado.
        action: A ação a ser executada ('play' ou 'stop').
        fade: Duração em milissegundos para o efeito de fade-in ou fade-out.
        """
        # Verifica se o som com o nome fornecido foi carregado.
        if name in self.sounds:
            if action == 'play':
                # Toca o som. 'fade_ms' cria um efeito de fade-in.
                self.sounds[name].play(fade_ms=fade)
            elif action == 'stop':
                # Para o som com um efeito de fade-out.
                self.sounds[name].fadeout(fade)
        else:
            # Informa no console se o som não foi encontrado.
            print(f'O som "{name}" não foi encontrado.')

    def play_music(self, name, loops=-1):
        """
        Toca uma música a partir do caminho registrado.
        name: O nome da música a ser tocada.
        loops: O número de vezes que a música deve repetir. -1 significa tocar indefinidamente.
        """
        # Verifica se a música com o nome fornecido foi registrada.
        if name in self.musics:
            # Carrega a música no canal de música dedicado do Pygame.
            pygame.mixer.music.load(self.musics[name])
            # Toca a música carregada.
            pygame.mixer.music.play(loops)
        else:
            # Informa no console se a música não foi encontrada.
            print(f'A música "{name}" não foi encontrada.')

    def set_sound_volume(self, volume):
        """

        Ajusta o volume de TODOS os efeitos sonoros carregados.
        volume: Um valor de 0.0 (mudo) a 1.0 (máximo).
        """
        # Itera sobre cada objeto de som no dicionário 'self.sounds'.
        for sound in self.sounds.values():
            # Define o volume para aquele som específico.
            sound.set_volume(volume)
        print(f"Volume do efeito sonoro ajustado para {volume}")

    def set_music_volume(self, volume):
        """
        Ajusta o volume do canal de música.
        volume: Um valor de 0.0 (mudo) a 1.0 (máximo).
        """
        # O Pygame tem um controle de volume separado para o canal de música.
        pygame.mixer.music.set_volume(volume)
        print(f"Volume da música ajustado para {volume}")
