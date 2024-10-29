// Initialize the video stream
async function startVideo() {
    const video = document.getElementById('video');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing webcam: ", err);
    }
}

// Load face-api.js models from the static/models directory
async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');  // Model for face detection
    await faceapi.nets.faceLandmark68Net.loadFromUri('/static/models');  // Model for facial landmarks
    await faceapi.nets.faceRecognitionNet.loadFromUri('/static/models');  // Model for face recognition

    startVideo();
}

// Detect faces and draw bounding boxes or landmarks
async function detectFaces() {
    const video = document.getElementById('video');
    const canvas = faceapi.createCanvasFromMedia(video);
    document.body.append(canvas);

    const displaySize = { width: video.width, height: video.height };
    faceapi.matchDimensions(canvas, displaySize);

    // Continuously detect faces
    setInterval(async () => {
        const detections = await faceapi.detectAllFaces(
            video, 
            new faceapi.TinyFaceDetectorOptions()
        ).withFaceLandmarks().withFaceDescriptors();

        // Clear the canvas before drawing new detections
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

        // Resize the detections to match the video size
        const resizedDetections = faceapi.resizeResults(detections, displaySize);

        // Draw the detected faces and landmarks on the canvas
        faceapi.draw.drawDetections(canvas, resizedDetections);
        faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
    }, 100);
}

// Event listener for when the video is playing
document.getElementById('video').addEventListener('play', () => {
    detectFaces();
});

// Load the models and start video when the page is ready
window.addEventListener('load', async () => {
    await loadModels();
});
