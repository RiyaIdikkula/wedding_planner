// Load face-api.js models
async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('/static/models');
    await faceapi.nets.faceRecognitionNet.loadFromUri('/static/models');
}

// Start the video stream
async function startVideo() {
    const video = document.getElementById('video');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing webcam: ", err);
    }
}

// Detect face and landmarks in an image
async function detectFaceAndLandmarks(imageElement) {
    const detections = await faceapi.detectSingleFace(
        imageElement, 
        new faceapi.TinyFaceDetectorOptions()
    ).withFaceLandmarks();

    if (detections) {
        // Draw face detection box and landmarks
        const canvas = faceapi.createCanvasFromMedia(imageElement);
        document.body.append(canvas);

        faceapi.matchDimensions(canvas, imageElement);

        const resizedDetections = faceapi.resizeResults(detections, imageElement);
        faceapi.draw.drawDetections(canvas, resizedDetections);
        faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);

        return resizedDetections;  // Return detected landmarks
    } else {
        console.error("No face detected.");
    }
}

// When the image is loaded, run face detection
const imgElement = document.getElementById('sourceImage');
imgElement.addEventListener('load', async () => {
    await loadModels();
    const landmarks = await detectFaceAndLandmarks(imgElement);
    console.log(landmarks);  // Log the landmarks for further processing
});



// {
//     _positions: [
//         { x: ..., y: ... },  // Left eye
//         { x: ..., y: ... },  // Right eye
//         { x: ..., y: ... },  // Nose
//         { x: ..., y: ... },  // Mouth
//         ...
//     ]
// }


async function swapFace(sourceImage, targetCanvas, targetLandmarks) {
    const ctx = targetCanvas.getContext('2d');

    // Get the coordinates for the face (e.g., eyes, nose, etc.)
    const leftEye = targetLandmarks.landmarks.getLeftEye();
    const rightEye = targetLandmarks.landmarks.getRightEye();
    const nose = targetLandmarks.landmarks.getNose();
    const mouth = targetLandmarks.landmarks.getMouth();

    // Calculate the bounding box for the face using the landmarks
    const faceWidth = rightEye[0].x - leftEye[0].x;
    const faceHeight = mouth[0].y - nose[0].y;

    // Resize the source image to fit the face dimensions
    const resizedFace = await faceapi.resizeResults(sourceImage, { width: faceWidth, height: faceHeight });

    // Draw the swapped face on the target canvas at the location of the detected landmarks
    ctx.drawImage(resizedFace, leftEye[0].x, leftEye[0].y, faceWidth, faceHeight);
}

// Assuming you already have the source face, target canvas, and target landmarks
swapFace(sourceFaceImage, targetCanvas, targetLandmarks);

