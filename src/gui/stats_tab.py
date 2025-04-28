# src/gui/stats_tab.py
import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class StatsTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện tab thống kê"""
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(stats_frame, text="Thống kê dữ liệu", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame nút điều khiển
        control_frame = ttk.Frame(stats_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Cập nhật thống kê", command=self.update_statistics).pack(side=tk.LEFT, padx=5)
        
        # Notebook cho các tab thống kê
        self.stats_notebook = ttk.Notebook(stats_frame)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tab thống kê tổng quan
        self.overview_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.overview_tab, text="Tổng quan")
        
        # Tạo frame cho thống kê tổng quan
        overview_frame = ttk.LabelFrame(self.overview_tab, text="Thống kê tổng quan")
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Các chỉ số thống kê
        self.total_videos_var = tk.StringVar(value="Tổng số video: 0")
        ttk.Label(overview_frame, textvariable=self.total_videos_var, font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        self.total_objects_var = tk.StringVar(value="Tổng số đối tượng: 0")
        ttk.Label(overview_frame, textvariable=self.total_objects_var, font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        self.total_segments_var = tk.StringVar(value="Tổng số phân đoạn: 0")
        ttk.Label(overview_frame, textvariable=self.total_segments_var, font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        self.avg_segments_per_video_var = tk.StringVar(value="Số phân đoạn trung bình/video: 0")
        ttk.Label(overview_frame, textvariable=self.avg_segments_per_video_var, font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        self.avg_objects_per_video_var = tk.StringVar(value="Số đối tượng trung bình/video: 0")
        ttk.Label(overview_frame, textvariable=self.avg_objects_per_video_var, font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        # Tab thống kê theo đối tượng
        self.objects_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.objects_tab, text="Đối tượng")
        
        # Tạo frame cho thống kê theo đối tượng
        objects_frame = ttk.LabelFrame(self.objects_tab, text="Thống kê theo loại đối tượng")
        objects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview để hiển thị thống kê đối tượng
        columns = ("Loại đối tượng", "Số lượng", "Tỷ lệ (%)")
        self.objects_stats_tree = ttk.Treeview(objects_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.objects_stats_tree.heading(col, text=col)
            self.objects_stats_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(objects_frame, orient="vertical", command=self.objects_stats_tree.yview)
        self.objects_stats_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.objects_stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # Tab thống kê theo video
        self.videos_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.videos_tab, text="Video")
        
        # Tạo frame cho thống kê theo video
        videos_frame = ttk.LabelFrame(self.videos_tab, text="Thống kê theo video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview để hiển thị thống kê video
        columns = ("ID", "Tên video", "Số frame", "Số đối tượng", "Số phân đoạn")
        self.videos_stats_tree = ttk.Treeview(videos_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.videos_stats_tree.heading(col, text=col)
            self.videos_stats_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(videos_frame, orient="vertical", command=self.videos_stats_tree.yview)
        self.videos_stats_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.videos_stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # Cập nhật thống kê
        self.update_statistics()
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
        self.update_statistics()
    
    def update_statistics(self):
        """Cập nhật thống kê"""
        # Thống kê tổng quan
        videos = self.video_manager.get_all_videos()
        objects = self.video_manager.get_all_objects()
        segments = self.video_manager.segments
        
        # Cập nhật các biến hiển thị
        self.total_videos_var.set(f"Tổng số video: {len(videos)}")
        self.total_objects_var.set(f"Tổng số đối tượng: {len(objects)}")
        self.total_segments_var.set(f"Tổng số phân đoạn: {len(segments)}")
        
        # Tính trung bình
        if len(videos) > 0:
            avg_segments = len(segments) / len(videos)
            self.avg_segments_per_video_var.set(f"Số phân đoạn trung bình/video: {avg_segments:.2f}")
            
            # Đếm số đối tượng xuất hiện trong mỗi video
            objects_per_video = {}
            for vid, oid, _, _ in segments:
                if vid not in objects_per_video:
                    objects_per_video[vid] = set()
                objects_per_video[vid].add(oid)
            
            total_objects = sum(len(objs) for objs in objects_per_video.values())
            avg_objects = total_objects / len(videos)
            self.avg_objects_per_video_var.set(f"Số đối tượng trung bình/video: {avg_objects:.2f}")
        else:
            self.avg_segments_per_video_var.set("Số phân đoạn trung bình/video: 0")
            self.avg_objects_per_video_var.set("Số đối tượng trung bình/video: 0")
        
        # Thống kê theo loại đối tượng
        object_stats = self.video_manager.get_object_statistics()
        
        # Xóa dữ liệu cũ
        for item in self.objects_stats_tree.get_children():
            self.objects_stats_tree.delete(item)
        
        # Tính tổng số đối tượng
        total_objects = len(objects)
        
        # Thêm vào treeview
        for obj_type, count in object_stats.items():
            percentage = (count / total_objects) * 100 if total_objects > 0 else 0
            self.objects_stats_tree.insert("", tk.END, values=(obj_type, count, f"{percentage:.2f}"))
        
        # Thống kê theo video
        video_stats = self.video_manager.get_video_statistics()
        
        # Xóa dữ liệu cũ
        for item in self.videos_stats_tree.get_children():
            self.videos_stats_tree.delete(item)
        
        # Thêm vào treeview
        for vid, stats in video_stats.items():
            self.videos_stats_tree.insert("", tk.END, values=(
                vid, 
                stats["name"], 
                stats["frames"], 
                stats["object_count"], 
                stats["segment_count"]
            ))