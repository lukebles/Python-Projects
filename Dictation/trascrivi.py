import pygame
from pydub import AudioSegment, silence
from pydub.playback import _play_with_simpleaudio

# Carica il file MP3 e trova i chunks basati sui silenzi
audio_path = "audio.mp3"
audio = AudioSegment.from_mp3(audio_path)

print("")
print("#######################################################")
print(f"Elaborazione di {audio_path}... prego attendere")


# se il silenzio dura più di 300ms e il livello è inferiore a 40db
chunks = silence.split_on_silence(audio, min_silence_len=300, silence_thresh=-40)

# Inizializza pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Audio Player')

def play_chunk(chunk_index):
    """Riproduce il chunk specificato dall'indice."""
    if 0 <= chunk_index < len(chunks):
        _play_with_simpleaudio(chunks[chunk_index])

current_chunk = 0
play_chunk(current_chunk)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
            	# ripete chunk precedente
                current_chunk = max(0, current_chunk - 1)  # Assicura che l'indice non sia negativo
                play_chunk(current_chunk)
            elif event.key == pygame.K_RIGHT:
            	# esegue il chunk successivo
                current_chunk = min(len(chunks) - 1, current_chunk + 1)  # Evita di superare il numero di chunks
                play_chunk(current_chunk)
            elif event.key == pygame.K_SPACE:
            	# Ripete l'ultimo chunk
                play_chunk(current_chunk)
            elif event.key == pygame.K_ESCAPE:
                running = False  # Chiude l'applicazione quando viene premuto ESC                
                
    pygame.display.flip()

pygame.quit()
