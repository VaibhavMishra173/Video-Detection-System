export interface Video {
  id: number;
  filename: string;
  upload_date: string;
  processed: number; // 0: Not processed, 1: Processing, 2: Completed, 3: Error
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

export interface Detection {
  frame_number: number;
  timestamp: number;
  object_count: number;
  bounding_boxes: BoundingBox[];
}