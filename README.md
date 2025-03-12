# Music Recognition System with Python

A Shazam-like music recognition system that identifies songs from audio samples using audio fingerprinting technology.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

## Overview

This project implements an audio fingerprinting and recognition system similar to Shazam. It can identify songs from short audio clips, even in noisy environments or with low-quality recordings.

## Demo Video

Check out the demo video of the project below:

[Watch the demo video](https://drive.google.com/file/d/16PvMoYjZJ0HHA91cOk03xyn8eJv7zXEm/view?usp=drive_link)

### Key Features

- Fast and accurate music identification
- Robust against background noise and distortions
- Scalable database for storing song fingerprints
- Support for various audio formats

## How It Works

The system works by:

1. Creating unique audio fingerprints from songs
2. Storing these fingerprints in a database
3. Matching new audio samples against the database

For a detailed explanation of the technology:

- Read [How It Works](documentation/HOW-IT-WORKS.md)
- View [System Cons](documentation/System-Cons.md)
- See [Technology Stack](documentation/Tech-Stack.md)
- View [What i Learned](documentation/What-I-Learned.md)

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/Jace-0/music-recognition-app.git

# Create a virtual environment (optional but recommended)
python -m venv music_recognition_env
source music_recognition_env/bin/activate  # On Windows: music_recognition_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
