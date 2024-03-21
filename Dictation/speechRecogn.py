import speech_recognition as sr

def listen_for_commands():
    # Inizializza il riconoscitore
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say 'back', 'forward', or 'repeat'...")

        # Ascolta continuamente i comandi
        while True:
            try:
                # Ascolta per il primo pezzo di audio e tenta di riconoscerlo
                audio = r.listen(source)
                command = r.recognize_google(audio).lower()  # Utilizza Google Web Speech API
                print(f"Command recognized: {command}")

                # Esegui azioni in base al comando riconosciuto
                if command == "back":
                    print("Moving back...")
                elif command == "forward":
                    print("Moving forward...")
                elif command == "repeat":
                    print("Repeating...")
                else:
                    print("Command not recognized. Please try again.")
                    
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

# Avvia l'ascolto dei comandi vocali
listen_for_commands()
