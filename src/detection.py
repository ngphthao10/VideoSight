import cv2
import torch
import numpy as np
import os
import time

def detect_objects_in_video(video_path, model_name="YOLOv5", confidence_threshold=0.5, sample_rate=30, progress_callback=None):
    """
    Nhận diện đối tượng trong video sử dụng mô hình được chọn
    
    Args:
        video_path: Đường dẫn đến file video
        model_name: Tên mô hình sử dụng
        confidence_threshold: Ngưỡng tin cậy
        sample_rate: Tần suất lấy mẫu (mỗi bao nhiêu frame)
        progress_callback: Hàm callback để cập nhật tiến trình
        
    Returns:
        list: Danh sách kết quả [(frame, label, confidence, bbox), ...]
    """
    results = []
    
    try:
        # Tải model YOLOv5 từ torch hub
        if model_name == "YOLOv5":
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        elif model_name == "YOLOv8":
            # Sử dụng YOLOv5 làm thay thế
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            print("YOLOv8 chưa được hỗ trợ, sử dụng YOLOv5 thay thế")
        else:
            # Mặc định sử dụng YOLOv5
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            print(f"Model {model_name} chưa được hỗ trợ, sử dụng YOLOv5 thay thế")
        
        # Thiết lập ngưỡng tin cậy
        model.conf = confidence_threshold
        
        # Mở video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("Không thể mở video")
        
        # Lấy thông tin về video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Video có {total_frames} frames, FPS: {fps}")
        
        # Xử lý từng frame
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Chỉ xử lý các frame theo tần suất lấy mẫu
            if frame_count % sample_rate == 0:
                # Cập nhật tiến trình
                if progress_callback:
                    progress = frame_count / total_frames
                    progress_callback(progress)
                
                # Nhận diện đối tượng trong frame
                detections = model(frame)
                
                # Xử lý kết quả nhận diện
                for det in detections.xyxy[0]:  # xyxy format: x1, y1, x2, y2, confidence, class
                    x1, y1, x2, y2, conf, cls = det.tolist()
                    label = detections.names[int(cls)]
                    
                    # Lưu kết quả
                    results.append((frame_count, label, conf, (x1, y1, x2, y2)))
            
            frame_count += 1
        
        # Đóng video
        cap.release()
        
        # Cập nhật tiến trình hoàn thành
        if progress_callback:
            progress_callback(1.0)
            
    except Exception as e:
        print(f"Lỗi trong quá trình nhận diện: {str(e)}")
        raise e
    
    return results

def extract_keyframes(video_path, output_dir, interval=30):
    """
    Trích xuất các keyframe từ video
    
    Args:
        video_path: Đường dẫn đến file video
        output_dir: Thư mục lưu các frame
        interval: Khoảng cách giữa các frame (mỗi bao nhiêu frame)
    
    Returns:
        list: Danh sách đường dẫn đến các frame đã lưu
    """
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    # Mở video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception("Không thể mở video")
    
    frame_paths = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Lưu frame theo khoảng thời gian
        if frame_count % interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
        
        frame_count += 1
    
    cap.release()
    return frame_paths