import React, { useState, useEffect } from 'react';
import { uploadVideo, getVideos, getVideoDetections } from '../api/api';
import { useWebSocket } from '../hooks/useWebSocket';
import VideoPlayer from '../components/VideoPlayer';
import { Video, Detection } from '../types';

const Dashboard: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const { isConnected, message } = useWebSocket(selectedVideo?.id ?? null);

  useEffect(() => {
    fetchVideos();
  }, []);

  useEffect(() => {
    if (message && selectedVideo && message.video_id === selectedVideo.id) {
      const newDetection = {
        frame_number: message.frame_number,
        timestamp: message.frame_number / 30,
        object_count: message.object_count,
        bounding_boxes: []
      };

      setDetections(prev => {
        const existingIndex = prev.findIndex(d => d.frame_number === newDetection.frame_number);
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = newDetection;
          return updated;
        } else {
          return [...prev, newDetection];
        }
      });
    }
  }, [message, selectedVideo]);

  const fetchVideos = async () => {
    try {
      const data = await getVideos();
      setVideos(data);
    } catch (error) {
      setError('Failed to fetch videos');
      console.error(error);
    }
  };

  const handleSelectVideo = async (video: Video) => {
    setSelectedVideo(video);

    try {
      await fetch(`http://localhost:8000/api/videos/${video.id}/stream`, {
        method: 'GET',
      });

      const data = await getVideoDetections(video.id);
      setDetections(data.detections);
    } catch (error) {
      setError('Failed to fetch video stream or detections');
      console.error(error);
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const data = await uploadVideo(file);
      setUploadProgress(100);

      const newVideo = {
        id: data.id,
        filename: data.filename,
        processed: 1,
        upload_date: new Date().toISOString()
      };

      setVideos(prev => [...prev, newVideo]);
      setSelectedVideo(newVideo);
      setDetections([]);

      setTimeout(fetchVideos, 1000);
    } catch (error) {
      setError('Failed to upload video');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Video Detection Dashboard</h1>

      {/* Upload Section */}
      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-4">Upload Video</h2>
        <div className="flex items-center">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            disabled={isUploading}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100 cursor-pointer"
          />
          {isUploading && (
            <div className="ml-4">
              <div className="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video List */}
        <div className="lg:col-span-1">
          <h2 className="text-xl font-semibold mb-4">Videos</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <ul className="divide-y divide-gray-200">
              {videos.length === 0 ? (
                <li className="p-4 text-gray-500">No videos uploaded</li>
              ) : (
                videos.map(video => (
                  <li
                    key={video.id}
                    className={`p-4 transition-all transform duration-200 hover:scale-[1.01] hover:bg-blue-50 active:scale-[0.98] ${
                      selectedVideo?.id === video.id ? 'bg-blue-100 font-semibold' : ''
                    } cursor-pointer`}
                    onClick={() => handleSelectVideo(video)}
                  >
                    <div className="flex justify-between">
                      <span className="font-medium">{video.filename}</span>
                      <span className="text-sm text-gray-500">
                        {video.processed === 0 && 'Not Processed'}
                        {video.processed === 1 && 'Processing...'}
                        {video.processed === 2 && 'Processed'}
                        {video.processed === 3 && 'Error'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(video.upload_date).toLocaleString()}
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>

        {/* Video Player and Detections */}
        <div className="lg:col-span-2">
          {selectedVideo ? (
            <>
              <h2 className="text-xl font-semibold mb-4">
                {selectedVideo.filename}
                {isConnected && (
                  <span className="ml-2 text-sm text-green-500">
                    (Live updates enabled)
                  </span>
                )}
              </h2>

              <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
                <VideoPlayer
                  videoUrl={`http://localhost:8000/api/videos/${selectedVideo.id}/stream`}
                  detections={detections}
                />
              </div>

              <div className="bg-white rounded-lg shadow overflow-hidden">
                <h3 className="text-lg font-medium p-4 border-b">
                  Detection Results
                  <span className="ml-2 text-sm text-gray-500">
                    ({detections.length} frames with detections)
                  </span>
                </h3>

                <div className="overflow-x-auto" style={{ maxHeight: '400px' }}>
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Frame #
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Timestamp
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          People Count
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Details
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {detections.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                            {selectedVideo.processed === 1
                              ? 'Video is being processed...'
                              : 'No detections found'}
                          </td>
                        </tr>
                      ) : (
                        detections.map((detection) => (
                          <tr key={detection.frame_number}>
                            <td className="px-6 py-4 whitespace-nowrap">{detection.frame_number}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {detection.timestamp.toFixed(2)}s
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">{detection.object_count}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {detection.bounding_boxes.length > 0 && (
                                <button
                                  className="text-blue-600 hover:text-blue-800"
                                  onClick={() => {
                                    const videoEl = document.querySelector('video');
                                    if (videoEl) {
                                      videoEl.currentTime = detection.timestamp;
                                      videoEl.play();
                                      setTimeout(() => videoEl.pause(), 100);
                                    }
                                  }}
                                >
                                  View
                                </button>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
              Select a video from the list or upload a new one
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
