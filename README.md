## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run `main.py`

## Usage

1. Launch the application
2. Choose between:
   - Real-time webcam prediction
   - Image upload prediction
3. For real-time mode:
   - Show hand gestures to the camera
   - Hold gesture for 0.5 seconds to lock letter
   - Pause for 2 seconds to hear the formed word
   - Use "Reset Word" button to clear current word

## Project Structure

- `main.py`: Main application with GUI
- `audio_play.py`: Audio playback functionality
- `svm_model.pkl`: Pre-trained classifier model
- `alphabets/`: Directory for letter audio files
