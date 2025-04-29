# src/realtime_detection.py
import cv2
import torch
import numpy as np
import time
import logging
from threading import Thread, Event

logger = logging.getLogger(__name__)

class VideoDetector:
    def __init__(self, video_path=None, model_name="YOLOv5", confidence_threshold=0.5, update_callback=None):
        """
        Khởi tạo detector video
        
        Args:
            video_path: Đường dẫn đến file video
            model_name: Tên mô hình sử dụng
            confidence_threshold: Ngưỡng tin cậy
            update_callback: Callback được gọi khi có frame mới được xử lý
        """
        self.video_path = video_path
        self.confidence_threshold = confidence_threshold
        self.update_callback = update_callback
        self.is_running = False
        self.stop_event = Event()
        self.detection_thread = None
        self.cap = None
        self.frame_count = 0
        self.last_detection_results = []
        self.current_frame = None
        self.fps = 0
        self.real_fps = 0  # FPS thực tế của video
        self.skip_frames = 2  # Skip frames để tăng tốc độ xử lý
        
        # Tải model
        try:
            # Sử dụng cache=True để tránh tải lại model mỗi lần
            if model_name == "YOLOv5":
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)
            elif model_name == "YOLOv8":
                # Sử dụng YOLOv5 làm thay thế
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)
                logger.warning("YOLOv8 chưa được hỗ trợ, sử dụng YOLOv5 thay thế")
            else:
                # Mặc định sử dụng YOLOv5
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)
                logger.warning(f"Model {model_name} chưa được hỗ trợ, sử dụng YOLOv5 thay thế")
            
            # Thiết lập ngưỡng tin cậy
            self.model.conf = confidence_threshold
            logger.info(f"Đã tải model {model_name}")
            
            # Chạy dự đoán thử để khởi tạo model
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            self.model(dummy_img)
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model: {str(e)}")
            self.model = None
    
    def start(self):
        """Bắt đầu phát hiện trong video"""
        if self.is_running:
            logger.warning("Phát hiện đang chạy rồi!")
            return False
        
        # Kiểm tra video path
        if not self.video_path:
            logger.error("Cần chọn video trước khi bắt đầu!")
            return False
            
        # Khởi tạo video capture
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            
            if not self.cap.isOpened():
                logger.error("Không thể mở video!")
                return False
            
            self.is_running = True
            self.stop_event.clear()
            
            # Đọc thông tin video
            self.real_fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_count = 0
            
            logger.info(f"Video FPS: {self.real_fps}, Total frames: {self.total_frames}")
            
            # Bắt đầu thread xử lý
            self.detection_thread = Thread(target=self._detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()
            
            logger.info("Đã bắt đầu phát hiện trong video")
            return True
        
        except Exception as e:
            logger.error(f"Lỗi khi bắt đầu phát hiện: {str(e)}")
            if self.cap:
                self.cap.release()
            self.is_running = False
            return False
    
    def stop(self):
        """Dừng phát hiện"""
        if not self.is_running:
            return
        
        logger.info("Đang dừng phát hiện...")
        self.stop_event.set()
        self.is_running = False
        
        # Đợi thread kết thúc
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
            logger.info("Đã dừng thread phát hiện")
        
        # Giải phóng video capture
        if self.cap:
            self.cap.release()
            self.cap = None
            logger.info("Đã giải phóng video capture")
        
        logger.info("Đã dừng phát hiện")
    
    def _detection_loop(self):
        """Vòng lặp phát hiện chạy trong thread riêng"""
        last_time = time.time()
        frames_processed = 0
        frame_interval = 1.0 / self.real_fps if self.real_fps > 0 else 0.033
        
        while not self.stop_event.is_set():
            start_process_time = time.time()
            
            # Đọc frame
            ret, frame = self.cap.read()
            
            if not ret:
                # Kết thúc video
                logger.info("Video đã kết thúc")
                self.stop()
                break
            
            # Tăng frame count
            self.frame_count += 1
            frames_processed += 1
            
            # Skip frames để tăng tốc độ (chỉ phát hiện mỗi 'skip_frames' frame)
            if self.frame_count % self.skip_frames != 0:
                # Vẫn hiển thị frame nhưng không phát hiện
                if self.update_callback:
                    # Thêm thông tin trạng thái vào frame
                    cv2.putText(frame, f"Frame: {self.frame_count}/{self.total_frames}", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"FPS: {self.fps:.1f}", 
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Vẽ các box đã phát hiện được trước đó
                    for _, label, conf, (x1, y1, x2, y2) in self.last_detection_results:
                        # Vẽ khung
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Vẽ nhãn
                        text = f"{label}: {conf:.2f}"
                        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    self.update_callback(frame, self.last_detection_results)
                
                # Tính toán thời gian cần đợi để duy trì tốc độ
                process_time = time.time() - start_process_time
                wait_time = max(0, frame_interval - process_time)
                time.sleep(wait_time)
                
                continue
            
            # Lưu frame hiện tại
            self.current_frame = frame.copy()
            
            # Tính FPS thực tế
            current_time = time.time()
            if current_time - last_time >= 1.0:  # Cập nhật FPS mỗi giây
                self.fps = frames_processed / (current_time - last_time)
                frames_processed = 0
                last_time = current_time
            
            # Phát hiện đối tượng
            try:
                if self.model is not None:
                    # Sử dụng model để phát hiện
                    with torch.no_grad():  # Tắt gradient để tiết kiệm bộ nhớ và tăng tốc
                        results = self.model(frame)
                    
                    # Xử lý kết quả
                    new_results = []
                    
                    for det in results.xyxy[0]:  # xyxy format: x1, y1, x2, y2, confidence, class
                        x1, y1, x2, y2, conf, cls = det.tolist()
                        if conf >= self.confidence_threshold:
                            label = results.names[int(cls)]
                            
                            # Lưu kết quả
                            new_results.append((self.frame_count, label, conf, (int(x1), int(y1), int(x2), int(y2))))
                    
                    # Chỉ cập nhật nếu có kết quả mới
                    if new_results:
                        self.last_detection_results = new_results
                    
                    # Vẽ bounding box lên frame
                    for _, label, conf, (x1, y1, x2, y2) in self.last_detection_results:
                        # Vẽ khung
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Vẽ nhãn
                        text = f"{label}: {conf:.2f}"
                        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            except Exception as e:
                logger.error(f"Lỗi khi phát hiện đối tượng: {str(e)}")
            
            # Vẽ thông tin lên frame
            cv2.putText(frame, f"Frame: {self.frame_count}/{self.total_frames}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"FPS: {self.fps:.1f}", 
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Gọi callback nếu có
            if self.update_callback:
                self.update_callback(frame, self.last_detection_results)
            
            # Tính toán thời gian xử lý và thời gian đợi để duy trì tốc độ
            process_time = time.time() - start_process_time
            wait_time = max(0, frame_interval - process_time)
            
            # Đợi để duy trì tốc độ phát lại gần với FPS gốc
            time.sleep(wait_time)
    
    def save_video_with_detection(self, output_path):
        """
        Lưu video với kết quả phát hiện
        
        Args:
            output_path: Đường dẫn file đầu ra
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        if not self.video_path:
            logger.error("Không có video để lưu!")
            return False
        
        try:
            # Tạm dừng phát hiện hiện tại
            was_running = self.is_running
            if was_running:
                self.stop()
            
            # Mở video đầu vào
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                logger.error("Không thể mở video đầu vào!")
                return False
            
            # Lấy thông tin video
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Tạo VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Định dạng MP4
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Khởi tạo model
            model = self.model
            
            # Xử lý từng frame
            for frame_idx in range(total_frames):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Phát hiện đối tượng mỗi 3 frame để tăng tốc
                if frame_idx % 3 == 0:
                    # Phát hiện đối tượng
                    with torch.no_grad():
                        results = model(frame)
                    
                    # Lưu kết quả mới nhất
                    detections = []
                    for det in results.xyxy[0]:
                        x1, y1, x2, y2, conf, cls = det.tolist()
                        if conf >= self.confidence_threshold:
                            label = results.names[int(cls)]
                            detections.append((label, conf, (int(x1), int(y1), int(x2), int(y2))))
                
                # Vẽ bounding box
                for label, conf, (x1, y1, x2, y2) in detections:
                    # Vẽ khung
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Vẽ nhãn
                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Vẽ thông tin frame
                cv2.putText(frame, f"Frame: {frame_idx}/{total_frames}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Ghi frame đã xử lý
                out.write(frame)
                
                # Hiển thị tiến trình
                if frame_idx % 30 == 0:  # Mỗi 30 frame
                    logger.info(f"Tiến trình: {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")
            
            # Giải phóng tài nguyên
            cap.release()
            out.release()
            
            logger.info(f"Đã lưu video thành công: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Lỗi khi lưu video: {str(e)}")
            return False