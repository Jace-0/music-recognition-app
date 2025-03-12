# Detailed Explanation of the Audio Fingerprinting Algorithm

This code creates an audio fingerprint from an audio file, which is a compact representation of the audio that can be used for music recognition.

Step by step breakdown

## Stage 1: Audio Loading and Preprocessing

```python
def create_fingerprint(audio_path, sr=11025):
    y, sr = librosa.load(audio_path, sr=sr)
```

- **Input**: Path to an audio file
- **Process**:
  - Loads the audio file using librosa
  - Converts to mono if stereo
  - Resamples to 11,025 Hz (lower than CD quality to reduce processing time)
- **Output**: `y` (audio time series as a numpy array) and `sr` (sample rate)

## Stage 2: Spectrogram Computation

```python
# Compute the spectrogram using Short-Time Fourier Transform (STFT)
S = np.abs(librosa.stft(y, n_fft=1024, hop_length=512))
```

- **Process**:
  - Applies Short-Time Fourier Transform to convert audio from time domain to frequency domain
  - `n_fft=1024`: Uses 1024-sample windows (~93ms at 11,025 Hz)
  - `hop_length=512`: Moves 512 samples (~46ms) between windows (50% overlap)
  - `np.abs()`: Takes the magnitude (ignores phase information)
- **Output**: `S` - a 2D array (spectrogram) where:
  - Rows represent frequencies (513 frequency bins for n_fft=1024)
  - Columns represent time frames
  - Values represent the magnitude of each frequency at each time

## Stage 3: Conversion to Decibels

```python
# Convert to log scale (dB) and normalize
S_db = librosa.amplitude_to_db(S, ref=np.max)
```

- **Process**:
  - Converts amplitude values to decibels (logarithmic scale)
  - Normalizes relative to the maximum value (`ref=np.max`)
  - This better represents how humans perceive sound (logarithmic, not linear)
- **Output**: `S_db` - spectrogram in decibels, with values typically ranging from -80dB to 0dB

## Stage 4: Peak Finding

```python
# Find local peaks in the spectrogram
neighborhood = generate_binary_structure(2, 1)
neighborhood = iterate_structure(neighborhood, 2)  # Smaller neighborhood

# Find local maxima
local_max = maximum_filter(S_db, footprint=neighborhood) == S_db
```

- **Process**:
  - Creates a pattern defining what "neighborhood" means (which surrounding points to compare)
  - `generate_binary_structure(2, 1)`: Creates a simple cross pattern
  - `iterate_structure(neighborhood, 2)`: Expands it to a larger pattern
  - `maximum_filter`: Replaces each point with the maximum value in its neighborhood
  - `== S_db`: Identifies points that are already the maximum in their neighborhood
- **Output**: `local_max` - a boolean array where `True` indicates a local peak

## Stage 5: Thresholding

```python
# Apply threshold to find significant peaks
threshold = np.median(S_db) + 15
peaks = np.logical_and(local_max, S_db > threshold)
```

- **Process**:
  - Filters out quieter sounds and keeps only the loudest, most important peaks
  - Calculates a threshold as 15dB above the median value
  - Combines two conditions with logical AND:
    1. Is this point a local maximum?
    2. Is this point louder than the threshold?
  - Only points satisfying both conditions are considered significant peaks
- **Output**: `peaks` - a boolean array where `True` indicates a significant peak

## Stage 6: Peak Extraction

```python
# Get the coordinates of peaks
peak_coords = np.where(peaks)
frequencies = peak_coords[0]
times = peak_coords[1]
```

- **Process**:
  - `np.where(peaks)` finds the coordinates of all `True` values
  - Separates the coordinates into frequency indices and time indices
- **Output**:
  - `frequencies` - array of row indices (frequency bins)
  - `times` - array of column indices (time frames)

## Stage 7: Dynamic Peak Selection Formula

This formula dynamically calculates how many peaks to keep based on the audio duration.

```python
# Get the coordinates of peaks
max_peaks = min(3000, max(300, int(duration * 50)))  # 50 peaks per second, up to 3000
```

The formula has three main components:

1. `int(duration * 50)`: This calculates 50 peaks for each second of audio

   - For a 5-second clip: 5 × 50 = 250 peaks
   - For a 2-minute song: 120 × 50 = 6,000 peaks

2. `max(300, int(duration * 50))`: This ensures we have at least 300 peaks, even for very short clips

   - For a 0.57-second clip: max(300, 0.57 × 50) = max(300, 28) = 300 peaks
   - For a 10-second clip: max(300, 10 × 50) = max(300, 500) = 500 peaks

3. `min(3000, max(300, int(duration * 50)))`: This caps the maximum number of peaks at 3,000
   - For a 2-minute song: min(3000, max(300, 6000)) = min(3000, 6000) = 3,000 peaks

## stage 8: Peak Limiting Code

```python

     # Limit number of peaks for faster processing
    if len(frequencies) > max_peaks:
        # Keep only the loudest peaks
        peak_values = S_db[peaks]
        top_indices = np.argsort(peak_values)[-max_peaks:]
        frequencies = frequencies[top_indices]
        times = times[top_indices]
```

It checks if we have more peaks than our calculated max_peaks limit.

**Example:**

- If we detected 250 peaks but `max_peaks` is 300, this condition is false and we skip the entire block

- If we detected 5000 peaks but `max_peaks` is 3000, this condition is true
  `peak_values = S_db[peaks]` Extracts actual decibel values of all the peaks we found.
  `top_indices = np.argsort(peak_values)[-max_peaks:]` finds the indices of the loudest peaks
  `frequencies = frequencies[top_indices]` filters the `frequencies` array to keep only the entries corresponding to the loudest peaks.
  `times = times[top_indices]` filters the `times` array to keep only the entries corresponding to the loudest peaks

## Stage 9: Create Fingerprint Hash Tokens

```python

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
    # print('max_fingerprints', max_fingerprints)
    if len(tokens) > max_fingerprints:
        tokens = random.sample(tokens, max_fingerprints)
        # print(f"Sampled down to {max_fingerprints} fingerprints")

    return tokens

```

This creates unique "fingerprint patterns" by connecting pairs of important sound points. It's like drawing constellations between stars in the night sky to create recognizable patterns.
