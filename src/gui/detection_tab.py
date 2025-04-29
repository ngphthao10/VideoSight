# src/gui/detection_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
import logging
import threading
import time
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

class DetectionTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.detector = None
        self.is_detecting = False
        self.video_frame = None
        self.detection_results = []  # Kết quả phát hiện tích lũy
        self.current_results = []    # Kết quả phát hiện cho frame hiện tại
        self.update_id = None
        self.max_results = 10000     # Giới hạn số lượng kết quả lưu trữ
        
        # Tải các module cần thiết
        try:
            from ..realtime_detection import VideoDetector
            self.VideoDetector = VideoDetector
        except ImportError as e:
            logger.error(f"Không thể tải module realtime_detection: {e}")
            self.VideoDetector = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện tab nhận diện đối tượng"""
        detection_frame = ttk.Frame(self.parent)
        detection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Phân chia thành hai phần: cài đặt và hiển thị video
        left_frame = ttk.Frame(detection_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        right_frame = ttk.Frame(detection_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phần cài đặt (bên trái)
        # Tiêu đề
        ttk.Label(left_frame, text="Nhận diện đối tượng trong Video", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame chọn video
        video_select_frame = ttk.LabelFrame(left_frame, text="Chọn video")
        video_select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(video_select_frame, text="Chọn file video", command=self.select_video_file).pack(pady=10)
        
        self.selected_video_var = tk.StringVar()
        ttk.Entry(video_select_frame, textvariable=self.selected_video_var, width=30, state="readonly").pack(pady=5, padx=10, fill=tk.X)
        
        # Frame tùy chọn nhận diện
        detection_options = ttk.LabelFrame(left_frame, text="Tùy chọn nhận diện")
        detection_options.pack(fill=tk.X, pady=10)
        
        # Model nhận diện
        ttk.Label(detection_options, text="Model nhận diện:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value="YOLOv5")
        models = ["YOLOv5", "YOLOv8", "SSD MobileNet", "Faster R-CNN"]
        ttk.Combobox(detection_options, textvariable=self.model_var, values=models, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        # Ngưỡng tin cậy
        ttk.Label(detection_options, text="Ngưỡng tin cậy:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(detection_options, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.confidence_var, length=150)
        confidence_scale.grid(row=1, column=1, padx=5, pady=5)
        
        self.confidence_label = ttk.Label(detection_options, text="0.50")
        self.confidence_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Tùy chỉnh bỏ qua frame
        ttk.Label(detection_options, text="Bỏ qua frame:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.skip_frames_var = tk.IntVar(value=2)
        ttk.Spinbox(detection_options, from_=0, to=10, textvariable=self.skip_frames_var, width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(detection_options, text="(Cao hơn = nhanh hơn)").grid(row=2, column=2, padx=5, pady=5)
        
        # Cập nhật label khi thay đổi giá trị
        def update_confidence_label(*args):
            self.confidence_label.config(text=f"{self.confidence_var.get():.2f}")
        
        self.confidence_var.trace_add("write", update_confidence_label)
        
        # Nút điều khiển
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Bắt đầu", command=self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Dừng", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Nút lưu video
        save_frame = ttk.Frame(left_frame)
        save_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(save_frame, text="Lưu video kết quả:").pack(anchor=tk.W)
        
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(save_frame, textvariable=self.output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(save_frame, text="...", command=self.select_output_file, width=3).pack(side=tk.LEFT, padx=2, pady=5)
        
        ttk.Button(save_frame, text="Lưu video", command=self.save_detection_video).pack(pady=5)
        
        # Nút lưu kết quả vào DB
        db_frame = ttk.Frame(left_frame)
        db_frame.pack(fill=tk.X, pady=10)
        
        self.db_button = ttk.Button(db_frame, text="Lưu kết quả vào DB", command=self.save_detection_results)
        self.db_button.pack(fill=tk.X)
        
        # Thông tin kết quả phát hiện
        result_info_frame = ttk.Frame(left_frame)
        result_info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(result_info_frame, text="Số kết quả phát hiện:").pack(side=tk.LEFT, padx=5)
        self.result_count_var = tk.StringVar(value="0")
        ttk.Label(result_info_frame, textvariable=self.result_count_var).pack(side=tk.LEFT, padx=5)
        
        # Phần hiển thị video (bên phải)
        # Frame hiển thị video
        video_display_frame = ttk.LabelFrame(right_frame, text="Video")
        video_display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas để hiển thị video
        self.canvas = tk.Canvas(video_display_frame, bg="black", width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Khung hiển thị trạng thái
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Trạng thái:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="Chưa bắt đầu")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(status_frame, text="FPS:").pack(side=tk.LEFT, padx=5)
        self.fps_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.fps_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(status_frame, text="Frame:").pack(side=tk.LEFT, padx=5)
        self.frame_var = tk.StringVar(value="0/0")
        ttk.Label(status_frame, textvariable=self.frame_var).pack(side=tk.LEFT, padx=5)
        
        # Kết quả phân tích
        result_frame = ttk.LabelFrame(right_frame, text="Kết quả nhận diện")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview để hiển thị kết quả
        columns = ("Frame", "Đối tượng", "Tin cậy", "Vị trí")
        self.detection_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)
        
        # Thiết lập các cột
        for col in columns:
            self.detection_tree.heading(col, text=col)
            self.detection_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.detection_tree.yview)
        self.detection_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detection_tree.pack(fill=tk.BOTH, expand=True)
    
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
            
    def select_output_file(self):
        """Hiển thị hộp thoại để chọn file đầu ra"""
        # Mở hộp thoại chọn file
        filetypes = [
            ("MP4 video", "*.mp4"),
            ("AVI video", "*.avi")
        ]
        filepath = filedialog.asksaveasfilename(
            title="Lưu video đầu ra",
            filetypes=filetypes,
            defaultextension=".mp4"
        )
        
        if filepath:
            self.output_var.set(filepath)
    
    def start_detection(self):
        """Bắt đầu nhận diện đối tượng trong video"""
        # Kiểm tra video
        video_path = self.selected_video_var.get()
        if not video_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
            return
        
        # Kiểm tra module detector
        if self.VideoDetector is None:
            messagebox.showerror("Lỗi", "Không thể tải module phát hiện đối tượng!")
            return
        
        # Dừng nếu đang chạy
        if self.is_detecting:
            self.stop_detection()
        
        # Xóa kết quả cũ
        self.clear_detection_results()
        
        # Lấy tham số
        model_name = self.model_var.get()
        confidence = self.confidence_var.get()
        skip_frames = self.skip_frames_var.get()
        
        try:
            # Callback khi có frame mới
            def update_frame(frame, results):
                if not self.is_detecting:
                    return
                
                # Hiển thị frame
                self.update_video_display(frame)
                
                # Cập nhật trạng thái
                if hasattr(self.detector, 'fps'):
                    self.fps_var.set(f"{self.detector.fps:.1f}")
                if hasattr(self.detector, 'frame_count') and hasattr(self.detector, 'total_frames'):
                    self.frame_var.set(f"{self.detector.frame_count}/{self.detector.total_frames}")
                
                # Cập nhật kết quả vào tree view
                if results:
                    # Xóa bảng nếu có quá nhiều kết quả hiển thị
                    if len(self.detection_tree.get_children()) > 100:
                        for item in self.detection_tree.get_children():
                            self.detection_tree.delete(item)
                    
                    # Thêm kết quả mới vào đầu bảng
                    for result in results:
                        if not result in self.current_results:  # Chỉ hiển thị kết quả mới
                            frame, label, conf, bbox = result
                            self.detection_tree.insert("", 0, values=(
                                frame, label, f"{conf:.2f}",
                                f"({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"
                            ))
                            
                            # Lưu trữ kết quả để phân tích sau
                            self.detection_results.append(result)
                            
                            # Giới hạn số lượng kết quả lưu trữ
                            if len(self.detection_results) > self.max_results:
                                self.detection_results = self.detection_results[-self.max_results:]
                                
                    # Cập nhật số lượng kết quả
                    self.result_count_var.set(str(len(self.detection_results)))
                    
                    # Lưu kết quả hiện tại
                    self.current_results = results.copy()
            
            # Khởi tạo detector
            self.detector = self.VideoDetector(
                video_path=video_path,
                model_name=model_name,
                confidence_threshold=confidence,
                update_callback=update_frame
            )
            
            # Cập nhật skip frames
            self.detector.skip_frames = skip_frames
            
            # Bắt đầu detector
            if self.detector.start():
                self.is_detecting = True
                self.status_var.set("Đang phát hiện...")
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.db_button.config(state=tk.DISABLED)  # Không thể lưu trong khi đang phát hiện
                
                # Cập nhật định kỳ
                self.update_detection_display()
            else:
                messagebox.showerror("Lỗi", "Không thể bắt đầu phát hiện!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể bắt đầu phát hiện: {str(e)}")
            logger.exception("Lỗi khi bắt đầu phát hiện")
    
    def stop_detection(self):
        """Dừng nhận diện đối tượng"""
        if not self.is_detecting or self.detector is None:
            return
        
        try:
            # Dừng detector
            self.detector.stop()
            
            # Cập nhật trạng thái
            self.is_detecting = False
            self.status_var.set("Đã dừng")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.db_button.config(state=tk.NORMAL)  # Bật lại nút lưu
            
            # Dừng cập nhật
            if self.update_id is not None:
                self.parent.after_cancel(self.update_id)
                self.update_id = None
            
            # Hiển thị thông báo số lượng kết quả phát hiện
            messagebox.showinfo("Kết quả phát hiện", 
                               f"Đã phát hiện {len(self.detection_results)} đối tượng trong video.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể dừng phát hiện: {str(e)}")
            logger.exception("Lỗi khi dừng phát hiện")
    
    def update_video_display(self, frame):
        """Cập nhật hiển thị video"""
        if frame is None:
            return
        
        try:
            # Điều chỉnh kích thước frame
            frame_height, frame_width = frame.shape[:2]
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Nếu canvas chưa được hiển thị
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 640
                canvas_height = 480
            
            # Tính toán tỷ lệ để giữ nguyên aspect ratio
            scale = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Chuyển đổi frame thành hình ảnh Tkinter
            # Chuyển từ BGR sang RGB
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Chuyển thành hình ảnh PIL
            pil_image = Image.fromarray(rgb_frame)
            
            # Chuyển thành hình ảnh Tkinter
            self.video_frame = ImageTk.PhotoImage(image=pil_image)
            
            # Cập nhật canvas
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.video_frame)
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật hiển thị video: {e}")
    
    def update_detection_display(self):
        """Cập nhật hiển thị video theo định kỳ"""
        if not self.is_detecting or self.detector is None:
            return
        
        # Cập nhật lại sau 33ms (khoảng 30 FPS)
        self.update_id = self.parent.after(33, self.update_detection_display)
    
    def save_detection_video(self):
        """Lưu video đã phát hiện"""
        if self.detector is None:
            messagebox.showerror("Lỗi", "Chưa khởi tạo detector!")
            return
        
        output_path = self.output_var.get()
        if not output_path:
            output_path = filedialog.asksaveasfilename(
                title="Lưu video đầu ra",
                filetypes=[("MP4 video", "*.mp4"), ("AVI video", "*.avi")],
                defaultextension=".mp4"
            )
            if output_path:
                self.output_var.set(output_path)
            else:
                return
        
        # Hỏi xác nhận nếu đang trong chế độ phát hiện
        if self.is_detecting:
            confirm = messagebox.askyesno(
                "Xác nhận", 
                "Phát hiện đang chạy sẽ bị dừng lại để lưu video. Bạn có muốn tiếp tục không?"
            )
            if not confirm:
                return
        
        # Lưu video
        try:
            # Dừng phát hiện nếu đang chạy
            was_running = self.is_detecting
            if was_running:
                self.stop_detection()
            
            # Hiển thị thông báo
            self.status_var.set("Đang lưu video...")
            self.parent.update_idletasks()
            
            # Lưu video
            success = self.detector.save_video_with_detection(output_path)
            
            if success:
                messagebox.showinfo("Thành công", f"Đã lưu video thành công: {output_path}")
                self.status_var.set("Đã lưu video")
            else:
                messagebox.showerror("Lỗi", "Không thể lưu video!")
                self.status_var.set("Lỗi khi lưu video")
            
            # Khởi động lại nếu đã dừng
            if was_running:
                self.start_detection()
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu video: {str(e)}")
            logger.exception("Lỗi khi lưu video")
    
    def save_detection_results(self):
        """Lưu kết quả nhận diện vào cơ sở dữ liệu"""
        # Kiểm tra xem có kết quả không
        if not hasattr(self, 'detection_results') or not self.detection_results:
            messagebox.showerror("Lỗi", "Không có kết quả nhận diện nào để lưu!")
            return
        
        logger.info(f"Bắt đầu lưu {len(self.detection_results)} kết quả nhận diện")
        
        # Lấy đường dẫn video và tên video
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
            if len(frames) > 0:
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
            self.detection_results = []
            self.current_results = []
            self.result_count_var.set("0")
        
        # Xóa dữ liệu trên treeview
        for item in self.detection_tree.get_children():
            self.detection_tree.delete(item)
        
    def __del__(self):
        """Phương thức hủy để giải phóng tài nguyên"""
        if hasattr(self, 'is_detecting') and self.is_detecting:
            self.stop_detection()
        
        if hasattr(self, 'update_id') and self.update_id is not None:
            try:
                self.parent.after_cancel(self.update_id)
            except Exception:
                pass