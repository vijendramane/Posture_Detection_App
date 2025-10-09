from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np 
import base64  
import json  
import io  
from PIL import Image 
import time
from typing import Dict, List
import asyncio
 

from posture_detector import PostureDetector


app = FastAPI(title="Posture Detection API", version="1.0.0")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize posture detector
detector = PostureDetector()

# Store active WebSocket connections
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Posture Detection API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode base64 image string to numpy array"""
    try:
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

@app.post("/analyze-frame")
async def analyze_frame(
    image_data: str,
    posture_type: str = "sitting"
):
    """Analyze a single frame for posture detection"""
    try:
        # Decode the image
        image = decode_base64_image(image_data)
        
        # Analyze posture
        result = detector.analyze_posture(image, posture_type)
        
        # Add timestamp
        result['timestamp'] = time.time()
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-video")
async def analyze_video(
    file: UploadFile = File(...),
    posture_type: str = "sitting"
):
    """Analyze uploaded video for posture detection"""
    try:
        # Read video file
        video_bytes = await file.read()
        
        # Save temporarily
        temp_video_path = f"temp_video_{int(time.time())}.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_bytes)
        
        # Open video
        cap = cv2.VideoCapture(temp_video_path)
        
        results = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Analyze every 5th frame to reduce processing time
            if frame_count % 5 == 0:
                result = detector.analyze_posture(frame, posture_type)
                result['frame_number'] = frame_count
                result['timestamp'] = frame_count / cap.get(cv2.CAP_PROP_FPS)
                results.append(result)
            
            frame_count += 1
        
        cap.release()
        
        # Clean up temporary file
        import os
        os.remove(temp_video_path)
        
        # Calculate summary statistics
        total_frames = len(results)
        good_posture_frames = sum(1 for r in results if r.get('analysis', {}).get('is_good_posture', False))
        
        summary = {
            'total_frames_analyzed': total_frames,
            'good_posture_frames': good_posture_frames,
            'bad_posture_frames': total_frames - good_posture_frames,
            'posture_score': (good_posture_frames / total_frames * 100) if total_frames > 0 else 0,
            'posture_type': posture_type
        }
        
        return JSONResponse(content={
            'summary': summary,
            'frame_results': results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time posture analysis"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'frame':
                try:
                    # Decode and analyze frame
                    image = decode_base64_image(message['image'])
                    posture_type = message.get('posture_type', 'sitting')
                    
                    result = detector.analyze_posture(image, posture_type)
                    result['timestamp'] = time.time()
                    
                    # Send result back
                    await manager.send_personal_message(
                        json.dumps({'type': 'analysis', 'data': result}),
                        websocket
                    )
                    
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({'type': 'error', 'message': str(e)}),
                        websocket
                    )
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/export-analysis")
async def export_analysis(analysis_data: Dict):
    """Export analysis results to JSON/CSV format"""
    try:
        # For now, just return the data as JSON
        # In a real implementation, you might save to file or database
        return JSONResponse(content={
            'export_format': 'json',
            'data': analysis_data,
            'exported_at': time.time()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
