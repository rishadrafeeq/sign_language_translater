import os
from gtts import gTTS

# Directory to save the audio files
output_dir = "alphabets"

# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate voice clips for each letter from A to Z
for letter in range(ord('A'), ord('Z') + 1):
    text = f"The predicted letter is {chr(letter)}"
    
    # Convert the text to speech
    tts = gTTS(text=text, lang='en')
    
    # Save the audio file as mp3
    file_name = f"{chr(letter)}.mp3"
    tts.save(os.path.join(output_dir, file_name))

    print(f"Generated: {file_name}")

print("All voice clips have been generated and saved in the 'alphabets' folder.")
