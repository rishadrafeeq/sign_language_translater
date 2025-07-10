import os
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Directory where the audio files are saved
output_dir = "alphabets"

# Function to play a sound file
def play_audio(letter):
    file_path = os.path.join(output_dir, f"{letter}.mp3")
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Example: Play the audio for letter A
play_audio('A')
