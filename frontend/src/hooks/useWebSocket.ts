import { useState, useEffect, useCallback } from 'react';

interface WebSocketMessage {
  video_id: number;
  frame_number: number;
  object_count: number;
}

export const useWebSocket = (videoId: number | null) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [message, setMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    // Only connect if we have a videoId
    if (videoId === null) {
      return;
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/${videoId}`);

    ws.onopen = () => {
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(data)
        setMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
    };
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, [videoId]);

  const sendMessage = useCallback((data: object) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(data));
    }
  }, [socket, isConnected]);

  return { isConnected, message, sendMessage };
};