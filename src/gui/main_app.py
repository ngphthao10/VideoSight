import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os

from .video_tab import VideoTab
from .object_tab import ObjectTab
from .segment_tab import SegmentTab
from .search_tab import SearchTab
from .detection_tab import DetectionTab
from .stats_tab import StatsTab
from .db_settings import show_db_settings

# Configure logging
logger = logging.getLogger(__name__)

class VideoDBApp:
    def __init__(self, root, video_manager):
        self.root = root
        self.video_manager = video_manager
        
        # Thiết lập cửa sổ chính
        self.root.title("Hệ thống Cơ sở dữ liệu Video - MongoDB")
        self.root.geometry("900x600")
        
        # Frame trạng thái
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Hiển thị trạng thái kết nối MongoDB
        self.connection_status = tk.StringVar(value="Trạng thái DB: Đang kiểm tra...")
        ttk.Label(self.status_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=10)
        
        # Kiểm tra kết nối MongoDB
        self.check_mongodb_connection()
        
        # Tạo tab control
        self.tab_control = ttk.Notebook(root)
        
        # Tab 1: Quản lý Video
        self.tab_videos = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_videos, text="Quản lý Video")
        self.videos_tab = VideoTab(self.tab_videos, self.video_manager)
        
        # Tab 2: Quản lý Đối tượng
        self.tab_objects = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_objects, text="Quản lý Đối tượng")
        self.objects_tab = ObjectTab(self.tab_objects, self.video_manager)
        
        # Tab 3: Quản lý Phân đoạn
        self.tab_segments = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_segments, text="Quản lý Phân đoạn")
        self.segments_tab = SegmentTab(self.tab_segments, self.video_manager)
        
        # Tab 4: Tìm kiếm
        self.tab_search = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_search, text="Tìm kiếm")
        search_type_var = tk.StringVar(value="find_video_with_object")
        self.search_tab = SearchTab(self.tab_search, self.video_manager, search_type_var)
        
        # Tab 5: Nhận diện đối tượng
        self.tab_detection = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_detection, text="Nhận diện đối tượng")
        self.detection_tab = DetectionTab(self.tab_detection, self.video_manager)

        # Tab 6: Thống kê
        self.tab_stats = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_stats, text="Thống kê")
        self.stats_tab = StatsTab(self.tab_stats, self.video_manager)
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Menu
        self.setup_menu()
    
    def setup_menu(self):
        """Thiết lập menu chính của ứng dụng"""
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Lưu dữ liệu", command=self.save_data)
        self.file_menu.add_command(label="Tải dữ liệu", command=self.load_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Xuất báo cáo", command=self.export_report)
        self.file_menu.add_command(label="Xuất CSV", command=self.export_csv)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Cài đặt DB", command=self.show_db_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Thoát", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Hướng dẫn sử dụng", command=self.show_help)
        self.help_menu.add_command(label="Thông tin", command=self.show_about)
        self.menu_bar.add_cascade(label="Trợ giúp", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def check_mongodb_connection(self):
        """Kiểm tra kết nối với MongoDB"""
        try:
            from ..mongodb import get_mongodb_client
            client = get_mongodb_client()
            # Thử ping để kiểm tra kết nối
            client.db.command('ping')
            self.connection_status.set("Trạng thái DB: MongoDB đã kết nối")
            return True
        except Exception as e:
            logger.error(f"Lỗi kết nối MongoDB: {e}")
            self.connection_status.set("Trạng thái DB: Lỗi kết nối MongoDB")
            return False
    
    def show_db_settings(self):
        """Hiển thị cửa sổ cài đặt kết nối DB"""
        show_db_settings(self.root, self.check_mongodb_connection)
    
    def save_data(self):
        """Lưu dữ liệu vào cơ sở dữ liệu"""
        from ..persistence import save_data
        if save_data(self.video_manager):
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu!")
        else:
            messagebox.showerror("Lỗi", "Không thể lưu dữ liệu!")
    
    def load_data(self):
        """Tải dữ liệu từ cơ sở dữ liệu"""
        from ..persistence import load_data
        loaded_manager = load_data()
        if loaded_manager:
            self.video_manager = loaded_manager
            # Cập nhật dữ liệu cho tất cả các tab
            self.videos_tab.refresh_data(self.video_manager)
            self.objects_tab.refresh_data(self.video_manager)
            self.segments_tab.refresh_data(self.video_manager)
            self.stats_tab.refresh_data(self.video_manager)
            messagebox.showinfo("Thành công", "Đã tải dữ liệu!")
        else:
            messagebox.showerror("Lỗi", "Không thể tải dữ liệu!")
    
    def export_report(self):
        """Xuất báo cáo thống kê"""
        from ..utils import generate_report
        filename = generate_report(self.video_manager)
        messagebox.showinfo("Thành công", f"Đã xuất báo cáo: {filename}")
    
    def export_csv(self):
        """Xuất dữ liệu sang CSV"""
        from ..utils import export_to_csv
        filename = export_to_csv(self.video_manager)
        messagebox.showinfo("Thành công", f"Đã xuất dữ liệu CSV: {filename}")
    
    def show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        help_text = """
        Hướng dẫn sử dụng hệ thống cơ sở dữ liệu video:
        
        1. Quản lý Video: Thêm, chỉnh sửa và xóa video
        2. Quản lý Đối tượng: Thêm, chỉnh sửa và xóa đối tượng
        3. Quản lý Phân đoạn: Thêm và xóa phân đoạn xuất hiện của đối tượng trong video
        4. Tìm kiếm: Tìm kiếm video hoặc đối tượng
        5. Nhận diện đối tượng: Phân tích video để tự động nhận diện đối tượng
        6. Thống kê: Xem thống kê về dữ liệu
        
        Menu File:
        - Lưu/Tải dữ liệu: Lưu và tải dữ liệu từ MongoDB hoặc file JSON
        - Xuất báo cáo/CSV: Xuất dữ liệu sang định dạng khác
        - Cài đặt DB: Cấu hình kết nối MongoDB
        """
        messagebox.showinfo("Hướng dẫn sử dụng", help_text)
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        about_text = """
        Hệ thống Cơ sở dữ liệu Video v2.0
        
        Phát triển dựa trên cấu trúc Frame Segment Tree và MongoDB.
        
        © 2025
        """
        messagebox.showinfo("Thông tin", about_text)