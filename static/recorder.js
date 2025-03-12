document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const recordButton = document.getElementById('recordButton');
    const resultContainer = document.querySelector('.result-container');
    
    // Variables for recording
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let signalAnimation;

    // Audio context variables
    let audioContext;
    let analyser;
    let source;
    let animationFrame;
        
    // Initialize audio recording
    const initializeRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create audio context and analyser
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            
            // Configure media recorder
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                stopSignalAnimation();
                stopVisualization();
                
                // Create audio blob from recorded chunks
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                // Simulate recognition
                resultContainer.innerHTML = '<h3>Processing...</h3>';
                
                try {
                    const formData = new FormData();
                    formData.append('audio_file', audioBlob, 'recording.webm');
                    
                    const response = await fetch('/recognize', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.recognized) {
                        resultContainer.innerHTML = `
                            <h3>Song Found!</h3>
                            <p>Title: ${result.song_name}</p>
                            <p>Artist: ${result.artist}</p>
                            <p>Confidence: ${result.confidence}%</p>
                        `;
                    } else {
                        resultContainer.innerHTML = `
                            <h3>No Match Found</h3>
                            <p>Try recording again or add this song to the database.</p>
                        `;
                    }
                } catch (error) {
                    resultContainer.innerHTML = `
                        <h3>Error</h3>
                        <p>Failed to recognize song. Please try again.</p>
                    `;
                }
                resultContainer.classList.add('active');
            };
            
            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            resultContainer.innerHTML = `
                <h3>Error</h3>
                <p>Could not access microphone. Please ensure microphone permissions are granted.</p>
            `;
            resultContainer.classList.add('active');
            return false;
        }
    };

    // Visualize audio
    const startVisualization = () => {
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            animationFrame = requestAnimationFrame(draw);
            
            analyser.getByteFrequencyData(dataArray);
            
            // Use the frequency data to modify the button's glow effect
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            const intensity = Math.min(100, average * 2);
            recordButton.style.boxShadow = `0 0 ${intensity}px rgba(0, 136, 255, 0.8)`;
        };
        
        draw();
    };
    
    const stopVisualization = () => {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
        recordButton.style.boxShadow = '0 0 30px rgba(0, 136, 255, 0.5)';
    };
    
    // Start recording
    const startRecording = () => {
        isRecording = true;
        audioChunks = [];
        resultContainer.classList.remove('active');
        
        // Show listening message
        resultContainer.innerHTML = `
            
            <h3><i class="fa-solid fa-headphones-simple"></i> Listening for music</h3>
            <p>Make sure your device can hear the song clearly</p>
        `;

        resultContainer.classList.add('active');
        
        startSignalAnimation();
        startVisualization();
        mediaRecorder.start();
        
        // Auto-stop after 15 seconds
        setTimeout(() => {
            if (isRecording) {
                stopRecording();
            }
        }, 15000);
    };

    // Animation and recording control functions (unchanged)
    const startSignalAnimation = () => {
        let scale = 1;
        let growing = true;
        
        signalAnimation = setInterval(() => {
            if (growing) {
                scale += 0.1;
                if (scale >= 1.2) growing = false;
            } else {
                scale -= 0.1;
                if (scale <= 0.8) growing = true;
            }
            recordButton.style.transform = `scale(${scale})`;
        }, 100);
    };

    const stopSignalAnimation = () => {
        clearInterval(signalAnimation);
        recordButton.style.transform = 'scale(1)';
    };

    const stopRecording = () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            isRecording = false;
            mediaRecorder.stop();
            stopSignalAnimation();
            stopVisualization();
        }
    };


     // Handle record button click
     recordButton.addEventListener('click', async () => {
        if (!mediaRecorder) {
            const initialized = await initializeRecording();
            if (initialized) {
                startRecording();
            }
        } else if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

});