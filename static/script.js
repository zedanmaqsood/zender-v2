const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = document.getElementById('progressBar');
const uploadStatus = document.getElementById('uploadStatus');

// Only add upload-related event listeners if we're in a directory (upload container exists)
if (dropZone) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    dropZone.classList.add('drag-over');
}

function unhighlight(e) {
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files } });
}

function handleFiles(e) {
    const files = [...e.target.files];
    if (files.length === 0) return;

    uploadFiles(files);
}

async function uploadFiles(files) {
    uploadProgress.style.display = 'block';
    progressBar.style.width = '0%';
    uploadStatus.textContent = 'Uploading...';

    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    // Add current directory to the form data
    const currentDir = window.location.pathname.substring(1); // Remove leading slash
    formData.append('current_dir', currentDir);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            progressBar.style.width = '100%';
            uploadStatus.textContent = 'Upload complete!';
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        progressBar.style.width = '0%';
        uploadStatus.textContent = error.message || 'Upload failed. Please try again.';
        console.error('Upload error:', error);
    }
}