import React, { useRef, useEffect, useState } from 'react';
import { Detection } from '../types';

interface VideoPlayerProps {
  videoUrl: string;
  detections: Detection[];
}

const FPS = 30;

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, detections }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [currentFrame, setCurrentFrame] = useState<number | null>(null);
  const [currentDetections, setCurrentDetections] = useState<Detection[]>([]);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);

  // Resize canvas to match video
  const resizeCanvas = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video && canvas) {
      canvas.width = video.clientWidth;
      canvas.height = video.clientHeight;
    }
  };

  // Update frame and detection
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const frame = Math.floor(video.currentTime * FPS);
      if (frame !== currentFrame) {
        setCurrentFrame(frame);
        const frameDetections = detections.filter(d => d.frame_number === frame);
        setCurrentDetections(frameDetections);
      }
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', resizeCanvas);
    window.addEventListener('resize', resizeCanvas);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', resizeCanvas);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [detections, currentFrame]);

  // Draw boxes
  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || !video.videoWidth || !video.videoHeight) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = video.clientWidth;
    canvas.height = video.clientHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!showBoxes) return;

    const scaleX = canvas.width / video.videoWidth;
    const scaleY = canvas.height / video.videoHeight;

    currentDetections.forEach(det => {
      det.bounding_boxes.forEach(box => {
        const x = box.x1 * scaleX;
        const y = box.y1 * scaleY;
        const width = (box.x2 - box.x1) * scaleX;
        const height = (box.y2 - box.y1) * scaleY;

        // Green stroke
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.9)';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);

        // Label with background
        const label = `${Math.round(box.confidence * 100)}%`;
        ctx.font = '13px Arial';
        ctx.fillStyle = 'rgba(0, 128, 0, 0.7)';
        const textWidth = ctx.measureText(label).width;
        const padding = 4;
        ctx.fillRect(x, y - 18, textWidth + padding * 2, 16);

        // Text on top
        ctx.fillStyle = 'white';
        ctx.fillText(label, x + padding, y - 5);
      });
    });
  }, [currentDetections, showBoxes]);

  return (
    <div className="relative w-full">
      {/* Toggle */}
      <div className="flex items-center gap-2 mb-2">
        <label htmlFor="toggle" className="text-sm font-medium text-gray-700">
          Show Detections
        </label>
        <button
          id="toggle"
          onClick={() => setShowBoxes(prev => !prev)}
          className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-300 
            ${showBoxes ? 'bg-green-500' : 'bg-gray-300'}`}
        >
          <div
            className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300
              ${showBoxes ? 'translate-x-6' : 'translate-x-0'}`}
          />
        </button>
      </div>

      {/* Video */}
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        className="w-full block"
        onLoadedMetadata={resizeCanvas}
      />

      {/* Canvas Overlay */}
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 pointer-events-none"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default VideoPlayer;
