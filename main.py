import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.playback import play
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Constants
SAMPLE_RATE = 8000  # Hz
DURATION = 0.04  # 40ms for each character
CHAR_FREQUENCIES = {
    'a': (100, 1100, 2500), 'b': (100, 1100, 3000), 'c': (100, 1100, 3500),
    'd': (100, 1300, 2500), 'e': (100, 1300, 3000), 'f': (100, 1300, 3500),
    'g': (100, 1500, 2500), 'h': (100, 1500, 3000), 'i': (100, 1500, 3500),
    'j': (300, 1100, 2500), 'k': (300, 1100, 3000), 'l': (300, 1100, 3500),
    'm': (300, 1300, 2500), 'n': (300, 1300, 3000), 'o': (300, 1300, 3500),
    'p': (300, 1500, 2500), 'q': (300, 1500, 3000), 'r': (300, 1500, 3500),
    's': (500, 1100, 2500), 't': (500, 1100, 3000), 'u': (500, 1100, 3500),
    'v': (500, 1300, 2500), 'w': (500, 1300, 3000), 'x': (500, 1300, 3500),
    'y': (500, 1500, 2500), 'z': (500, 1500, 3000), ' ': (500, 1500, 3500)}

def play_audio(signal):
    try:
        formatted_signal = (signal * 32767 / np.max(np.abs(signal))).astype(np.int16)
        audio_segment = AudioSegment(
            formatted_signal.tobytes(),
            frame_rate=SAMPLE_RATE,
            sample_width=formatted_signal.dtype.itemsize,
            channels=1
        )
        play(audio_segment)
    except Exception as e:
        print(f"Error playing audio: {e}")

def save_audio(signal):
    file_path = filedialog.asksaveasfilename(defaultextension=".wav")
    if file_path:
        wav.write(file_path, SAMPLE_RATE, signal.astype(np.float32))

def generate_signal(character):
    if character not in CHAR_FREQUENCIES:
        raise ValueError(f"Character '{character}' not recognized")

    low, mid, high = CHAR_FREQUENCIES[character]
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    signal = (np.cos(2 * np.pi * low * t) + np.cos(2 * np.pi * mid * t) + np.cos(2 * np.pi * high * t))
    return signal

def apply_bandpass_filters(signal, sample_rate):
    # Implement your bandpass filters
    # For example, you can use scipy.signal.butter to design bandpass filters
    # Apply the filters to the input signal and return the result

    # This is a placeholder implementation, replace it with your own
    return signal

def bandpass_filters():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        sample_rate, signal = wav.read(file_path)
        filtered_signal = apply_bandpass_filters(signal, sample_rate)
        decoded_string = decode_fourier(filtered_signal, sample_rate, DURATION)
        decoded_text_field.delete(1.0, tk.END)
        decoded_text_field.insert(tk.END, decoded_string)
    else:
        messagebox.showinfo("Info", "No file selected")

def decode_and_display_fourier():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        sample_rate, signal = wav.read(file_path)
        decoded_string = decode_fourier(signal, sample_rate, DURATION)
        decoded_text_field.delete(1.0, tk.END)
        decoded_text_field.insert(tk.END, decoded_string)
    else:
        messagebox.showinfo("Info", "No file selected")

def generate_and_plot_signal():
    input_string = text_entry.get()
    generated_signal = np.concatenate([generate_signal(char) for char in input_string.lower()])

    # Open a new window for plotting the generated signal
    plot_window = tk.Toplevel(root)
    plot_window.title("Generated Signal Plot")

    # Create a figure and a set of subplots
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(generated_signal)
    ax.set_title("Generated Signal Plot")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")

    # Embed the plot into the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

def reset_gui():
    clear_widgets()
    tk.Button(root, text="Encode", command=select_encode, bg="gray", padx=10, pady=5, fg='white', width=15).pack()
    tk.Button(root, text="Decode (Fourier)", command=decode_and_display_fourier, bg="gray", padx=10, pady=5, fg='white', width=15).pack()
    tk.Button(root, text="Decode (Bandpass Filters)", command=bandpass_filters, bg="gray", padx=10, pady=5, fg='white', width=25).pack()

