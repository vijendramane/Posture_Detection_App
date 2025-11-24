# Posture Detection App

A complete full-stack web application for rule-based bad posture detection using computer vision and pose estimation.

## Features

- **Real-time Posture Analysis**: Use webcam for live posture monitoring
- **Video Upload Analysis**: Upload videos for batch posture analysis
- **Posture Types**: Support for sitting and squat posture analysis  
- **Rule-based Detection**: Custom rules for detecting bad posture patterns 
- **Visual Feedback**: Real-time overlay with posture alerts 
- **Export Results**: Download analysis reports as JSON 
- **Responsive Design**: Works on desktop and mobile devices 
 -**Rule-based Detection**: Custom riles for detection bad posture analytics
-**Export Reult**: real time overlay with poture as JSON 
## Tech Stack 
 
### Backend
- **FastAPI** - Modern Python web framework
- **MediaPipe** - Google's pose estimation library
- **OpenCV** - Computer vision processing
- **WebSockets** - Real-time communication
- **Uvicorn** - Agsi servers

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe JavaScript
- **React Webcam** - Webcam integration
- **Axios** - HTTP client
- **WebSocket** - Real-time communication

## Posture Analysis Rules

### For Sitting Posture:
- **Neck Forward**: Flags if neck angle > 30°
- **Back Straightness**: Detects slouching based on shoulder-hip alignment
- **Shoulder Level**: Checks for balanced shoulder positioning

### For Squat Posture:
- **Knee Over Toe**: Flags if knee x-coordinate is ahead of toe
- **Back Angle**: Flags if back angle (shoulder-hip-knee) < 150° 
- **Squat Depth**: Checks if knee angle indicates sufficient depth

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

### REST Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `POST /analyze-frame` - Analyze single frame
- `POST /analyze-video` - Analyze uploaded video
- `POST /export-analysis` - Export analysis results

### WebSocket Endpoints
- `WS /ws` - Real-time frame analysis

## Usage

1. **Select Posture Type**: Choose between "Sitting" or "Squat" analysis
2. **Real-time Analysis**: 
   - Click "Start Analysis" to begin webcam monitoring
   - Position yourself in front of the camera
   - View real-time posture feedback
3. **Video Analysis**:
   - Upload a video file (MP4, AVI, MOV, WebM)
   - Wait for processing to complete
   - View detailed analysis results
4. **Export Results**: Click "Export Results" to download analysis data

## Project Structure

```
posture-detection-app/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── posture_detector.py     # Pose analysis logic
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── WebcamCapture.tsx  # Webcam integration
│   │   ├── VideoUpload.tsx    # Video upload component
│   │   ├── AnalysisResults.tsx # Results display
│   │   ├── api.ts             # API service
│   │   ├── types.ts           # TypeScript types
│   │   └── App.css            # Styles
│   ├── package.json           # Node.js dependencies
│   └── tsconfig.json          # TypeScript configuration
└── README.md                  # This file
```

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation at `http://localhost:8000/docs`
- MediaPipe processes video frames for pose estimation
- Rule-based logic checks posture against defined thresholds
- WebSocket support for real-time communication

### Frontend Development
- React with TypeScript for type safety
- Responsive design with CSS Grid and Flexbox
- Real-time updates via WebSocket connection
- File upload with progress tracking

## Customization

### Adding New Posture Rules
1. Open `backend/posture_detector.py`
2. Add new analysis functions (e.g., `analyze_standing_posture`)
3. Update the `analyze_posture` method to handle new types
4. Add corresponding UI options in the frontend

### Adjusting Thresholds
- Modify angle thresholds in posture analysis functions
- Update distance thresholds for alignment checks
- Fine-tune sensitivity based on your requirements

## Troubleshooting

### Common Issues

1. **Camera Access**: Ensure browser permissions for camera access
2. **WebSocket Connection**: Check that backend is running on port 8000
3. **CORS Issues**: Verify CORS settings in `main.py`
4. **MediaPipe Installation**: May require specific Python version compatibility

### Performance Optimization
- Adjust frame capture interval in `WebcamCapture.tsx`
- Modify video analysis frame sampling rate
- Consider using different MediaPipe model complexity settings

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue in the GitHub repository.
