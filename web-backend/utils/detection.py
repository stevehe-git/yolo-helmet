from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import base64
from io import BytesIO
from pathlib import Path
from config import Config

class DetectionService:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Config.MODELS_FOLDER / Config.DEFAULT_MODEL
            if not Path(model_path).exists():
                # Download default model if not exists
                model_path = Config.DEFAULT_MODEL
        
        self.model = YOLO(str(model_path))
        self.class_names = {0: 'with_helmet', 1: 'without_helmet'}
    
    def detect_image(self, image_path_or_array):
        """Detect helmets in an image"""
        results = self.model(image_path_or_array, conf=Config.CONFIDENCE_THRESHOLD, iou=Config.IOU_THRESHOLD)
        
        detections = []
        with_helmet = 0
        without_helmet = 0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
                
                class_name = self.class_names.get(cls, 'unknown')
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': bbox
                })
                
                if class_name == 'with_helmet':
                    with_helmet += 1
                elif class_name == 'without_helmet':
                    without_helmet += 1
        
        # Draw results on image
        annotated_image = self._draw_detections(image_path_or_array, detections)
        
        return {
            'image': annotated_image,
            'detections': detections,
            'stats': {
                'total': len(detections),
                'with_helmet': with_helmet,
                'without_helmet': without_helmet
            }
        }
    
    def _draw_detections(self, image_path_or_array, detections):
        """Draw bounding boxes on image"""
        if isinstance(image_path_or_array, (str, Path)):
            img = cv2.imread(str(image_path_or_array))
        else:
            img = image_path_or_array
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            color = (0, 255, 0) if det['class'] == 'with_helmet' else (255, 0, 0)
            
            cv2.rectangle(img_rgb, (x1, y1), (x2, y2), color, 2)
            label = f"{det['class']} {det['confidence']:.2f}"
            cv2.putText(img_rgb, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Convert to base64
        pil_img = Image.fromarray(img_rgb)
        buff = BytesIO()
        pil_img.save(buff, format='JPEG')
        img_str = base64.b64encode(buff.getvalue()).decode()
        
        return img_str
    
    def detect_video(self, video_path, output_path=None):
        """Detect helmets in a video"""
        cap = cv2.VideoCapture(str(video_path))
        frame_results = []
        total_detections = 0
        total_with_helmet = 0
        total_without_helmet = 0
        frame_count = 0
        
        if output_path is None:
            output_path = Config.UPLOAD_FOLDER / 'results' / f'result_{Path(video_path).stem}.mp4'
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            result = self.detect_image(frame)
            
            # Store every 10th frame result
            if frame_count % 10 == 0:
                frame_results.append(result)
            
            total_detections += result['stats']['total']
            total_with_helmet += result['stats']['with_helmet']
            total_without_helmet += result['stats']['without_helmet']
            
            # Draw on frame and write
            annotated_frame = self._frame_from_base64(result['image'])
            out.write(annotated_frame)
        
        cap.release()
        out.release()
        
        return {
            'video_url': f'/api/uploads/results/{Path(output_path).name}',
            'frame_results': frame_results[:6],  # Return top 6 frames
            'summary': {
                'total_frames': frame_count,
                'total_detections': total_detections,
                'with_helmet': total_with_helmet,
                'without_helmet': total_without_helmet
            }
        }
    
    def _frame_from_base64(self, base64_str):
        """Convert base64 image back to OpenCV frame"""
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

