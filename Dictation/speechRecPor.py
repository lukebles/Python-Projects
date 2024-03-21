import pvporcupine
import pyaudio
import struct

# Sostituisci questo con il tuo access key ottenuto da Picovoice
access_key = "yM+BHv0MHDNu+OVSJdARsO74pcRN3DAm4FHSLf1ZgC3q1g+IQZgJgg=="

# Inizializza PyAudio
pa = pyaudio.PyAudio()

try:
    # Crea un'istanza di Porcupine con i comandi desiderati e l'access_key
    porcupine = pvporcupine.create(access_key=access_key, keywords=["grapefruit", "americano", "terminator"])

    # Apre un flusso audio con PyAudio
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Dì 'grapefruit', 'americano', o 'terminator'...")
    while True:
        # Legge il frame audio
        audio_frame = audio_stream.read(porcupine.frame_length)
        audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_frame)

        # Usa Porcupine per analizzare il frame audio
        keyword_index = porcupine.process(audio_frame)

        if keyword_index == 0:
            print("Rilevato 'grapefruit'!")
        elif keyword_index == 1:
            print("Rilevato 'americano'!")
        elif keyword_index == 2:
            print("Rilevato 'terminator'!")
finally:
    # Chiude il flusso audio e rilascia le risorse
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
