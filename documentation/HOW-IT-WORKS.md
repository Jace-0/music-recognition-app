# How The Music Recognition System Works

Music recognition app works by creating and comparing "audio fingerprints" - compact digital summaries of audio that capture the distinctive characteristics of a song. Here's the step-by-step process:

## Step 1

### Audio Sampling and Conversion

When you tap "Record," the web app records a short audio clip (usually 10-15 seconds) using your device's microphone. This raw audio is converted from an analog sound wave into a digital signal through:

    Sampling: The continuous audio wave is measured at regular intervals (typically 44,100 times per second)
    Quantization: Each sample is represented as a numerical value
    Conversion: The resulting stream of numbers represents the audio's amplitude over time (the waveform)

## Step 2

### Spectrogram Creation

The digital audio is then transformed from the time domain into the frequency domain using a mathematical technique called the Fast Fourier Transform (FFT):

The audio is divided into short overlapping segments (typically 10-40 milliseconds)
Each segment is analyzed to determine which frequencies are present and at what intensities.

The result is a spectrogram - a time-frequency representation showing how the audio's frequency content changes over time

## Step 3

### Peak Extraction and Constellation Map

The spectrogram is analyzed to identify "peak points" - the strongest energy points where certain frequencies are particularly prominent
These peaks represent frequencies that stand out and are likely to survive even in noisy environments

Only these peaks are kept, discarding most of the spectrogram data
The resulting sparse set of time-frequency points forms what's called a "constellation map" - like stars in a night sky

This approach was revolutionary because:

    It drastically reduces the amount of data needed
    The peaks tend to survive background noise, making recognition robust
    It creates a highly distinctive fingerprint specific to each song

## Step 4

### Creating Hash Tokens

To make searching efficient:

Each peak point is paired with several nearby peaks to create "hash tokens"
A typical hash token contains:

    The frequency of the anchor peak
    The frequency of the target peak
    The time difference between them
    An absolute time offset from the beginning of the song

These hash tokens serve as the actual fingerprints that will be used for matching.

## Step 5

### Database Matching

    When you record a song snippet
    The app generates hash tokens from your audio sample
    These tokens are sent to the server
    The server looks up each token in its database of pre-computed song fingerprints
    For each matching token, it records the song ID and the time offset in that song
    It then looks for clusters of matches from the same song with consistent time offsets
    Songs with many matching tokens in the correct time sequence become candidates

## Step 6

### Verification and Ranking

To determine the final match:

Candidate songs are ranked by the number and quality of matching tokens
The system checks for consistent time alignment between the sample and original recording
Statistical confidence scores are calculated

The highest-scoring match is returned as the result

See [Algorithm Detailed Explanation](fingerprint-Algorithm.md)

See [Audio Fingerprinting Visualization](Audio-Fingerprinting.ipynb)
