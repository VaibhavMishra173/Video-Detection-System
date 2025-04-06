// API interaction functions
export const API_URL = 'http://localhost:8000/api';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const uploadVideo = async (file: File): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload video');
  }

  return response.json();
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const getVideos = async (): Promise<any[]> => {
  const response = await fetch(`${API_URL}/videos`);

  if (!response.ok) {
    throw new Error('Failed to fetch videos');
  }

  return response.json();
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const getVideoDetections = async (videoId: number): Promise<any> => {
  const response = await fetch(`${API_URL}/videos/${videoId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch video detections');
  }

  return response.json();
};