from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import base64
from io import BytesIO
from pathlib import Path
from config import Config
import subprocess
import tempfile

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
        
        # 确保 output_path 是 Path 对象
        if output_path is None:
            output_path = Config.UPLOAD_FOLDER / 'results' / f'result_{Path(video_path).stem}.mp4'
        elif isinstance(output_path, str):
            output_path = Path(output_path)
        
        # 使用更兼容的编码格式
        # 优先尝试使用XVID或X264，这些格式在浏览器中兼容性更好
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 尝试多种编码格式，找到可用的
        # 优先使用H.264编码（avc1），这是浏览器最兼容的格式
        codecs_to_try = [
            ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264编码，浏览器兼容性最好
            ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264编码（备用）
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID编码
            ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4编码（最后备选）
        ]
        
        out = None
        used_codec = None
        for codec_name, fourcc in codecs_to_try:
            out = cv2.VideoWriter(str(output_path), fourcc, video_fps, (width, height))
            if out.isOpened():
                used_codec = codec_name
                print(f"Using codec: {codec_name} for video output")
                break
            else:
                if out:
                    out.release()
        
        if not out or not out.isOpened():
            raise RuntimeError(f"Failed to initialize video writer with any codec. Tried: {[c[0] for c in codecs_to_try]}")
        
        # 计算跳帧间隔：根据检测FPS和视频FPS计算
        detection_fps = detection_fps if detection_fps is not None else self.detection_fps
        if detection_fps >= video_fps:
            # 如果检测FPS大于等于视频FPS，每帧都检测
            frame_skip = 1
        else:
            # 计算跳帧间隔：每N帧检测一次
            frame_skip = max(1, int(video_fps / detection_fps))
        
        last_detected_frame = None
        detected_frame_count = 0  # 已检测的帧数（不是总帧数）
        
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
                detected_frame_count += 1
                
                # 收集关键帧：收集所有检测帧（不限制数量），以便更好地展示检测结果
                # 如果检测帧数较少，全部收集；如果较多，均匀采样
                should_collect = False
                if detected_frame_count <= 10:
                    # 前10个检测帧都收集
                    should_collect = True
                else:
                    # 之后每检测到一定数量的帧就收集一个，最多收集30个关键帧
                    collect_interval = max(1, detected_frame_count // 30)
                    should_collect = (detected_frame_count % collect_interval == 0) and len(frame_results) < 30
                
                if should_collect:
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
        
        # 确保视频文件被正确写入和关闭
        # 检查输出文件是否存在且大小大于0
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Video file was not created or is empty: {output_path}")
        
        print(f"Video saved successfully (temporary): {output_path}, size: {output_path.stat().st_size} bytes, codec: {used_codec}")
        
        # 如果使用的不是H.264编码，使用ffmpeg转换为H.264格式以确保浏览器兼容性
        if used_codec not in ['avc1', 'H264']:
            temp_output = None
            try:
                # 创建临时文件用于转换
                temp_output = output_path.parent / f"temp_{output_path.name}"
                output_path.rename(temp_output)
                
                # 使用ffmpeg转换为H.264格式
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', str(temp_output),
                    '-c:v', 'libx264',  # 使用H.264编码
                    '-preset', 'fast',  # 快速编码
                    '-crf', '23',  # 质量参数（18-28，23是默认值）
                    '-c:a', 'copy',  # 如果有音频，直接复制
                    '-movflags', '+faststart',  # 优化网络播放
                    '-y',  # 覆盖输出文件
                    str(output_path)
                ]
                
                print(f"Converting video to H.264 using ffmpeg...")
                result = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    # 删除临时文件
                    if temp_output and temp_output.exists():
                        temp_output.unlink()
                    print(f"Video converted to H.264 successfully: {output_path}, size: {output_path.stat().st_size} bytes")
                else:
                    # 转换失败，恢复原文件
                    print(f"FFmpeg conversion failed: {result.stderr}")
                    if temp_output and temp_output.exists():
                        temp_output.rename(output_path)
                    print(f"Using original video file with codec: {used_codec}")
            except subprocess.TimeoutExpired:
                print("FFmpeg conversion timed out, using original video")
                if temp_output and temp_output.exists():
                    temp_output.rename(output_path)
            except FileNotFoundError:
                print("FFmpeg not found, using original video with codec:", used_codec)
                if temp_output and temp_output.exists():
                    temp_output.rename(output_path)
            except Exception as e:
                print(f"Error during video conversion: {str(e)}")
                import traceback
                traceback.print_exc()
                if temp_output and temp_output.exists():
                    temp_output.rename(output_path)
        else:
            print(f"Video already in H.264 format: {output_path}, size: {output_path.stat().st_size} bytes")
        
        return {
            'video_url': f'/api/detect/uploads/results/{Path(output_path).name}',
            'frame_results': frame_results,  # Return all collected keyframes (up to 30)
            'summary': {
                'total_frames': frame_count,
                'total_detections': total_detections,
                'with_helmet': total_with_helmet,
                'without_helmet': total_without_helmet,
                'detected_frames': detected_frame_count  # 实际检测的帧数
            }
        }
    
    def _frame_from_base64(self, base64_str):
        """Convert base64 image back to OpenCV frame"""
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

