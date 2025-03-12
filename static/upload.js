document.addEventListener('DOMContentLoaded', () => {
    
    // DOM elements for recording functionality
    const recordButton = document.getElementById('recordButton');
    const resultContainer = document.querySelector('.result-container');
    
    // DOM elements for add song functionality
    const addSongForm = document.getElementById('addSongForm');
    const addStatusDiv = document.getElementById('addStatus');
    
    // Handle add song form submission
    if (addSongForm) {        
        addSongForm.addEventListener('submit', async function(event) {
            // Prevent the default form submission
            event.preventDefault();
            
            const songName = document.getElementById('songName').value;
            const artist = document.getElementById('artist').value;
            const songFileInput = document.getElementById('songFile');
            const songFile = songFileInput.files[0];
                        
            if (!songFile) {
                addStatusDiv.textContent = 'Please select an audio file.';
                return;
            }
            
            const formData = new FormData();
            formData.append('audio_file', songFile);
            formData.append('song_name', songName);
            formData.append('artist', artist);
            
            addStatusDiv.textContent = 'Adding song...';
            
            try {
                // Note: Using the correct endpoint with underscore
                const response = await fetch('/add_song', {
                    method: 'POST',
                    body: formData
                });
                                
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    addStatusDiv.textContent = 'Song added successfully!';
                    addSongForm.reset();
                } else {
                    addStatusDiv.textContent = `Error adding song: ${result.message || 'Unknown error'}`;
                }
            } catch (error) {
                console.error('Error adding song:', error);
                addStatusDiv.textContent = `Error adding song: ${error.message}. Please try again.`;
            }
        });
    } else {
        console.log('Add song form not found in the DOM');
    }
});