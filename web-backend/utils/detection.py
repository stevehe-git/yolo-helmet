from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import base64
from io import BytesIO
from pathlib import Path
from config import Config

class DetectionService:
    def __init__(self, model_path=None, confidence_threshold=None):
        if model_path is None:
            # 不再使用默认模型，必须明确指定模型路径
            raise ValueError('必须指定模型路径，不能使用默认模型')
        
        self.model = YOLO(str(model_path))
        self.class_names = {0: 'with_helmet', 1: 'without_helmet'}
        # 支持动态置信度阈值
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else Config.CONFIDENCE_THRESHOLD
        # 支持动态检测帧率
        self.detection_fps = 10  # 默认10 FPS
    
    def detect_image(self, image_path_or_array, confidence=None):
        """Detect helmets in an image"""
        # 使用传入的置信度或实例的置信度阈值
        conf_threshold = confidence if confidence is not None else self.confidence_threshold
        try:
            results = self.model(image_path_or_array, conf=conf_threshold, iou=Config.IOU_THRESHOLD, task='detect')
        except Exception as e:
            # 如果指定task失败，尝试不指定task
            print(f"Warning: Failed with task='detect', trying without task: {str(e)}")
            results = self.model(image_path_or_array, conf=conf_threshold, iou=Config.IOU_THRESHOLD)
        
        detections = []
        with_helmet = 0
        without_helmet = 0
        
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
            boxes = result.boxes
            for box in boxes:
                if box.cls is None or len(box.cls) == 0:
                    continue
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
        try:
            if isinstance(image_path_or_array, (str, Path)):
                img = cv2.imread(str(image_path_or_array))
                if img is None:
                    raise ValueError(f"无法读取图片: {image_path_or_array}")
            else:
                img = image_path_or_array
                if img is None:
                    raise ValueError("图片数组为空")
            
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
        except Exception as e:
            print(f"Error in _draw_detections: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def detect_video(self, video_path, output_path=None, detection_fps=None):
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
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(str(output_path), fourcc, video_fps, (width, height))
        
        # 计算跳帧间隔：根据检测FPS和视频FPS计算
        detection_fps = detection_fps if detection_fps is not None else self.detection_fps
        if detection_fps >= video_fps:
            # 如果检测FPS大于等于视频FPS，每帧都检测
            frame_skip = 1
        else:
            # 计算跳帧间隔：每N帧检测一次
            frame_skip = max(1, int(video_fps / detection_fps))
        
        last_detected_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 根据跳帧间隔决定是否检测
            if frame_count % frame_skip == 0:
                # 进行检测
                result = self.detect_image(frame)
                last_detected_frame = result
                
                # Store every 10th frame result
                if frame_count % (frame_skip * 10) == 0:
                    frame_results.append(result)
                
                total_detections += result['stats']['total']
                total_with_helmet += result['stats']['with_helmet']
                total_without_helmet += result['stats']['without_helmet']
                
                # Draw on frame and write
                annotated_frame = self._frame_from_base64(result['image'])
                out.write(annotated_frame)
            else:
                # 跳过检测，直接使用上一帧的检测结果（如果有）
                if last_detected_frame:
                    annotated_frame = self._frame_from_base64(last_detected_frame['image'])
                    out.write(annotated_frame)
                else:
                    # 第一帧之前，直接写入原始帧
                    out.write(frame)
        
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

