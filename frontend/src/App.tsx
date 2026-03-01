import React, { useState } from 'react';
import './App.css';
import WebcamCapture from './WebcamCapture'; 
import VideoUpload from './VideoUpload';
import AnalysisResults from './AnalysisResults';    
import { AnalysisResult, VideoAnalysisResult } from './types'; 

const App: React.FC = () => { 
  const [postureType, setPostureType] = useState<'sitting' | 'squat'>('sitting');
  const [realtimeResult, setRealtimeResult] = useState<AnalysisResult | undefined>();
  const [videoResult, setVideoResult] = useState<VideoAnalysisResult | undefined>(); 

  const handlePostureTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPostureType(event.target.value as 'sitting' | 'squat');
  };

  const handleRealtimeResult = (result: AnalysisResult) => {
    setRealtimeResult(result);
  };

  const handleVideoResult = (result: VideoAnalysisResult) => {
    setVideoResult(result);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Posture Detection App</h1>
        <div className="posture-selector">
          <label htmlFor="posture-type">Select Posture Type: </label>
          <select id="posture-type" value={postureType} onChange={handlePostureTypeChange}>
            <option value="sitting">Sitting</option>
            <option value="squat">Squat</option>
          </select>
        </div>
      </header>
      <main className="app-main">
        <div className="capture-section">
          <WebcamCapture postureType={postureType} onAnalysisResult={handleRealtimeResult} />
          <VideoUpload postureType={postureType} onAnalysisResult={handleVideoResult} />
        </div>
        <AnalysisResults realtimeResult={realtimeResult} videoResult={videoResult} />
      </main>
    </div>
  );
};

export default App;
