import cv2
import mediapipe as mp
import joblib
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
import pygame
import time
import pyttsx3
import sys

# Initialize pygame mixer
pygame.mixer.init()

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Load the pre-trained SVM model
clf = joblib.load('svm_model.pkl')

# Path to the folder containing pre-generated audio files
audio_folder = "alphabets"

# Variables for word formation
last_predicted_letter = None
current_word = ""
last_letter_time = 0
letter_hold_time = 0.5  # seconds to hold a letter to lock it
word_pause_time = 2.0  # seconds of no new letters to read the word
last_word_update_time = 0
is_speaking = False
speech_cooldown = 3.0  # seconds to wait before allowing next speech
last_speech_time = 0

def data_clean(landmark):
    data = landmark[0]
    try:
        data = str(data)
        data = data.strip().split('\n')
        garbage = ['landmark {', '  visibility: 0.0', '  presence: 0.0', '}']
        without_garbage = [i for i in data if i not in garbage]

        clean = [i.strip()[2:] for i in without_garbage]
        finalClean = [float(clean[i]) for i in range(0, len(clean)) if (i + 1) % 3 != 0]

        return [finalClean]

    except:
        return np.zeros([1, 63], dtype=int)[0]

def play_audio(letter):
    global last_predicted_letter
    if letter != last_predicted_letter:
        file_path = os.path.join(audio_folder, f"{letter}.mp3")
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        last_predicted_letter = letter

def speak_word(word):
    global is_speaking, last_speech_time
    current_time = time.time()
    if word and not is_speaking and (current_time - last_speech_time) >= speech_cooldown:
        is_speaking = True
        engine.say(word)
        engine.runAndWait()
        is_speaking = False
        last_speech_time = current_time

def reset_word():
    global current_word, last_predicted_letter, last_letter_time, last_word_update_time, is_speaking, last_speech_time
    current_word = ""
    last_predicted_letter = None
    last_letter_time = 0
    last_word_update_time = 0
    is_speaking = False
    last_speech_time = 0

def predict_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        cleaned_landmark = data_clean(results.multi_hand_landmarks)
        if cleaned_landmark:
            y_pred = clf.predict(cleaned_landmark)
            letter = y_pred[0]
            QMessageBox.information(None, "Prediction", f"The predicted letter is: {letter}")
    else:
        QMessageBox.information(None, "Prediction", "No hand detected in the image.")

def upload_image():
    file_path, _ = QFileDialog.getOpenFileName(None, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
    if file_path:
        predict_image(file_path)

def predict_real_time():
    global last_predicted_letter, current_word, last_letter_time, last_word_update_time, is_speaking, last_speech_time
    last_predicted_letter = None
    current_word = ""
    last_letter_time = 0
    last_word_update_time = 0
    is_speaking = False
    last_speech_time = 0
    
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_time = time.time()
        letter_detected = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cleaned_landmark = data_clean(results.multi_hand_landmarks)
            if cleaned_landmark:
                y_pred = clf.predict(cleaned_landmark)
                letter = y_pred[0]
                letter_detected = True

                # Check if the same letter is being held
                if letter == last_predicted_letter:
                    if current_time - last_letter_time >= letter_hold_time:
                        # Lock the letter and add it to the word
                        current_word += letter
                        last_letter_time = current_time
                        last_word_update_time = current_time
                else:
                    last_predicted_letter = letter
                    last_letter_time = current_time

        else:
            last_predicted_letter = None
            last_letter_time = 0

        # Check if enough time has passed to read the word
        if current_word and current_time - last_word_update_time >= word_pause_time and not is_speaking:
            speak_word(current_word)
            last_word_update_time = current_time  # Reset the timer after reading

        # Display current letter and word
        if letter_detected:
            image = cv2.putText(image, f"Current: {last_predicted_letter}", (50, 100), 
                              cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        
        image = cv2.putText(image, f"Word: {current_word}", (50, 200), 
                          cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Real-Time Prediction', image)

        if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Gesture Prediction")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons with improved visibility
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        
        upload_image_btn = QPushButton("Upload Image")
        upload_image_btn.setFixedSize(200, 50)
        upload_image_btn.clicked.connect(upload_image)
        upload_image_btn.setStyleSheet(button_style)
        
        real_time_btn = QPushButton("Predict in Real-Time")
        real_time_btn.setFixedSize(200, 50)
        real_time_btn.clicked.connect(predict_real_time)
        real_time_btn.setStyleSheet(button_style)
        
        reset_btn = QPushButton("Reset Word")
        reset_btn.setFixedSize(200, 50)
        reset_btn.clicked.connect(reset_word)
        reset_btn.setStyleSheet(button_style)
        
        # Add buttons to layout
        layout.addWidget(upload_image_btn, alignment=Qt.AlignCenter)
        layout.addWidget(real_time_btn, alignment=Qt.AlignCenter)
        layout.addWidget(reset_btn, alignment=Qt.AlignCenter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
