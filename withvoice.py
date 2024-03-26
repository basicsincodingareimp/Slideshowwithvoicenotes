import tkinter as tk
from tkinter import filedialog
from itertools import cycle
import pyaudio
import wave
import threading

class ImageSlideshow:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Slideshow")
        self.image_paths = []
        self.current_image_label = tk.Label(master)
        self.current_image_label.pack(padx=10, pady=10)
        self.current_image = None
        self.current_image_index = 0

        self.load_button = tk.Button(master, text="Load Images", command=self.load_images)
        self.load_button.pack(pady=5)

        self.start_button = tk.Button(master, text="Start Slideshow", command=self.start_slideshow, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.num_images_label = tk.Label(master, text="No images selected")
        self.num_images_label.pack(pady=5)

        self.record_button = tk.Button(master, text="Record Voice Note", command=self.record_voice_note)
        self.record_button.pack(pady=5)

        self.user_text_entry = tk.Entry(master)
        self.user_text_entry.pack(pady=5)

        self.audio_filename = "recorded_audio.wav"
        self.audio_thread = None

    def load_images(self):
        self.image_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if self.image_paths:
            self.current_image_index = 0
            self.update_num_images_label()

    def update_num_images_label(self):
        num_images = len(self.image_paths)
        self.num_images_label.config(text=f"{num_images} images selected")
        self.start_button.config(state=tk.NORMAL if num_images > 0 else tk.DISABLED)

    def start_slideshow(self):
        if not self.image_paths:
            return
        self.start_button.config(state=tk.DISABLED)
        self.current_image = cycle(self.image_paths)
        self.show_next_image()

    def show_next_image(self):
        image_path = next(self.current_image)
        image = tk.PhotoImage(file=image_path)
        self.current_image_label.config(image=image)
        self.current_image_label.image = image
        self.current_image_index += 1
        self.update_num_images_label()

        if self.current_image_index == len(self.image_paths):
            user_text = self.user_text_entry.get()  # Get user's entered text
            self.current_image_label.config(text=user_text, font=("Arial", 16), fg="blue")
            self.current_image_label.place(relx=0.5, rely=0.5, anchor="center")
            self.start_button.config(state=tk.NORMAL)

            self.audio_thread = threading.Thread(target=self.play_voice_note)
            self.audio_thread.start()
        else:
            self.master.after(1000, self.show_next_image)

    def record_voice_note(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 30  # Record for 30 seconds

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        print("Recording...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Finished recording.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def play_voice_note(self):
        try:
            wf = wave.open(self.audio_filename, 'rb')
            audio = pyaudio.PyAudio()
            stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                                rate=wf.getframerate(), output=True)
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception as e:
            print("Error playing audio:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSlideshow(root)
    root.mainloop()
