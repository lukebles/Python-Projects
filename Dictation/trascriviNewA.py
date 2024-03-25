import pygame
from pydub import AudioSegment, silence
from pydub.playback import _play_with_simpleaudio as play_audio

import pvporcupine
import pyaudio
import struct


current_playback = None  # Variabile per tenere traccia dell'ultimo oggetto di riproduzione    

def ms_to_min_sec(ms):
    seconds = int((ms // 1000) % 60)
    minutes = int((ms // (1000 * 60)) % 60)
    return f"{minutes}:{seconds:02}"

def trova_posizioni_pause(file_mp3, lunghezza_pausa_ms=300, soglia_silenzio_db=-40):
    # Carica il file MP3
    audio = AudioSegment.from_mp3(file_mp3)
    
    # Usa detect_nonsilent per trovare le parti in cui c'è parlato, invertendo la logica
    # per determinare le pause. Ci restituisce una lista di tuple (start, end) in millisecondi
    # dove NON c'è silenzio (cioè dove c'è parlato)
    segmenti_parlato = silence.detect_nonsilent(
        audio, 
        min_silence_len=lunghezza_pausa_ms, 
        silence_thresh=soglia_silenzio_db
    )
    
    # Calcoliamo le posizioni medie delle pause tra i segmenti di parlato.
    # Ogni pausa si trova tra la fine di un segmento di parlato e l'inizio del successivo.
    posizioni_pause_medie = []
    for i in range(len(segmenti_parlato) - 1):
        fine_parlato_corrente = segmenti_parlato[i][1]
        inizio_parlato_successivo = segmenti_parlato[i + 1][0]
        posizione_media_pausa = (fine_parlato_corrente + inizio_parlato_successivo) / 2
        posizioni_pause_medie.append(posizione_media_pausa)
    
    return posizioni_pause_medie

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Navigatore di Pause Audio')

def play_segments(audio, segmenti, indice_corrente):
    global current_playback

    durata_totale = 0
    segmento_composto = AudioSegment.silent(duration=0)
    
    while durata_totale < 1000 and indice_corrente < len(segmenti):
        start_ms, end_ms = segmenti[indice_corrente]
        durata_totale += (end_ms - start_ms)
        segmento_composto += audio[start_ms:end_ms]
        indice_corrente += 1

    # Se c'è una riproduzione in corso, fermala
    if current_playback is not None:
        current_playback.stop()


    current_playback = play_audio(segmento_composto)
    return indice_corrente - 1

# Definisce le funzioni per la navigazione
def vai_indietro(audio, segmenti, indice_corrente):
    indice_corrente = max(indice_corrente - 1, 0)
    indice_corrente = play_segments(audio, segmenti, indice_corrente)
    start_ms = segmenti[indice_corrente][0]
    print(f"Chunk attuale in riproduzione: {ms_to_min_sec(start_ms)}")
    return indice_corrente

def vai_avanti(audio, segmenti, indice_corrente):
    indice_corrente = min(indice_corrente + 1, len(segmenti) - 1)
    indice_corrente = play_segments(audio, segmenti, indice_corrente)
    start_ms = segmenti[indice_corrente][0]
    print(f"Chunk attuale in riproduzione: {ms_to_min_sec(start_ms)}")
    return indice_corrente

def ripeti(audio, segmenti, indice_corrente):
    indice_corrente = play_segments(audio, segmenti, indice_corrente)
    start_ms = segmenti[indice_corrente][0]
    print(f"Chunk attuale in riproduzione: {ms_to_min_sec(start_ms)}")
    return indice_corrente

def main(file_mp3):
    posizioni_pause_medie = trova_posizioni_pause(file_mp3)
    audio = AudioSegment.from_mp3(file_mp3)
    
    if not posizioni_pause_medie:
        print("Nessuna pausa trovata.")
        return
    
    # Aggiunge un segmento che inizia da 0
    segmenti = [(0, posizioni_pause_medie[0])]
    segmenti += [(posizioni_pause_medie[i], posizioni_pause_medie[i + 1]) for i in range(len(posizioni_pause_medie) - 1)]

    init_pygame()
    running = True
    indice_corrente = 0

    ##### Crea un'istanza di Porcupine ###########################
    access_key = "yM+BHv0MHDNu+OVSJdARsO74pcRN3DAm4FHSLf1ZgC3q1g+IQZgJgg=="
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


    while running:
        # comandi porcupine
        audio_frame = audio_stream.read(porcupine.frame_length)
        audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_frame)

        # Usa Porcupine per analizzare il frame audio
        keyword_index = porcupine.process(audio_frame)

        if keyword_index == 0:
            indice_corrente = ripeti(audio, segmenti, indice_corrente)
        elif keyword_index == 1:
            indice_corrente = vai_avanti(audio, segmenti, indice_corrente)
        elif keyword_index == 2:
            indice_corrente = vai_indietro(audio, segmenti, indice_corrente)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    indice_corrente = vai_indietro(audio, segmenti, indice_corrente)
                elif event.key == pygame.K_RIGHT:
                    indice_corrente = vai_avanti(audio, segmenti, indice_corrente)
                elif event.key == pygame.K_UP:
                    indice_corrente = ripeti(audio, segmenti, indice_corrente)
    
    pygame.quit()

if __name__ == "__main__":
    file_mp3 = "005-Learn English Through Stories The Neighborhood Picnic  Listen and Speak English.mp3"
    main(file_mp3)
