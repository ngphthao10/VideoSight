# src/gui/segment_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class SegmentTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Frame bên trái: Danh sách phân đoạn
        left_frame = ttk.Frame(self.parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Phân đoạn", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame lọc
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Lọc theo video:").pack(side=tk.LEFT, padx=5)
        self.filter_video_var = tk.StringVar()
        self.filter_video_combo = ttk.Combobox(filter_frame, textvariable=self.filter_video_var, width=20)
        self.filter_video_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Lọc theo đối tượng:").pack(side=tk.LEFT, padx=5)
        self.filter_object_var = tk.StringVar()
        self.filter_object_combo = ttk.Combobox(filter_frame, textvariable=self.filter_object_var, width=20)
        self.filter_object_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Lọc", command=self.filter_segments).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Xóa bộ lọc", command=self.clear_segment_filters).pack(side=tk.LEFT, padx=5)
        
        # Treeview để hiển thị danh sách phân đoạn
        columns = ("ID", "Video", "Đối tượng", "Frame Bắt đầu", "Frame Kết thúc")
        self.segments_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.segments_tree.heading(col, text=col)
            self.segments_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.segments_tree.yview)
        self.segments_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.segments_tree.pack(fill=tk.BOTH, expand=True)
        
        self.segments_tree.bind("<<TreeviewSelect>>", self.on_segment_select)
        
        # Frame nút
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Nút làm mới danh sách
        ttk.Button(button_frame, text="Làm mới", command=self.refresh_segments_list).pack(side=tk.LEFT, padx=5)
        
        # Nút xóa phân đoạn
        ttk.Button(button_frame, text="Xóa", command=self.delete_segment).pack(side=tk.LEFT, padx=5)
        
        # Frame bên phải: Thêm phân đoạn
        right_frame = ttk.Frame(self.parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(right_frame, text="Thêm Phân đoạn Mới", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Form thêm phân đoạn
        # Video
        ttk.Label(right_frame, text="Video:").pack(anchor=tk.W, pady=5)
        self.segment_video_var = tk.StringVar()
        self.segment_video_combo = ttk.Combobox(right_frame, textvariable=self.segment_video_var, width=28)
        self.segment_video_combo.pack(fill=tk.X, pady=5)
        
        # Đối tượng
        ttk.Label(right_frame, text="Đối tượng:").pack(anchor=tk.W, pady=5)
        self.segment_object_var = tk.StringVar()
        self.segment_object_combo = ttk.Combobox(right_frame, textvariable=self.segment_object_var, width=28)
        self.segment_object_combo.pack(fill=tk.X, pady=5)
        
        # Frame bắt đầu và kết thúc
        ttk.Label(right_frame, text="Frame bắt đầu:").pack(anchor=tk.W, pady=5)
        self.start_frame_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.start_frame_var, width=30).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Frame kết thúc:").pack(anchor=tk.W, pady=5)
        self.end_frame_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.end_frame_var, width=30).pack(fill=tk.X, pady=5)
        
        # Nút thêm
        ttk.Button(right_frame, text="Thêm Phân đoạn", command=self.add_segment).pack(pady=10)
        
        # Làm mới danh sách combobox
        self.refresh_combo_lists()
        
        # Làm mới danh sách phân đoạn
        self.refresh_segments_list()
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
        self.refresh_segments_list()
        self.refresh_combo_lists()
    
    def refresh_segments_list(self):
        """Làm mới danh sách phân đoạn"""
        # Xóa dữ liệu cũ
        for item in self.segments_tree.get_children():
            self.segments_tree.delete(item)
        
        # Lấy danh sách phân đoạn
        segments = self.video_manager.segments
        
        # Thêm vào treeview
        count = 1
        for vid, oid, start, end in segments:
            video_name = self.video_manager.videos[vid][0]
            object_name = self.video_manager.objects[oid][0]
            self.segments_tree.insert("", tk.END, values=(count, video_name, object_name, start, end))
            count += 1
    
    def refresh_combo_lists(self):
        """Làm mới danh sách combobox"""
        # Làm mới danh sách video trong combobox
        videos = self.video_manager.get_all_videos()
        video_names = [f"{vid}: {name}" for vid, name, _ in videos]
        self.segment_video_combo['values'] = video_names
        self.filter_video_combo['values'] = [""] + video_names
        
        # Làm mới danh sách đối tượng trong combobox
        objects = self.video_manager.get_all_objects()
        object_names = [f"{oid}: {name}" for oid, name, _ in objects]
        self.segment_object_combo['values'] = object_names
        self.filter_object_combo['values'] = [""] + object_names
    
    def filter_segments(self):
        """Lọc phân đoạn theo video và đối tượng"""
        # Xóa dữ liệu cũ
        for item in self.segments_tree.get_children():
            self.segments_tree.delete(item)
        
        # Lấy giá trị lọc
        video_filter = self.filter_video_var.get().split(": ")[0] if ": " in self.filter_video_var.get() else ""
        object_filter = self.filter_object_var.get().split(": ")[0] if ": " in self.filter_object_var.get() else ""
        
        try:
            vid_filter = int(video_filter) if video_filter else None
            oid_filter = int(object_filter) if object_filter else None
        except ValueError:
            vid_filter = None
            oid_filter = None
        
        # Lấy danh sách phân đoạn
        segments = self.video_manager.segments
        
        # Thêm vào treeview
        count = 1
        for vid, oid, start, end in segments:
            # Áp dụng bộ lọc
            if (vid_filter is None or vid == vid_filter) and (oid_filter is None or oid == oid_filter):
                video_name = self.video_manager.videos[vid][0]
                object_name = self.video_manager.objects[oid][0]
                self.segments_tree.insert("", tk.END, values=(count, video_name, object_name, start, end))
                count += 1
    
    def clear_segment_filters(self):
        """Xóa bộ lọc phân đoạn"""
        self.filter_video_var.set("")
        self.filter_object_var.set("")
        self.refresh_segments_list()
    
    def on_segment_select(self, event):
        """Xử lý sự kiện khi chọn một phân đoạn trong danh sách"""
        # Lấy item được chọn
        selected_item = self.segments_tree.selection()
        if not selected_item:
            return
        
        # Lấy thông tin phân đoạn
        segment_values = self.segments_tree.item(selected_item[0], "values")
        # ID, Video, Đối tượng, Start, End
        
        # Hiển thị thông tin chi tiết cho mục đích xem
        video_name = segment_values[1]
        object_name = segment_values[2]
        start_frame = segment_values[3]
        end_frame = segment_values[4]
        
        # Tìm video_id và object_id
        video_id = None
        for vid, (name, _, _) in self.video_manager.videos.items():
            if name == video_name:
                video_id = vid
                break
        
        object_id = None
        for oid, (name, _) in self.video_manager.objects.items():
            if name == object_name:
                object_id = oid
                break
        
        if video_id is not None and object_id is not None:
            # Cập nhật combobox
            for i, value in enumerate(self.segment_video_combo['values']):
                if value.startswith(f"{video_id}: "):
                    self.segment_video_combo.current(i)
                    break
            
            for i, value in enumerate(self.segment_object_combo['values']):
                if value.startswith(f"{object_id}: "):
                    self.segment_object_combo.current(i)
                    break
            
            # Cập nhật các trường khác
            self.start_frame_var.set(start_frame)
            self.end_frame_var.set(end_frame)
    
    def add_segment(self):
        """Thêm phân đoạn mới"""
        # Lấy thông tin từ form
        video_selection = self.segment_video_var.get()
        object_selection = self.segment_object_var.get()
        
        try:
            # Trích xuất ID từ chuỗi selection
            video_id = int(video_selection.split(":")[0])
            object_id = int(object_selection.split(":")[0])
            
            start_frame = int(self.start_frame_var.get())
            end_frame = int(self.end_frame_var.get())
            
            if start_frame >= end_frame:
                messagebox.showerror("Lỗi", "Frame bắt đầu phải nhỏ hơn frame kết thúc!")
                return
                
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Vui lòng chọn video, đối tượng và nhập frame hợp lệ!")
            return
        
        # Thêm phân đoạn mới
        result = self.video_manager.add_segment(video_id, object_id, start_frame, end_frame)
        
        if result:
            # Làm mới danh sách
            self.refresh_segments_list()
            
            # Xóa form
            self.start_frame_var.set("")
            self.end_frame_var.set("")
            
            messagebox.showinfo("Thành công", "Đã thêm phân đoạn mới!")
        else:
            messagebox.showerror("Lỗi", "Không thể thêm phân đoạn. ID video hoặc đối tượng không hợp lệ!")
    
    def delete_segment(self):
        """Xóa phân đoạn"""
        selected_item = self.segments_tree.selection()
        if not selected_item:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một phân đoạn để xóa!")
            return
        
        # Lấy thông tin phân đoạn
        segment_values = self.segments_tree.item(selected_item[0], "values")
        # ID, Video, Đối tượng, Start, End
        
        # Tìm video_id và object_id
        video_name = segment_values[1]
        object_name = segment_values[2]
        start_frame = int(segment_values[3])
        end_frame = int(segment_values[4])
        
        video_id = None
        for vid, (name, _, _) in self.video_manager.videos.items():
            if name == video_name:
                video_id = vid
                break
        
        object_id = None
        for oid, (name, _) in self.video_manager.objects.items():
            if name == object_name:
                object_id = oid
                break
        
        if video_id is None or object_id is None:
            messagebox.showerror("Lỗi", "Không thể xác định video hoặc đối tượng!")
            return
        
        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa phân đoạn này?")
        if not confirm:
            return
        
        # Xóa phân đoạn
        if self.video_manager.delete_segment(video_id, object_id, start_frame, end_frame):
            messagebox.showinfo("Thành công", "Đã xóa phân đoạn!")
            
            # Làm mới danh sách
            self.refresh_segments_list()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa phân đoạn!")