import speech_recognition as sr
import threading
import pygame
from pydub import AudioSegment, silence
from pydub.playback import _play_with_simpleaudio

# Carica il file MP3 e trova i chunks basati sui silenzi
audio_path = "001-Get fluent with AI - Use ChatGPT to learn and practice English.mp3"
audio = AudioSegment.from_mp3(audio_path)

print("")
print("#######################################################")
print(f"Elaborazione di {audio_path}... prego attendere")


# se il silenzio dura più di 300ms e il livello è inferiore a 40db
chunks = silence.split_on_silence(audio, min_silence_len=300, silence_thresh=-40)

# Calcola la posizione di inizio di ciascun chunk
chunk_starts = [0]
for i in range(1, len(chunks)):
    chunk_starts.append(chunk_starts[i-1] + len(chunks[i-1]))


# Unisci i chunks corti con il successivo
merged_chunks = []
i = 0
while i < len(chunks):
    current_chunk = chunks[i]
    # Se la durata del chunk è inferiore a 1 secondo e non è l'ultimo chunk
    while i + 1 < len(chunks) and len(current_chunk) < 500:
        i += 1
        # Unisci il chunk corrente con il successivo
        current_chunk += chunks[i]
    merged_chunks.append(current_chunk)
    i += 1

# Inizializza pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Audio Player')


current_playback = None  # Variabile per tenere traccia dell'ultimo oggetto di riproduzione


def play_chunk(chunk_index):
    global current_playback

    """Riproduce il chunk specificato dall'indice e stampa la sua posizione."""
    if 0 <= chunk_index < len(merged_chunks):
        # Se c'è una riproduzione in corso, fermala
        if current_playback is not None:
            current_playback.stop()

        # Calcola la posizione in minuti e secondi
        position_ms = chunk_starts[chunk_index]
        position_seconds = position_ms / 1000
        position_minutes = position_seconds // 60
        position_seconds = position_seconds % 60
        print(f"Riproduzione chunk {chunk_index+1}/{len(chunks)} - Posizione: {int(position_minutes)}:{int(position_seconds):02d}")

        # Riproduci il nuovo chunk e tieni traccia dell'oggetto di riproduzione
        current_playback = _play_with_simpleaudio(merged_chunks[chunk_index])


def recognize_commands():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                print("Listening for commands...")
                audio = r.listen(source)
                command = r.recognize_google(audio, language='it-IT').lower()
                print(f"Received command: {command}")

                if command == "avanti":
                    play_chunk(min(len(chunks) - 1, current_chunk_index + 1))
                elif command == "indietro":
                    play_chunk(max(0, current_chunk_index - 1))
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except Exception as e:
                print(f"An error occurred: {e}")


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
                current_chunk = min(len(merged_chunks) - 1, current_chunk + 1)  # Evita di superare il numero di chunks
                play_chunk(current_chunk)
            elif event.key == pygame.K_SPACE:
            	# Ripete l'ultimo chunk
                play_chunk(current_chunk)
            elif event.key == pygame.K_ESCAPE:
                running = False  # Chiude l'applicazione quando viene premuto ESC                
                
    pygame.display.flip()

pygame.quit()
