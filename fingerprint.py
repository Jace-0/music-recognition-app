import librosa
import numpy as np
from scipy.ndimage import maximum_filter
from scipy.ndimage import generate_binary_structure, iterate_structure
import random

def create_fingerprint(audio_path, sr=11025):
    y, sr = librosa.load(audio_path, sr=sr)

     # Get audio duration in seconds
    duration = librosa.get_duration(y=y, sr=sr)
    # print(f"Audio duration: {duration:.2f} seconds")

    # Compute the spectrogram using Short-Time Fourier Transform (STFT)
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=512))
    
    # Convert to log scale (dB) and normalize
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    # Find local peaks in the spectrogram
    neighborhood = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(neighborhood, 2)  # Smaller neighborhood

    # Find local maxima
    local_max = maximum_filter(S_db, footprint=neighborhood) == S_db


    # Apply threshold to find significant peaks
    threshold = np.median(S_db) + 15
    peaks = np.logical_and(local_max, S_db > threshold)
    
    # Get the coordinates of peaks
    peak_coords = np.where(peaks)
    frequencies = peak_coords[0]
    times = peak_coords[1]

    # Calculate number of peaks to keep based on duration
    # For longer songs, we want more peaks to ensure good coverage
    max_peaks = min(3000, max(300, int(duration * 50)))  # 50 peaks per second, up to 3000

     # Limit number of peaks for faster processing
    if len(frequencies) > max_peaks:
        # Keep only the loudest peaks
        peak_values = S_db[peaks]
        top_indices = np.argsort(peak_values)[-max_peaks:]
        frequencies = frequencies[top_indices]
        times = times[top_indices]
    
    # Create hash tokens from peaks
    # Each token connects an anchor point with points in its target zone
    tokens = []

    # Adjust target zone based on audio duration
    min_delta = 1
    max_delta = min(50, max(10, int(duration / 10)))  # Wider window for longer songs

    for i in range(len(frequencies)):
        # Define a target zone
        freq_anchor = frequencies[i]
        time_anchor = times[i]

         # Look for points in the target zone
        for j in range(i + 1, len(frequencies)):
            freq_target = frequencies[j]
            time_target = times[j]
            # Calculate how far apart in time these peaks are
            time_delta = time_target - time_anchor
            
            # Only consider points within an adaptive time window
            if min_delta <= time_delta <= max_delta:
                # Only create tokens if the frequency difference is significant
                freq_delta = abs(freq_target - freq_anchor)
                if freq_delta > 4:
                    # Create a hash token
                    token = (freq_anchor, freq_target, time_delta, time_anchor)
                    tokens.append(token)
    
    # If we still have too many fingerprints, sample them
    # Scale max fingerprints based on duration
    max_fingerprints = min(20000, max(5000, int(duration * 1000)))
    if len(tokens) > max_fingerprints:
        tokens = random.sample(tokens, max_fingerprints)

    return tokens