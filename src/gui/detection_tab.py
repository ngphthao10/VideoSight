# src/gui/detection_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
import logging

logger = logging.getLogger(__name__)

class DetectionTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện tab nhận diện đối tượng"""
        detection_frame = ttk.Frame(self.parent)
        detection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(detection_frame, text="Nhận diện đối tượng trong Video", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame chọn video
        video_select_frame = ttk.LabelFrame(detection_frame, text="Chọn video để phân tích")
        video_select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(video_select_frame, text="Chọn file video", command=self.select_video_file).pack(pady=10)
        
        self.selected_video_var = tk.StringVar()
        ttk.Entry(video_select_frame, textvariable=self.selected_video_var, width=50, state="readonly").pack(pady=5, padx=10, fill=tk.X)
        
        # Frame tùy chọn nhận diện
        detection_options = ttk.LabelFrame(detection_frame, text="Tùy chọn nhận diện")
        detection_options.pack(fill=tk.X, pady=10)
        
        # Model nhận diện
        ttk.Label(detection_options, text="Model nhận diện:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value="YOLOv5")
        models = ["YOLOv5", "YOLOv8", "SSD MobileNet", "Faster R-CNN"]
        ttk.Combobox(detection_options, textvariable=self.model_var, values=models, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # Ngưỡng tin cậy
        ttk.Label(detection_options, text="Ngưỡng tin cậy:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(detection_options, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.confidence_var, length=200)
        confidence_scale.grid(row=1, column=1, padx=5, pady=5)
        
        self.confidence_label = ttk.Label(detection_options, text="0.50")
        self.confidence_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Cập nhật label khi thay đổi giá trị
        def update_confidence_label(*args):
            self.confidence_label.config(text=f"{self.confidence_var.get():.2f}")
        
        self.confidence_var.trace_add("write", update_confidence_label)
        
        # Tần suất lấy mẫu
        ttk.Label(detection_options, text="Tần suất lấy mẫu (frames):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.sample_rate_var = tk.IntVar(value=30)
        ttk.Entry(detection_options, textvariable=self.sample_rate_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Nút bắt đầu phân tích
        ttk.Button(detection_frame, text="Bắt đầu nhận diện", command=self.start_detection).pack(pady=10)
        
        # Thanh tiến trình
        progress_frame = ttk.Frame(detection_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT, padx=5)
        
        # Kết quả phân tích
        result_frame = ttk.LabelFrame(detection_frame, text="Kết quả nhận diện")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview để hiển thị kết quả
        columns = ("Frame", "Đối tượng", "Tin cậy", "Vị trí")
        self.detection_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.detection_tree.heading(col, text=col)
            self.detection_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.detection_tree.yview)
        self.detection_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detection_tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame nút
        button_frame = ttk.Frame(detection_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Nút lưu kết quả
        ttk.Button(button_frame, text="Lưu kết quả vào cơ sở dữ liệu", command=self.save_detection_results).pack(side=tk.LEFT, padx=5)
        
        # Nút xóa kết quả
        ttk.Button(button_frame, text="Xóa kết quả", command=self.clear_detection_results).pack(side=tk.LEFT, padx=5)
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
    
    def select_video_file(self):
        """Hiển thị hộp thoại để chọn file video"""
        # Mở hộp thoại chọn file
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=filetypes
        )
        
        if filepath:
            self.selected_video_var.set(filepath)
    
    def start_detection(self):
        """Bắt đầu nhận diện đối tượng trong video"""
        # Lấy đường dẫn file video
        video_path = self.selected_video_var.get()
        if not video_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
            return
        
        # Lấy tham số nhận diện
        model_name = self.model_var.get()
        confidence = self.confidence_var.get()
        sample_rate = self.sample_rate_var.get()
        
        # Xóa kết quả cũ
        for item in self.detection_tree.get_children():
            self.detection_tree.delete(item)
        
        # Thực hiện nhận diện đối tượng
        try:
            # Thiết lập thanh tiến trình
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            self.parent.update_idletasks()
            
            # Callback để cập nhật tiến trình
            def update_progress(value):
                self.progress_var.set(value * 100)
                self.progress_label.config(text=f"{int(value * 100)}%")
                self.parent.update_idletasks()
            
            # Gọi hàm nhận diện từ module detection
            from ..detection import detect_objects_in_video
            self.detection_results = detect_objects_in_video(
                video_path, model_name, confidence, sample_rate, 
                progress_callback=update_progress
            )
            
            # Hiển thị kết quả
            for result in self.detection_results:
                frame, obj_name, confidence, bbox = result
                self.detection_tree.insert("", tk.END, values=(
                    frame, obj_name, f"{confidence:.2f}",
                    f"({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})"
                ))
            
            messagebox.showinfo("Thành công", f"Đã nhận diện {len(self.detection_results)} đối tượng trong video!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhận diện đối tượng: {str(e)}")
            logger.exception("Lỗi trong quá trình nhận diện")
    
    def save_detection_results(self):
        """Lưu kết quả nhận diện vào cơ sở dữ liệu"""
        # Kiểm tra xem có kết quả không
        if not hasattr(self, 'detection_results') or not self.detection_results:
            messagebox.showerror("Lỗi", "Không có kết quả nhận diện nào để lưu!")
            return
        
        logger.info(f"Bắt đầu lưu {len(self.detection_results)} kết quả nhận diện")
        
        # Lấy đường dẫn video
        video_path = self.selected_video_var.get()
        video_name = os.path.basename(video_path)
        logger.info(f"Video: {video_name}")
        
        # Thêm video mới nếu chưa có
        import cv2
        try:
            # Lấy số frame của video
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            logger.info(f"Tổng số frame: {total_frames}")
        except Exception as e:
            logger.error(f"Lỗi khi đọc số frame: {e}")
            total_frames = 1000  # Giá trị mặc định
        
        video_id = self.video_manager.add_video_if_not_exists(video_name, total_frames)
        logger.info(f"Video ID: {video_id}")
        
        # Xử lý từng kết quả nhận diện
        added_count = 0
        
        # Tạo dictionary để gom nhóm các phân đoạn theo đối tượng
        segments_by_object = {}
        
        for result in self.detection_results:
            frame, obj_name, confidence, bbox = result
            
            # Thêm đối tượng mới nếu chưa có
            object_id = self.video_manager.add_object_if_not_exists(obj_name, "Detected")
            
            # Thêm frame vào dictionary
            if object_id not in segments_by_object:
                segments_by_object[object_id] = []
            
            segments_by_object[object_id].append(frame)
        
        logger.info(f"Đã tìm thấy {len(segments_by_object)} đối tượng khác nhau")
        
        # Tạo các phân đoạn liên tục
        for object_id, frames in segments_by_object.items():
            frames.sort()  # Sắp xếp các frame
            logger.info(f"Xử lý đối tượng ID {object_id} với {len(frames)} frames")
            
            # Gộp các frame liên tục thành phân đoạn
            segments = []
            start = frames[0]
            prev = frames[0]
            
            for i in range(1, len(frames)):
                # Nếu không liên tục, tạo phân đoạn mới
                if frames[i] > prev + 5:  # Threshold 5 frames
                    segments.append((start, prev + 1))
                    start = frames[i]
                prev = frames[i]
            
            # Thêm phân đoạn cuối cùng
            segments.append((start, prev + 1))
            
            logger.info(f"Đã tạo {len(segments)} phân đoạn cho đối tượng {object_id}")
            
            # Thêm các phân đoạn vào database
            for start_frame, end_frame in segments:
                logger.info(f"Thêm phân đoạn: video_id={video_id}, object_id={object_id}, start={start_frame}, end={end_frame}")
                result = self.video_manager.add_segment(video_id, object_id, start_frame, end_frame)
                logger.info(f"Kết quả thêm phân đoạn: {result}")
                if result:
                    added_count += 1
        
        logger.info(f"Tổng số phân đoạn đã thêm: {added_count}")
        messagebox.showinfo("Thành công", f"Đã lưu {added_count} phân đoạn vào cơ sở dữ liệu!")

        
    def clear_detection_results(self):
        """Xóa kết quả nhận diện"""
        if hasattr(self, 'detection_results'):
            del self.detection_results
        
        # Xóa dữ liệu trên treeview
        for item in self.detection_tree.get_children():
            self.detection_tree.delete(item)
        
        # Reset thanh tiến trình
        self.progress_var.set(0)
        self.progress_label.config(text="0%")