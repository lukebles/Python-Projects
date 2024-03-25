import pvporcupine
import pyaudio
import struct
import pygame
from pydub import AudioSegment, silence
from pydub.playback import _play_with_simpleaudio


# Chiedi all'utente da quale chunk iniziare
def ask_for_starting_chunk(chunks):
    while True:
        try:
            starting_chunk_index = int(input(f"Da quale chunk vuoi partire? (1-{len(chunks)}) ")) - 1
            if 0 <= starting_chunk_index < len(chunks):
                return starting_chunk_index
            else:
                print(f"Per favore, inserisci un numero tra 1 e {len(chunks)}.")
        except ValueError:
            print("Input non valido. Per favore, inserisci un numero.")

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

def avanti():
    global current_chunk
    # esegue il chunk successivo
    current_chunk = min(len(merged_chunks) - 1, current_chunk + 1)  # Evita di superare il numero di chunks
    play_chunk(current_chunk)

def indietro():
    global current_chunk
    # ripete chunk precedente
    current_chunk = max(0, current_chunk - 1)  # Assicura che l'indice non sia negativo
    play_chunk(current_chunk)

def ripeti():
    global current_chunk    
    # Ripete l'ultimo chunk
    play_chunk(current_chunk)


################ Carica il file MP3 e trova i chunks basati sui silenzi #######
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

######### Inizializza pygame ####################################
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Audio Player')

current_playback = None  # Variabile per tenere traccia dell'ultimo oggetto di riproduzione    

########### da quale chunk parto? ###############################
current_chunk = ask_for_starting_chunk(chunks) #chunk_di_partenza
play_chunk(current_chunk)

##### Crea un'istanza di Porcupine ###########################
access_key = "insert your key"
porcupine = pvporcupine.create(access_key=access_key, keywords=["grapefruit", "americano", "terminator"])
# Inizializza PyAudio
pa = pyaudio.PyAudio()    
# Apre un flusso audio con PyAudio
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)
print("avanti='americano'  indietro='terminator'  ripeti='grapefruit'")

running = True
while running:
    # Legge il frame audio
    audio_frame = audio_stream.read(porcupine.frame_length)
    audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_frame)

    # Usa Porcupine per analizzare il frame audio
    keyword_index = porcupine.process(audio_frame)

    if keyword_index == 0:
        ripeti()
    elif keyword_index == 1:
        avanti()
    elif keyword_index == 2:
        indietro()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                indietro()
            elif event.key == pygame.K_RIGHT:
                avanti()
            elif event.key == pygame.K_SPACE:
                ripeti()
            elif event.key == pygame.K_ESCAPE:
                running = False  # Chiude l'applicazione quando viene premuto ESC                
                
    pygame.display.flip()

pygame.quit()