def select_encode():
    clear_widgets()
    text_entry.pack(pady=10)
    encode_button.pack(pady=5)
    generate_button.pack(pady=5)  # New button
    play_button.pack(pady=5)
    save_button.pack(pady=5)
    tk.Button(root, text="Back", command=reset_gui, bg="gray", padx=10, pady=5, fg='white', width=15).pack()

def clear_widgets():
    for widget in root.winfo_children():
        widget.pack_forget()

def encode_string(string):
    signals = [generate_signal(char) for char in string.lower()]
    encoded_signal = np.concatenate(signals)
    return encoded_signal

def encode_and_process():
    input_string = text_entry.get()
    encoded_signal = encode_string(input_string)
    play_button.config(state='normal', command=lambda: play_audio(encoded_signal))
    save_button.config(state='normal', command=lambda: save_audio(encoded_signal))

def decode_fourier(signal, sample_rate, duration):
    decoded_string = ''
    segment_length = int(duration * sample_rate)
    expected_freqs = set(f for char_freqs in CHAR_FREQUENCIES.values() for f in char_freqs)

    for i in range(0, len(signal), segment_length):
        segment = signal[i:i + segment_length]
        fft_result = np.fft.fft(segment)
        freqs = np.fft.fftfreq(len(segment), d=1/sample_rate)

        freq_magnitudes = np.abs(fft_result)
        top_frequencies = []
        for ef in expected_freqs:
            index = np.argmin(np.abs(freqs - ef))
            top_frequencies.append((freqs[index], freq_magnitudes[index]))

        top_frequencies.sort(key=lambda x: x[1], reverse=True)
        top_freq_values = [f[0] for f in top_frequencies[:3]]

        decoded_char = map_frequencies_to_char(top_freq_values)
        decoded_string += decoded_char

    return decoded_string

def map_frequencies_to_char(frequencies):
    tolerance = 100

    for char, char_freqs in CHAR_FREQUENCIES.items():
        match_count = sum(any(abs(cf - f) <= tolerance for cf in char_freqs) for f in frequencies)
        if match_count >= 3:
            return char

    return '?'

# GUI Setup
root = tk.Tk()
root.title("Voice-Frequency Encoder/Decoder")
root.configure(bg='#50a7f5')  # Set background color

encode_button = tk.Button(root, text="Encode", command=select_encode, bg="#323232", padx=10, pady=5, fg='white', width=15)
encode_button.pack(pady=10)
tk.Label(root, text=" " * 20, bg='#50a7f5').pack()  # Add some space between Logo and Encode buttons
decode_fourier_button = tk.Button(root, text="Decode (Fourier)", command=decode_and_display_fourier, bg="#323232", padx=10, pady=5, fg='white', width=25)
decode_fourier_button.pack(pady=10)
decode_bandpass_button = tk.Button(root, text="Decode (Bandpass Filters)", command=bandpass_filters, bg="#323232", padx=10, pady=5, fg='white', width=25)
decode_bandpass_button.pack(pady=10)

# Widgets for Encoding
text_entry = tk.Entry(root, width=50, bg="#c0c0c0", font=("Arial", 12))
encode_button = tk.Button(root, text="Encode", command=encode_and_process, bg="#323232", padx=10, pady=5, fg='white', width=15)
generate_button = tk.Button(root, text="Generate Signal", command=generate_and_plot_signal, bg="#323232", padx=10, pady=5, fg='white', width=15)  # New button
play_button = tk.Button(root, text="Play", state='disabled', bg="#323232", padx=10, pady=5, fg='white', width=15)
save_button = tk.Button(root, text="Save as WAV", state='disabled', bg="#323232", padx=10, pady=5, fg='white', width=15)

# Widgets for Decoding
decoded_text_field = tk.Text(root, height=5, width=50, bg="#c0c0c0", font=("Arial", 12))
decoded_text_field.pack(pady=10)

# Start the GUI loop
root.mainloop()
