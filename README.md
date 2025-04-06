# Video Detection System

A web application that processes videos to detect people using YOLOv8, stores detection results in a database, and displays them in a React dashboard with real-time updates.

---

## Features

- Upload and process videos  
- Detect people using YOLOv8  
- Store detection results in PostgreSQL database  
- Real-time processing updates via WebSockets  
- Interactive dashboard to view detection results  
- Visualization of bounding boxes on video frames  

---

## Tech Stack

### Backend
- FastAPI  
- SQLAlchemy with PostgreSQL/SQLite  
- OpenCV  
- YOLOv8 with PyTorch  
- WebSockets for real-time updates  

### Frontend
- React with TypeScript  
- WebSockets for real-time updates  
- Tailwind CSS for styling  

### Deployment
- Docker & Docker Compose  

---

## Setup Instructions

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/video-detection-system.git
   cd video-detection-system
   ```

2. **Start the application using Docker Compose:**
   ```bash
   % docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)  
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Manual Setup

#### Backend

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

---

## API Endpoints

- `POST /api/upload`: Upload a video file for processing  
- `GET /api/videos`: Get a list of all uploaded videos  
- `GET /api/videos/{video_id}`: Get details of a specific video including detection results  
- `GET /api/videos/{video_id}/stream`: Stream the raw video file directly for playback in the frontend.
- `GET /api/ws/{video_id}`: Open a WebSocket connection to receive live updates about the processing progress of a specific video.

---

## Database Schema

- **videos**: Stores information about uploaded videos  
- **detections**: Stores frame-level detection results  
- **bounding_boxes**: Stores coordinates of detected objects  

---

## Security Considerations

- Input validation for file uploads  
- Proper error handling and logging  
- Database query parameterization to prevent SQL injection  
- CORS configuration to restrict API access  

---

## Scalability

- Background tasks for video processing to handle multiple requests  
- Database indexing for efficient queries  
- Dockerized deployment for easy scaling  

---

## Future Improvements

- Add authentication and user management  
- Support for different object detection models  
- Video compression for efficient storage  
- Integration with cloud storage for scalability  
- Batch processing for multiple videos
