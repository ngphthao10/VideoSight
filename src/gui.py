# # src/gui.py (cập nhật)
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# import os
# import logging
# from .database import VideoManager
# from .persistence import save_data, load_data
# from .visualize import visualize_tree

# # Configure logging
# logger = logging.getLogger(__name__)

# class VideoDBApp:
#     def __init__(self, root, video_manager):
#         self.root = root
#         self.video_manager = video_manager
        
#         # Thiết lập cửa sổ chính
#         self.root.title("Hệ thống Cơ sở dữ liệu Video - MongoDB")
#         self.root.geometry("900x600")
        
#         # Frame trạng thái
#         self.status_frame = ttk.Frame(root)
#         self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
#         # Hiển thị trạng thái kết nối MongoDB
#         self.connection_status = tk.StringVar(value="Trạng thái DB: Đã kết nối")
#         ttk.Label(self.status_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=10)
        
#         # Kiểm tra kết nối MongoDB
#         self.check_mongodb_connection()
        
#         # Tạo tab control
#         self.tab_control = ttk.Notebook(root)
        
#         # Tab 1: Quản lý Video
#         self.tab_videos = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_videos, text="Quản lý Video")
#         self.setup_videos_tab()
        
#         # Tab 2: Quản lý Đối tượng
#         self.tab_objects = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_objects, text="Quản lý Đối tượng")
#         self.setup_objects_tab()
        
#         # Tab 3: Quản lý Phân đoạn
#         self.tab_segments = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_segments, text="Quản lý Phân đoạn")
#         self.setup_segments_tab()
        
#         # Tab 4: Tìm kiếm
#         self.tab_search = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_search, text="Tìm kiếm")
#         self.search_type_var = tk.StringVar(value="find_video_with_object")
#         self.setup_search_tab()
        
#         # Tab 5: Nhận diện đối tượng
#         self.tab_detection = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_detection, text="Nhận diện đối tượng")
#         self.setup_detection_tab()

#         # Tab 6: Thống kê
#         self.tab_stats = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_stats, text="Thống kê")
#         self.setup_stats_tab()
        
#         self.tab_control.pack(expand=1, fill="both")
        
#         # Menu
#         self.menu_bar = tk.Menu(root)
#         self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
#         self.file_menu.add_command(label="Lưu dữ liệu", command=self.save_data)
#         self.file_menu.add_command(label="Tải dữ liệu", command=self.load_data)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Xuất báo cáo", command=self.export_report)
#         self.file_menu.add_command(label="Xuất CSV", command=self.export_csv)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Cài đặt DB", command=self.show_db_settings)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Thoát", command=root.quit)
#         self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
#         self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
#         self.help_menu.add_command(label="Hướng dẫn sử dụng", command=self.show_help)
#         self.help_menu.add_command(label="Thông tin", command=self.show_about)
#         self.menu_bar.add_cascade(label="Trợ giúp", menu=self.help_menu)
        
#         root.config(menu=self.menu_bar)
    
#     def check_mongodb_connection(self):
#         """Kiểm tra kết nối với MongoDB"""
#         try:
#             from .mongodb import get_mongodb_client
#             client = get_mongodb_client()
#             # Thử ping để kiểm tra kết nối
#             client.db.command('ping')
#             self.connection_status.set("Trạng thái DB: MongoDB đã kết nối")
#             return True
#         except Exception as e:
#             logger.error(f"Lỗi kết nối MongoDB: {e}")
#             self.connection_status.set("Trạng thái DB: Lỗi kết nối MongoDB")
#             return False
    
#     def show_db_settings(self):
#         """Hiển thị cửa sổ cài đặt kết nối DB"""
#         # Tạo cửa sổ cài đặt
#         settings_window = tk.Toplevel(self.root)
#         settings_window.title("Cài đặt kết nối MongoDB")
#         settings_window.geometry("500x300")
#         settings_window.grab_set()  # Modal window
        
#         # Frame chính
#         main_frame = ttk.Frame(settings_window, padding=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
        
#         # Tiêu đề
#         ttk.Label(main_frame, text="Cài đặt kết nối MongoDB", font=("Arial", 14, "bold")).pack(pady=10)
        
#         # Trường nhập liệu
#         form_frame = ttk.Frame(main_frame)
#         form_frame.pack(fill=tk.BOTH, pady=10)
        
#         # Connection string
#         ttk.Label(form_frame, text="Connection string:").grid(row=0, column=0, sticky=tk.W, pady=5)
#         connection_var = tk.StringVar()
        
#         # Lấy connection string hiện tại
#         try:
#             from .config import MONGODB_URI
#             connection_var.set(MONGODB_URI)
#         except Exception:
#             connection_var.set("mongodb+srv://username:password@cluster.mongodb.net/videoDatabase")
        
#         ttk.Entry(form_frame, textvariable=connection_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        
#         # Database name
#         ttk.Label(form_frame, text="Tên Database:").grid(row=1, column=0, sticky=tk.W, pady=5)
#         db_name_var = tk.StringVar(value="videoDatabase")
#         ttk.Entry(form_frame, textvariable=db_name_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        
#         # Tùy chọn lưu trữ
#         storage_frame = ttk.LabelFrame(main_frame, text="Phương thức lưu trữ")
#         storage_frame.pack(fill=tk.X, pady=10)
        
#         storage_var = tk.BooleanVar(value=True)  # True = MongoDB, False = JSON
#         ttk.Radiobutton(storage_frame, text="Sử dụng MongoDB", variable=storage_var, value=True).pack(anchor=tk.W, padx=20, pady=5)
#         ttk.Radiobutton(storage_frame, text="Sử dụng JSON (local)", variable=storage_var, value=False).pack(anchor=tk.W, padx=20, pady=5)
        
#         # Nút lưu và kiểm tra kết nối
#         button_frame = ttk.Frame(main_frame)
#         button_frame.pack(fill=tk.X, pady=10)
        
#         def save_settings():
#             try:
#                 # Cập nhật file config
#                 with open("src/config.py", "w", encoding="utf-8") as f:
#                     f.write(f"# src/config.py\n")
#                     f.write(f"# Cấu hình cho MongoDB Atlas\n\n")
#                     f.write(f"# Constants for MongoDB connection\n")
#                     f.write(f"MONGODB_URI = \"{connection_var.get()}\"\n")
#                     f.write(f"DATABASE_NAME = \"{db_name_var.get()}\"\n\n")
#                     f.write(f"# Collection names\n")
#                     f.write(f"VIDEO_COLLECTION = \"videos\"\n")
#                     f.write(f"OBJECT_COLLECTION = \"objects\"\n")
#                     f.write(f"SEGMENT_COLLECTION = \"segments\"\n")
#                     f.write(f"\n# Use MongoDB or JSON\n")
#                     f.write(f"USE_MONGODB = {storage_var.get()}\n")
                
#                 # Cập nhật persistence.py
#                 with open("src/persistence.py", "r", encoding="utf-8") as f:
#                     content = f.read()
                
#                 # Cập nhật flag USE_MONGODB
#                 import re
#                 new_content = re.sub(
#                     r"USE_MONGODB = (True|False)", 
#                     f"USE_MONGODB = {storage_var.get()}", 
#                     content
#                 )
                
#                 with open("src/persistence.py", "w", encoding="utf-8") as f:
#                     f.write(new_content)
                
#                 messagebox.showinfo("Thành công", "Đã lưu cài đặt. Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
#                 settings_window.destroy()
                
#             except Exception as e:
#                 messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
        
#         def test_connection():
#             try:
#                 from pymongo import MongoClient
#                 import certifi
                
#                 # Thử kết nối
#                 client = MongoClient(connection_var.get(), tlsCAFile=certifi.where())
#                 client.admin.command('ping')
#                 messagebox.showinfo("Thành công", "Kết nối đến MongoDB thành công!")
#             except Exception as e:
#                 messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến MongoDB: {str(e)}")
        
#         ttk.Button(button_frame, text="Kiểm tra kết nối", command=test_connection).pack(side=tk.LEFT, padx=5)
#         ttk.Button(button_frame, text="Lưu cài đặt", command=save_settings).pack(side=tk.RIGHT, padx=5)
#         ttk.Button(button_frame, text="Hủy", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
#     def setup_videos_tab(self):
#         # Frame bên trái: Danh sách video
#         left_frame = ttk.Frame(self.tab_videos)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Video", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame tìm kiếm
#         search_frame = ttk.Frame(left_frame)
#         search_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
#         self.video_search_var = tk.StringVar()
#         ttk.Entry(search_frame, textvariable=self.video_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
#         ttk.Button(search_frame, text="Tìm", command=self.search_videos).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách video
#         columns = ("ID", "Tên", "Số Frame")
#         self.videos_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.videos_tree.heading(col, text=col)
#             self.videos_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.videos_tree.yview)
#         self.videos_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.videos_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.videos_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_videos_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa video
#         ttk.Button(button_frame, text="Xóa", command=self.delete_video).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm/Chỉnh sửa video
#         right_frame = ttk.Frame(self.tab_videos)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm/Chỉnh sửa Video", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm video
#         ttk.Label(right_frame, text="Tên video:").pack(anchor=tk.W, pady=5)
#         self.video_name_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.video_name_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Số frame:").pack(anchor=tk.W, pady=5)
#         self.video_frames_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.video_frames_var, width=30).pack(fill=tk.X, pady=5)
        
#         # Nút thêm/cập nhật
#         self.video_action_button = ttk.Button(right_frame, text="Thêm Video", command=self.add_video)
#         self.video_action_button.pack(pady=10)
        
#         # Biến để theo dõi ID video đang chỉnh sửa
#         self.editing_video_id = None
        
#         # Nút hủy chỉnh sửa
#         self.cancel_edit_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_video)
#         self.cancel_edit_button.pack(pady=5)
#         self.cancel_edit_button.pack_forget()  # Ẩn đi ban đầu
        
#         # Nút hiển thị cây phân đoạn
#         ttk.Button(right_frame, text="Hiển thị Frame Segment Tree", command=self.show_tree).pack(pady=5)
        
#         # Trường hiển thị chi tiết cây
#         ttk.Label(right_frame, text="Cấu trúc cây:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
#         self.tree_text = tk.Text(right_frame, height=15, width=40)
#         self.tree_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
#         # Làm mới danh sách video
#         self.refresh_videos_list()
    
#     def setup_objects_tab(self):
#         # Frame bên trái: Danh sách đối tượng
#         left_frame = ttk.Frame(self.tab_objects)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame tìm kiếm
#         search_frame = ttk.Frame(left_frame)
#         search_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
#         self.object_search_var = tk.StringVar()
#         ttk.Entry(search_frame, textvariable=self.object_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
#         ttk.Button(search_frame, text="Tìm", command=self.search_objects).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách đối tượng
#         columns = ("ID", "Tên", "Loại")
#         self.objects_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.objects_tree.heading(col, text=col)
#             self.objects_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.objects_tree.yview)
#         self.objects_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.objects_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.objects_tree.bind("<<TreeviewSelect>>", self.on_object_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_objects_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa đối tượng
#         ttk.Button(button_frame, text="Xóa", command=self.delete_object).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm/Chỉnh sửa đối tượng
#         right_frame = ttk.Frame(self.tab_objects)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm/Chỉnh sửa Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm đối tượng
#         ttk.Label(right_frame, text="Tên đối tượng:").pack(anchor=tk.W, pady=5)
#         self.object_name_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.object_name_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Loại đối tượng:").pack(anchor=tk.W, pady=5)
#         self.object_type_var = tk.StringVar()
#         object_types = ["Person", "Vehicle", "Object", "Animal", "Other"]
#         ttk.Combobox(right_frame, textvariable=self.object_type_var, values=object_types, width=28).pack(fill=tk.X, pady=5)
        
#         # Nút thêm/cập nhật
#         self.object_action_button = ttk.Button(right_frame, text="Thêm Đối tượng", command=self.add_object)
#         self.object_action_button.pack(pady=10)
        
#         # Biến để theo dõi ID đối tượng đang chỉnh sửa
#         self.editing_object_id = None
        
#         # Nút hủy chỉnh sửa
#         self.cancel_edit_obj_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_object)
#         self.cancel_edit_obj_button.pack(pady=5)
#         self.cancel_edit_obj_button.pack_forget()  # Ẩn đi ban đầu
        
#         # Frame hiển thị phân đoạn của đối tượng
#         segments_frame = ttk.LabelFrame(right_frame, text="Phân đoạn của đối tượng")
#         segments_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
#         # Treeview hiển thị phân đoạn
#         columns = ("Video", "Frame Bắt đầu", "Frame Kết thúc")
#         self.object_segments_tree = ttk.Treeview(segments_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.object_segments_tree.heading(col, text=col)
#             self.object_segments_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(segments_frame, orient="vertical", command=self.object_segments_tree.yview)
#         self.object_segments_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.object_segments_tree.pack(fill=tk.BOTH, expand=True)
        
#         # Làm mới danh sách đối tượng
#         self.refresh_objects_list()

#     def setup_segments_tab(self):
#         # Frame bên trái: Danh sách phân đoạn
#         left_frame = ttk.Frame(self.tab_segments)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Phân đoạn", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame lọc
#         filter_frame = ttk.Frame(left_frame)
#         filter_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(filter_frame, text="Lọc theo video:").pack(side=tk.LEFT, padx=5)
#         self.filter_video_var = tk.StringVar()
#         self.filter_video_combo = ttk.Combobox(filter_frame, textvariable=self.filter_video_var, width=20)
#         self.filter_video_combo.pack(side=tk.LEFT, padx=5)
        
#         ttk.Label(filter_frame, text="Lọc theo đối tượng:").pack(side=tk.LEFT, padx=5)
#         self.filter_object_var = tk.StringVar()
#         self.filter_object_combo = ttk.Combobox(filter_frame, textvariable=self.filter_object_var, width=20)
#         self.filter_object_combo.pack(side=tk.LEFT, padx=5)
        
#         ttk.Button(filter_frame, text="Lọc", command=self.filter_segments).pack(side=tk.LEFT, padx=5)
#         ttk.Button(filter_frame, text="Xóa bộ lọc", command=self.clear_segment_filters).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách phân đoạn
#         columns = ("ID", "Video", "Đối tượng", "Frame Bắt đầu", "Frame Kết thúc")
#         self.segments_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.segments_tree.heading(col, text=col)
#             self.segments_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.segments_tree.yview)
#         self.segments_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.segments_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.segments_tree.bind("<<TreeviewSelect>>", self.on_segment_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_segments_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa phân đoạn
#         ttk.Button(button_frame, text="Xóa", command=self.delete_segment).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm phân đoạn
#         right_frame = ttk.Frame(self.tab_segments)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm Phân đoạn Mới", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm phân đoạn
#         # Video
#         ttk.Label(right_frame, text="Video:").pack(anchor=tk.W, pady=5)
#         self.segment_video_var = tk.StringVar()
#         self.segment_video_combo = ttk.Combobox(right_frame, textvariable=self.segment_video_var, width=28)
#         self.segment_video_combo.pack(fill=tk.X, pady=5)
        
#         # Đối tượng
#         ttk.Label(right_frame, text="Đối tượng:").pack(anchor=tk.W, pady=5)
#         self.segment_object_var = tk.StringVar()
#         self.segment_object_combo = ttk.Combobox(right_frame, textvariable=self.segment_object_var, width=28)
#         self.segment_object_combo.pack(fill=tk.X, pady=5)
        
#         # Frame bắt đầu và kết thúc
#         ttk.Label(right_frame, text="Frame bắt đầu:").pack(anchor=tk.W, pady=5)
#         self.start_frame_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.start_frame_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Frame kết thúc:").pack(anchor=tk.W, pady=5)
#         self.end_frame_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.end_frame_var, width=30).pack(fill=tk.X, pady=5)
        
#         # Nút thêm
#         ttk.Button(right_frame, text="Thêm Phân đoạn", command=self.add_segment).pack(pady=10)
        
#         # Làm mới danh sách combobox
#         self.refresh_combo_lists()
        
#         # Làm mới danh sách phân đoạn
#         self.refresh_segments_list()
# # Treeview để hiển thị thống kê đối tượng
#         columns = ("Loại đối tượng", "Số lượng", "Tỷ lệ (%)")
#         self.objects_stats_tree = ttk.Treeview(objects_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.objects_stats_tree.heading(col, text=col)
#             self.objects_stats_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(objects_frame, orient="vertical", command=self.objects_stats_tree.yview)
#         self.objects_stats_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.objects_stats_tree.pack(fill=tk.BOTH, expand=True)
        
#         # Tab thống kê theo video
#         videos_tab = ttk.Frame(stats_notebook)
#         stats_notebook.add(videos_tab, text="Video")
        
#         # Tạo frame cho thống kê theo video
#         videos_frame = ttk.LabelFrame(videos_tab, text="Thống kê theo video")
#         videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Treeview để hiển thị thống kê video
#         columns = ("ID", "Tên video", "Số frame", "Số đối tượng", "Số phân đoạn")
#         self.videos_stats_tree = ttk.Treeview(videos_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.videos_stats_tree.heading(col, text=col)
#             self.videos_stats_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(videos_frame, orient="vertical", command=self.videos_stats_tree.yview)
#         self.videos_stats_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.videos_stats_tree.pack(fill=tk.BOTH, expand=True)
        
#         # Cập nhật thống kê
#         self.update_statistics()

#     def setup_detection_tab(self):
#         # Frame chính
#         detection_frame = ttk.Frame(self.tab_detection)
#         detection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(detection_frame, text="Nhận diện đối tượng trong Video", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame chọn video
#         video_select_frame = ttk.LabelFrame(detection_frame, text="Chọn video để phân tích")
#         video_select_frame.pack(fill=tk.X, pady=10)
        
#         ttk.Button(video_select_frame, text="Chọn file video", command=self.select_video_file).pack(pady=10)
        
#         self.selected_video_var = tk.StringVar()
#         ttk.Entry(video_select_frame, textvariable=self.selected_video_var, width=50, state="readonly").pack(pady=5, padx=10, fill=tk.X)
        
#         # Frame tùy chọn nhận diện
#         detection_options = ttk.LabelFrame(detection_frame, text="Tùy chọn nhận diện")
#         detection_options.pack(fill=tk.X, pady=10)
        
#         # Model nhận diện
#         ttk.Label(detection_options, text="Model nhận diện:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
#         self.model_var = tk.StringVar(value="YOLOv5")
#         models = ["YOLOv5", "YOLOv8", "SSD MobileNet", "Faster R-CNN"]
#         ttk.Combobox(detection_options, textvariable=self.model_var, values=models, width=20).grid(row=0, column=1, padx=5, pady=5)
        
#         # Ngưỡng tin cậy
#         ttk.Label(detection_options, text="Ngưỡng tin cậy:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
#         self.confidence_var = tk.DoubleVar(value=0.5)
#         confidence_scale = ttk.Scale(detection_options, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.confidence_var, length=200)
#         confidence_scale.grid(row=1, column=1, padx=5, pady=5)
        
#         self.confidence_label = ttk.Label(detection_options, text="0.50")
#         self.confidence_label.grid(row=1, column=2, padx=5, pady=5)
        
#         # Cập nhật label khi thay đổi giá trị
#         def update_confidence_label(*args):
#             self.confidence_label.config(text=f"{self.confidence_var.get():.2f}")
        
#         self.confidence_var.trace_add("write", update_confidence_label)
        
#         # Tần suất lấy mẫu
#         ttk.Label(detection_options, text="Tần suất lấy mẫu (frames):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
#         self.sample_rate_var = tk.IntVar(value=30)
#         ttk.Entry(detection_options, textvariable=self.sample_rate_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
#         # Nút bắt đầu phân tích
#         ttk.Button(detection_frame, text="Bắt đầu nhận diện", command=self.start_detection).pack(pady=10)
        
#         # Thanh tiến trình
#         progress_frame = ttk.Frame(detection_frame)
#         progress_frame.pack(fill=tk.X, pady=10)
        
#         self.progress_var = tk.DoubleVar()
#         self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var)
#         self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
#         self.progress_label = ttk.Label(progress_frame, text="0%")
#         self.progress_label.pack(side=tk.RIGHT, padx=5)
        
#         # Kết quả phân tích
#         result_frame = ttk.LabelFrame(detection_frame, text="Kết quả nhận diện")
#         result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
#         # Treeview để hiển thị kết quả
#         columns = ("Frame", "Đối tượng", "Tin cậy", "Vị trí")
#         self.detection_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.detection_tree.heading(col, text=col)
#             self.detection_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.detection_tree.yview)
#         self.detection_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.detection_tree.pack(fill=tk.BOTH, expand=True)
        
#         # Frame nút
#         button_frame = ttk.Frame(detection_frame)
#         button_frame.pack(fill=tk.X, pady=10)
        
#         # Nút lưu kết quả
#         ttk.Button(button_frame, text="Lưu kết quả vào cơ sở dữ liệu", command=self.save_detection_results).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa kết quả
#         ttk.Button(button_frame, text="Xóa kết quả", command=self.clear_detection_results).pack(side=tk.LEFT, padx=5)
        
#     # Các phương thức callback và tiện ích
#     def refresh_videos_list(self):
#         # Xóa dữ liệu cũ
#         for item in self.videos_tree.get_children():
#             self.videos_tree.delete(item)
        
#         # Lấy danh sách video
#         videos = self.video_manager.get_all_videos()
        
#         # Thêm vào treeview
#         for vid, name, frames in videos:
#             self.videos_tree.insert("", tk.END, values=(vid, name, frames))
    
#     def refresh_objects_list(self):
#         # Xóa dữ liệu cũ
#         for item in self.objects_tree.get_children():
#             self.objects_tree.delete(item)
        
#         # Lấy danh sách đối tượng
#         objects = self.video_manager.get_all_objects()
        
#         # Thêm vào treeview
#         for oid, name, obj_type in objects:
#             self.objects_tree.insert("", tk.END, values=(oid, name, obj_type))
    
#     def refresh_segments_list(self):
#         # Xóa dữ liệu cũ
#         for item in self.segments_tree.get_children():
#             self.segments_tree.delete(item)
        
#         # Lấy danh sách phân đoạn
#         segments = self.video_manager.segments
        
#         # Thêm vào treeview
#         count = 1
#         for vid, oid, start, end in segments:
#             video_name = self.video_manager.videos[vid][0]
#             object_name = self.video_manager.objects[oid][0]
#             self.segments_tree.insert("", tk.END, values=(count, video_name, object_name, start, end))
#             count += 1
    
#     def filter_segments(self):
#         """Lọc phân đoạn theo video và đối tượng"""
#         # Xóa dữ liệu cũ
#         for item in self.segments_tree.get_children():
#             self.segments_tree.delete(item)
        
#         # Lấy giá trị lọc
#         video_filter = self.filter_video_var.get().split(": ")[0] if ": " in self.filter_video_var.get() else ""
#         object_filter = self.filter_object_var.get().split(": ")[0] if ": " in self.filter_object_var.get() else ""
        
#         try:
#             vid_filter = int(video_filter) if video_filter else None
#             oid_filter = int(object_filter) if object_filter else None
#         except ValueError:
#             vid_filter = None
#             oid_filter = None
        
#         # Lấy danh sách phân đoạn
#         segments = self.video_manager.segments
        
#         # Thêm vào treeview
#         count = 1
#         for vid, oid, start, end in segments:
#             # Áp dụng bộ lọc
#             if (vid_filter is None or vid == vid_filter) and (oid_filter is None or oid == oid_filter):
#                 video_name = self.video_manager.videos[vid][0]
#                 object_name = self.video_manager.objects[oid][0]
#                 self.segments_tree.insert("", tk.END, values=(count, video_name, object_name, start, end))
#                 count += 1
    
#     def clear_segment_filters(self):
#         """Xóa bộ lọc phân đoạn"""
#         self.filter_video_var.set("")
#         self.filter_object_var.set("")
#         self.refresh_segments_list()
    
#     def refresh_combo_lists(self):
#         # Làm mới danh sách video trong combobox
#         videos = self.video_manager.get_all_videos()
#         video_names = [f"{vid}: {name}" for vid, name, _ in videos]
#         self.segment_video_combo['values'] = video_names
#         self.filter_video_combo['values'] = [""] + video_names
        
#         # Làm mới danh sách đối tượng trong combobox
#         objects = self.video_manager.get_all_objects()
#         object_names = [f"{oid}: {name}" for oid, name, _ in objects]
#         self.segment_object_combo['values'] = object_names
#         self.filter_object_combo['values'] = [""] + object_names
    
#     def on_video_select(self, event):
#         # Lấy item được chọn
#         selected_item = self.videos_tree.selection()
#         if not selected_item:
#             return
        
#         # Lấy thông tin video
#         video_values = self.videos_tree.item(selected_item[0], "values")
#         vid = int(video_values[0])
        
#         # Hiển thị thông tin chi tiết
#         self.video_name_var.set(video_values[1])
#         self.video_frames_var.set(video_values[2])
        
#         # Cập nhật trạng thái chỉnh sửa
#         self.editing_video_id = vid
#         self.video_action_button.config(text="Cập nhật Video")
        
#         # Hiển thị nút hủy
#         self.cancel_edit_button.pack(pady=5)
    
#     def on_object_select(self, event):
#         # Lấy item được chọn
#         selected_item = self.objects_tree.selection()
#         if not selected_item:
#             return
        
#         # Lấy thông tin đối tượng
#         object_values = self.objects_tree.item(selected_item[0], "values")
#         oid = int(object_values[0])
        
#         # Hiển thị thông tin chi tiết
#         self.object_name_var.set(object_values[1])
#         self.object_type_var.set(object_values[2])
        
#         # Cập nhật trạng thái chỉnh sửa
#         self.editing_object_id = oid
#         self.object_action_button.config(text="Cập nhật Đối tượng")
        
#         # Hiển thị nút hủy
#         self.cancel_edit_obj_button.pack(pady=5)
        
#         # Hiển thị các phân đoạn của đối tượng
#         self.display_object_segments(oid)
    
#     def display_object_segments(self, object_id):
#         # Xóa dữ liệu cũ
#         for item in self.object_segments_tree.get_children():
#             self.object_segments_tree.delete(item)
        
#         # Lấy các phân đoạn của đối tượng
#         segments = self.video_manager.get_segments_for_object(object_id)
        
#         # Thêm vào treeview
#         for vid, video_name, start, end in segments:
#             self.object_segments_tree.insert("", tk.END, values=(video_name, start, end))
    
#     def on_segment_select(self, event):
#         # Lấy item được chọn
#         selected_item = self.segments_tree.selection()
#         if not selected_item:
#             return
        
#         # Lấy thông tin phân đoạn
#         segment_values = self.segments_tree.item(selected_item[0], "values")
#         # ID, Video, Đối tượng, Start, End
        
#         # Hiển thị thông tin chi tiết cho mục đích xem
#         video_name = segment_values[1]
#         object_name = segment_values[2]
#         start_frame = segment_values[3]
#         end_frame = segment_values[4]
        
#         # Tìm video_id và object_id
#         video_id = None
#         for vid, (name, _, _) in self.video_manager.videos.items():
#             if name == video_name:
#                 video_id = vid
#                 break
        
#         object_id = None
#         for oid, (name, _) in self.video_manager.objects.items():
#             if name == object_name:
#                 object_id = oid
#                 break
        
#         if video_id is not None and object_id is not None:
#             # Cập nhật combobox
#             for i, value in enumerate(self.segment_video_combo['values']):
#                 if value.startswith(f"{video_id}: "):
#                     self.segment_video_combo.current(i)
#                     break
            
#             for i, value in enumerate(self.segment_object_combo['values']):
#                 if value.startswith(f"{object_id}: "):
#                     self.segment_object_combo.current(i)
#                     break
            
#             # Cập nhật các trường khác
#             self.start_frame_var.set(start_frame)
#             self.end_frame_var.set(end_frame)
    
#     def add_video(self):
#         # Lấy thông tin từ form
#         video_name = self.video_name_var.get().strip()
#         try:
#             frames = int(self.video_frames_var.get().strip())
#         except ValueError:
#             messagebox.showerror("Lỗi", "Không thể lưu dữ liệu!")
    
#     def load_data(self):
#         from .persistence import load_data
#         loaded_manager = load_data()
#         if loaded_manager:
#             self.video_manager = loaded_manager
#             self.refresh_videos_list()
#             self.refresh_objects_list()
#             self.refresh_segments_list()
#             self.refresh_combo_lists()
#             messagebox.showinfo("Thành công", "Đã tải dữ liệu!")
#         else:
#             messagebox.showerror("Lỗi", "Không thể tải dữ liệu!")
    
#     def export_report(self):
#         from .utils import generate_report
#         filename = generate_report(self.video_manager)
#         messagebox.showinfo("Thành công", f"Đã xuất báo cáo: {filename}")
    
#     def export_csv(self):
#         from .utils import export_to_csv
#         filename = export_to_csv(self.video_manager)
#         messagebox.showinfo("Thành công", f"Đã xuất dữ liệu CSV: {filename}")
    
#     def update_search_conditions(self):
#         # Lấy kiểu tìm kiếm hiện tại
#         search_type = self.search_type_var.get()
        
#         # Ẩn tất cả các frame điều kiện
#         self.object_search_frame.pack_forget()
#         self.video_search_frame.pack_forget()
#         if hasattr(self, 'advanced_search_frame'):
#             self.advanced_search_frame.pack_forget()
        
#         # Hiển thị frame phù hợp
#         if search_type == "find_video_with_object":
#             self.object_search_frame.pack(fill=tk.X, pady=10)
#         elif search_type == "find_objects_in_video":
#             self.video_search_frame.pack(fill=tk.X, pady=10)
#         elif search_type == "advanced_search":
#             self.advanced_search_frame.pack(fill=tk.X, pady=10)
    
#     def search_videos(self):
#         """Tìm kiếm video theo tên"""
#         search_term = self.video_search_var.get().strip()
#         if not search_term:
#             self.refresh_videos_list()
#             return
        
#         # Tìm kiếm
#         results = self.video_manager.search_videos_by_name(search_term)
        
#         # Hiển thị kết quả
#         for item in self.videos_tree.get_children():
#             self.videos_tree.delete(item)
        
#         for vid, name, frames in results:
#             self.videos_tree.insert("", tk.END, values=(vid, name, frames))
    
#     def search_objects(self):
#         """Tìm kiếm đối tượng theo tên"""
#         search_term = self.object_search_var.get().strip()
#         if not search_term:
#             self.refresh_objects_list()
#             return
        
#         # Tìm kiếm
#         results = self.video_manager.search_objects_by_name(search_term)
        
#         # Hiển thị kết quả
#         for item in self.objects_tree.get_children():
#             self.objects_tree.delete(item)
        
#         for oid, name, obj_type in results:
#             self.objects_tree.insert("", tk.END, values=(oid, name, obj_type))
    
#     def perform_search(self):
#         # Lấy kiểu tìm kiếm
#         search_type = self.search_type_var.get()
        
#         # Xóa kết quả cũ
#         for item in self.result_tree.get_children():
#             self.result_tree.delete(item)
        
#         # Thiết lập cột phù hợp
#         if search_type == "find_video_with_object":
#             columns = ("Video ID", "Tên Video", "Frame Bắt đầu", "Frame Kết thúc")
#             self.result_tree["columns"] = columns
#             for col in columns:
#                 self.result_tree.heading(col, text=col)
#                 self.result_tree.column(col, width=100)
            
#             # Thực hiện tìm kiếm
#             object_name = self.search_object_var.get().strip()
#             if not object_name:
#                 messagebox.showerror("Lỗi", "Vui lòng nhập tên đối tượng!")
#                 return
            
#             results = self.video_manager.find_video_with_object(object_name)
            
#             if not results:
#                 messagebox.showinfo("Kết quả", f"Không tìm thấy video nào chứa '{object_name}'")
#             else:
#                 # Hiển thị kết quả
#                 for vid, name, start, end in results:
#                     self.result_tree.insert("", tk.END, values=(vid, name, start, end))
        
#         elif search_type == "find_objects_in_video":
#             columns = ("Đối tượng ID", "Tên Đối tượng", "Loại")
#             self.result_tree["columns"] = columns
#             for col in columns:
#                 self.result_tree.heading(col, text=col)
#                 self.result_tree.column(col, width=100)
            
#             # Thực hiện tìm kiếm
#             try:
#                 video_id = int(self.search_video_var.get().strip())
#                 start_frame = int(self.search_start_var.get().strip())
#                 end_frame = int(self.search_end_var.get().strip())
                
#                 results = self.video_manager.find_objects_in_video(video_id, start_frame, end_frame)
                
#                 if not results:
#                     messagebox.showinfo("Kết quả", f"Không tìm thấy đối tượng nào trong đoạn video từ frame {start_frame} đến {end_frame}")
#                 else:
#                     # Hiển thị kết quả
#                     for oid, name, obj_type in results:
#                         self.result_tree.insert("", tk.END, values=(oid, name, obj_type))
#             except ValueError:
#                 messagebox.showerror("Lỗi", "Vui lòng nhập ID và frame dạng số!")
        
#         elif search_type == "advanced_search":
#             columns = ("Video", "Đối tượng", "Loại", "Frame Bắt đầu", "Frame Kết thúc")
#             self.result_tree["columns"] = columns
#             for col in columns:
#                 self.result_tree.heading(col, text=col)
#                 self.result_tree.column(col, width=100)
            
#             # Thực hiện tìm kiếm nâng cao
#             object_type = self.adv_object_type_var.get()
#             if object_type == "Tất cả":
#                 object_type = ""
            
#             try:
#                 min_frame = int(self.adv_min_frame_var.get()) if self.adv_min_frame_var.get() else 0
#                 max_frame = int(self.adv_max_frame_var.get()) if self.adv_max_frame_var.get() else float('inf')
#             except ValueError:
#                 messagebox.showerror("Lỗi", "Frame phải là số nguyên!")
#                 return
            
#             # Tìm tất cả các đối tượng phù hợp với loại
#             matching_objects = []
#             if object_type:
#                 matching_objects = self.video_manager.search_objects_by_type(object_type)
#             else:
#                 matching_objects = self.video_manager.get_all_objects()
            
#             # Tìm các phân đoạn phù hợp
#             results = []
#             for oid, obj_name, obj_type in matching_objects:
#                 segments = self.video_manager.get_segments_for_object(oid)
#                 for vid, video_name, start, end in segments:
#                     # Kiểm tra điều kiện khoảng frame
#                     if (start <= max_frame and end >= min_frame):
#                         results.append((vid, video_name, oid, obj_name, obj_type, start, end))
            
#             if not results:
#                 messagebox.showinfo("Kết quả", "Không tìm thấy kết quả phù hợp")
#             else:
#                 # Hiển thị kết quả
#                 for vid, video_name, oid, obj_name, obj_type, start, end in results:
#                     self.result_tree.insert("", tk.END, values=(video_name, obj_name, obj_type, start, end))
    
#     def select_video_file(self):
#         # Mở hộp thoại chọn file
#         filetypes = [
#             ("Video files", "*.mp4 *.avi *.mov *.mkv"),
#             ("All files", "*.*")
#         ]
#         filepath = filedialog.askopenfilename(
#             title="Chọn file video",
#             filetypes=filetypes
#         )
        
#         if filepath:
#             self.selected_video_var.set(filepath)
    
#     def start_detection(self):
#         # Lấy đường dẫn file video
#         video_path = self.selected_video_var.get()
#         if not video_path:
#             messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
#             return
        
#         # Lấy tham số nhận diện
#         model_name = self.model_var.get()
#         confidence = self.confidence_var.get()
#         sample_rate = self.sample_rate_var.get()
        
#         # Xóa kết quả cũ
#         for item in self.detection_tree.get_children():
#             self.detection_tree.delete(item)
        
#         # Thực hiện nhận diện đối tượng
#         try:
#             # Thiết lập thanh tiến trình
#             self.progress_var.set(0)
#             self.progress_label.config(text="0%")
#             self.root.update_idletasks()
            
#             # Callback để cập nhật tiến trình
#             def update_progress(value):
#                 self.progress_var.set(value * 100)
#                 self.progress_label.config(text=f"{int(value * 100)}%")
#                 self.root.update_idletasks()
            
#             # Gọi hàm nhận diện
#             from .detection import detect_objects_in_video
#             self.detection_results = detect_objects_in_video(
#                 video_path, model_name, confidence, sample_rate, 
#                 progress_callback=update_progress
#             )
            
#             # Hiển thị kết quả
#             for result in self.detection_results:
#                 frame, obj_name, confidence, bbox = result
#                 self.detection_tree.insert("", tk.END, values=(
#                     frame, obj_name, f"{confidence:.2f}",
#                     f"({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})"
#                 ))
            
#             messagebox.showinfo("Thành công", f"Đã nhận diện {len(self.detection_results)} đối tượng trong video!")
        
#         except Exception as e:
#             messagebox.showerror("Lỗi", f"Không thể nhận diện đối tượng: {str(e)}")
#             logging.exception("Lỗi trong quá trình nhận diện")
    
#     def update_progress(self, value):
#         # Cập nhật thanh tiến trình
#         self.progress_var.set(value * 100)
#         self.root.update_idletasks()
    
#     def save_detection_results(self):
#         # Kiểm tra xem có kết quả không
#         if not hasattr(self, 'detection_results') or not self.detection_results:
#             messagebox.showerror("Lỗi", "Không có kết quả nhận diện nào để lưu!")
#             return
        
#         # Lấy đường dẫn video
#         video_path = self.selected_video_var.get()
#         video_name = os.path.basename(video_path)
        
#         # Thêm video mới nếu chưa có
#         import cv2
#         try:
#             # Lấy số frame của video
#             cap = cv2.VideoCapture(video_path)
#             total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#             cap.release()
#         except Exception:
#             total_frames = 1000  # Giá trị mặc định
        
#         video_id = self.video_manager.add_video_if_not_exists(video_name, total_frames)
        
#         # Xử lý từng kết quả nhận diện
#         added_count = 0
        
#         # Tạo dictionary để gom nhóm các phân đoạn theo đối tượng
#         segments_by_object = {}
        
#         for result in self.detection_results:
#             frame, obj_name, confidence, bbox = result
            
#             # Thêm đối tượng mới nếu chưa có
#             object_id = self.video_manager.add_object_if_not_exists(obj_name, "Detected")
            
#             # Thêm frame vào dictionary
#             if object_id not in segments_by_object:
#                 segments_by_object[object_id] = []
            
#             segments_by_object[object_id].append(frame)
        
#         # Tạo các phân đoạn liên tục
#         for object_id, frames in segments_by_object.items():
#             frames.sort()  # Sắp xếp các frame
            
#             # Gộp các frame liên tục thành phân đoạn
#             segments = []
#             start = frames[0]
#             prev = frames[0]
            
#             for i in range(1, len(frames)):
#                 # Nếu không liên tục, tạo phân đoạn mới
#                 if frames[i] > prev + 5:  # Threshold 5 frames
#                     segments.append((start, prev + 1))
#                     start = frames[i]
#                 prev = frames[i]
            
#             # Thêm phân đoạn cuối cùng
#             segments.append((start, prev + 1))
            
#             # Thêm các phân đoạn vào database
#             for start_frame, end_frame in segments:
#                 if self.video_manager.add_segment(video_id, object_id, start_frame, end_frame):
#                     added_count += 1
        
#         # Làm mới các danh sách
#         self.refresh_segments_list()
#         self.refresh_combo_lists()
        
#         messagebox.showinfo("Thành công", f"Đã lưu {added_count} phân đoạn vào cơ sở dữ liệu!")
    
#     def clear_detection_results(self):
#         """Xóa kết quả nhận diện"""
#         if hasattr(self, 'detection_results'):
#             del self.detection_results
        
#         # Xóa dữ liệu trên treeview
#         for item in self.detection_tree.get_children():
#             self.detection_tree.delete(item)
        
#         # Reset thanh tiến trình
#         self.progress_var.set(0)
#         self.progress_label.config(text="0%")
    
#     def show_help(self):
#         help_text = """
#         Hướng dẫn sử dụng hệ thống cơ sở dữ liệu video:
        
#         1. Quản lý Video: Thêm, chỉnh sửa và xóa video
#         2. Quản lý Đối tượng: Thêm, chỉnh sửa và xóa đối tượng
#         3. Quản lý Phân đoạn: Thêm và xóa phân đoạn xuất hiện của đối tượng trong video
#         4. Tìm kiếm: Tìm kiếm video hoặc đối tượng
#         5. Nhận diện đối tượng: Phân tích video để tự động nhận diện đối tượng
#         6. Thống kê: Xem thống kê về dữ liệu
        
#         Menu File:
#         - Lưu/Tải dữ liệu: Lưu và tải dữ liệu từ MongoDB hoặc file JSON
#         - Xuất báo cáo/CSV: Xuất dữ liệu sang định dạng khác
#         - Cài đặt DB: Cấu hình kết nối MongoDB
#         """
#         messagebox.showinfo("Hướng dẫn sử dụng", help_text)
    
#     def show_about(self):
#         about_text = """
#         Hệ thống Cơ sở dữ liệu Video v2.0
        
#         Phát triển dựa trên cấu trúc Frame Segment Tree và MongoDB.
        
#         © 2025
#         """
#         messagebox.showinfo("Thông tin", about_text)
    
#     def update_statistics(self):
#         """Cập nhật thống kê"""
#         # Thống kê tổng quan
#         videos = self.video_manager.get_all_videos()
#         objects = self.video_manager.get_all_objects()
#         segments = self.video_manager.segments
        
#         # Cập nhật các biến hiển thị
#         self.total_videos_var.set(f"Tổng số video: {len(videos)}")
#         self.total_objects_var.set(f"Tổng số đối tượng: {len(objects)}")
#         self.total_segments_var.set(f"Tổng số phân đoạn: {len(segments)}")
        
#         # Tính trung bình
#         if len(videos) > 0:
#             avg_segments = len(segments) / len(videos)
#             self.avg_segments_per_video_var.set(f"Số phân đoạn trung bình/video: {avg_segments:.2f}")
            
#             # Đếm số đối tượng xuất hiện trong mỗi video
#             objects_per_video = {}
#             for vid, oid, _, _ in segments:
#                 if vid not in objects_per_video:
#                     objects_per_video[vid] = set()
#                 objects_per_video[vid].add(oid)
            
#             total_objects = sum(len(objs) for objs in objects_per_video.values())
#             avg_objects = total_objects / len(videos)
#             self.avg_objects_per_video_var.set(f"Số đối tượng trung bình/video: {avg_objects:.2f}")
#         else:
#             self.avg_segments_per_video_var.set("Số phân đoạn trung bình/video: 0")
#             self.avg_objects_per_video_var.set("Số đối tượng trung bình/video: 0")
        
#         # Thống kê theo loại đối tượng
#         object_stats = self.video_manager.get_object_statistics()
        
#         # Xóa dữ liệu cũ
#         for item in self.objects_stats_tree.get_children():
#             self.objects_stats_tree.delete(item)
        
#         # Tính tổng số đối tượng
#         total_objects = len(objects)
        
#         # Thêm vào treeview
#         for obj_type, count in object_stats.items():
#             percentage = (count / total_objects) * 100 if total_objects > 0 else 0
#             self.objects_stats_tree.insert("", tk.END, values=(obj_type, count, f"{percentage:.2f}"))
        
#         # Thống kê theo video
#         video_stats = self.video_manager.get_video_statistics()
        
#         # Xóa dữ liệu cũ
#         for item in self.videos_stats_tree.get_children():
#             self.videos_stats_tree.delete(item)
        
#         # Thêm vào treeview
#         for vid, stats in video_stats.items():
#             self.videos_stats_tree.insert("", tk.END, values=(
#                 vid, 
#                 stats["name"], 
#                 stats["frames"], 
#                 stats["object_count"], 
#                 stats["segment_count"]
#             ))Số frame phải là số nguyên!")
#             return
        
#         if not video_name:
#             messagebox.showerror("Lỗi", "Tên video không được để trống!")
#             return
        
#         # Kiểm tra xem đang thêm mới hay cập nhật
#         if self.editing_video_id is not None:
#             # Cập nhật video
#             success = self.video_manager.update_video(self.editing_video_id, video_name, frames)
#             if success:
#                 messagebox.showinfo("Thành công", f"Đã cập nhật video ID: {self.editing_video_id}")
#             else:
#                 messagebox.showerror("Lỗi", "Không thể cập nhật video!")
#                 return
#         else:
#             # Thêm video mới
#             video_id = self.video_manager.add_video_if_not_exists(video_name, frames)
#             messagebox.showinfo("Thành công", f"Đã thêm video ID: {video_id}")
        
#         # Làm mới danh sách
#         self.refresh_videos_list()
#         self.refresh_combo_lists()
        
#         # Xóa form
#         self.cancel_edit_video()
    
#     def cancel_edit_video(self):
#         """Hủy chỉnh sửa video"""
#         self.editing_video_id = None
#         self.video_name_var.set("")
#         self.video_frames_var.set("")
#         self.video_action_button.config(text="Thêm Video")
#         self.cancel_edit_button.pack_forget()
    
#     def delete_video(self):
#         """Xóa video"""
#         selected_item = self.videos_tree.selection()
#         if not selected_item:
#             messagebox.showinfo("Thông báo", "Vui lòng chọn một video để xóa!")
#             return
        
#         # Lấy thông tin video
#         video_values = self.videos_tree.item(selected_item[0], "values")
#         vid = int(video_values[0])
        
#         # Xác nhận xóa
#         confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa video {video_values[1]} và tất cả phân đoạn liên quan?")
#         if not confirm:
#             return
        
#         # Xóa video
#         if self.video_manager.delete_video(vid):
#             messagebox.showinfo("Thành công", "Đã xóa video và các phân đoạn liên quan!")
            
#             # Làm mới danh sách
#             self.refresh_videos_list()
#             self.refresh_segments_list()
#             self.refresh_combo_lists()
            
#             # Xóa form nếu đang chỉnh sửa video này
#             if self.editing_video_id == vid:
#                 self.cancel_edit_video()
#         else:
#             messagebox.showerror("Lỗi", "Không thể xóa video!")
    
#     def add_object(self):
#         # Lấy thông tin từ form
#         object_name = self.object_name_var.get().strip()
#         object_type = self.object_type_var.get().strip()
        
#         if not object_name or not object_type:
#             messagebox.showerror("Lỗi", "Tên và loại đối tượng không được để trống!")
#             return
        
#         # Kiểm tra xem đang thêm mới hay cập nhật
#         if self.editing_object_id is not None:
#             # Cập nhật đối tượng
#             success = self.video_manager.update_object(self.editing_object_id, object_name, object_type)
#             if success:
#                 messagebox.showinfo("Thành công", f"Đã cập nhật đối tượng ID: {self.editing_object_id}")
#             else:
#                 messagebox.showerror("Lỗi", "Không thể cập nhật đối tượng!")
#                 return
#         else:
#             # Thêm đối tượng mới
#             object_id = self.video_manager.add_object_if_not_exists(object_name, object_type)
#             messagebox.showinfo("Thành công", f"Đã thêm đối tượng ID: {object_id}")
        
#         # Làm mới danh sách
#         self.refresh_objects_list()
#         self.refresh_combo_lists()
        
#         # Xóa form
#         self.cancel_edit_object()
    
#     def cancel_edit_object(self):
#         """Hủy chỉnh sửa đối tượng"""
#         self.editing_object_id = None
#         self.object_name_var.set("")
#         self.object_type_var.set("")
#         self.object_action_button.config(text="Thêm Đối tượng")
#         self.cancel_edit_obj_button.pack_forget()
        
#         # Xóa danh sách phân đoạn
#         for item in self.object_segments_tree.get_children():
#             self.object_segments_tree.delete(item)
    
#     def delete_object(self):
#         """Xóa đối tượng"""
#         selected_item = self.objects_tree.selection()
#         if not selected_item:
#             messagebox.showinfo("Thông báo", "Vui lòng chọn một đối tượng để xóa!")
#             return
        
#         # Lấy thông tin đối tượng
#         object_values = self.objects_tree.item(selected_item[0], "values")
#         oid = int(object_values[0])
        
#         # Xác nhận xóa
#         confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa đối tượng {object_values[1]} và tất cả phân đoạn liên quan?")
#         if not confirm:
#             return
        
#         # Xóa đối tượng
#         if self.video_manager.delete_object(oid):
#             messagebox.showinfo("Thành công", "Đã xóa đối tượng và các phân đoạn liên quan!")
            
#             # Làm mới danh sách
#             self.refresh_objects_list()
#             self.refresh_segments_list()
#             self.refresh_combo_lists()
            
#             # Xóa form nếu đang chỉnh sửa đối tượng này
#             if self.editing_object_id == oid:
#                 self.cancel_edit_object()
#         else:
#             messagebox.showerror("Lỗi", "Không thể xóa đối tượng!")
    
#     def add_segment(self):
#         # Lấy thông tin từ form
#         video_selection = self.segment_video_var.get()
#         object_selection = self.segment_object_var.get()
        
#         try:
#             # Trích xuất ID từ chuỗi selection
#             video_id = int(video_selection.split(":")[0])
#             object_id = int(object_selection.split(":")[0])
            
#             start_frame = int(self.start_frame_var.get())
#             end_frame = int(self.end_frame_var.get())
            
#             if start_frame >= end_frame:
#                 messagebox.showerror("Lỗi", "Frame bắt đầu phải nhỏ hơn frame kết thúc!")
#                 return
                
#         except (ValueError, IndexError):
#             messagebox.showerror("Lỗi", "Vui lòng chọn video, đối tượng và nhập frame hợp lệ!")
#             return
        
#         # Thêm phân đoạn mới
#         result = self.video_manager.add_segment(video_id, object_id, start_frame, end_frame)
        
#         if result:
#             # Làm mới danh sách
#             self.refresh_segments_list()
            
#             # Xóa form
#             self.start_frame_var.set("")
#             self.end_frame_var.set("")
            
#             messagebox.showinfo("Thành công", "Đã thêm phân đoạn mới!")
#         else:
#             messagebox.showerror("Lỗi", "Không thể thêm phân đoạn. ID video hoặc đối tượng không hợp lệ!")
    
#     def delete_segment(self):
#         """Xóa phân đoạn"""
#         selected_item = self.segments_tree.selection()
#         if not selected_item:
#             messagebox.showinfo("Thông báo", "Vui lòng chọn một phân đoạn để xóa!")
#             return
        
#         # Lấy thông tin phân đoạn
#         segment_values = self.segments_tree.item(selected_item[0], "values")
#         # ID, Video, Đối tượng, Start, End
        
#         # Tìm video_id và object_id
#         video_name = segment_values[1]
#         object_name = segment_values[2]
#         start_frame = int(segment_values[3])
#         end_frame = int(segment_values[4])
        
#         video_id = None
#         for vid, (name, _, _) in self.video_manager.videos.items():
#             if name == video_name:
#                 video_id = vid
#                 break
        
#         object_id = None
#         for oid, (name, _) in self.video_manager.objects.items():
#             if name == object_name:
#                 object_id = oid
#                 break
        
#         if video_id is None or object_id is None:
#             messagebox.showerror("Lỗi", "Không thể xác định video hoặc đối tượng!")
#             return
        
#         # Xác nhận xóa
#         confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa phân đoạn này?")
#         if not confirm:
#             return
        
#         # Xóa phân đoạn
#         if self.video_manager.delete_segment(video_id, object_id, start_frame, end_frame):
#             messagebox.showinfo("Thành công", "Đã xóa phân đoạn!")
            
#             # Làm mới danh sách
#             self.refresh_segments_list()
            
#             # Cập nhật danh sách phân đoạn của đối tượng nếu đang xem
#             if self.editing_object_id == object_id:
#                 self.display_object_segments(object_id)
#         else:
#             messagebox.showerror("Lỗi", "Không thể xóa phân đoạn!")
    
#     def show_tree(self):
#         # Lấy item được chọn
#         selected_item = self.videos_tree.selection()
#         if not selected_item:
#             messagebox.showinfo("Thông báo", "Vui lòng chọn một video từ danh sách!")
#             return
        
#         # Lấy ID video
#         video_values = self.videos_tree.item(selected_item[0], "values")
#         vid = int(video_values[0])
        
#         # Xóa nội dung hiện tại
#         self.tree_text.delete(1.0, tk.END)
        
#         # Lấy cây và hiển thị
#         if vid in self.video_manager.videos:
#             # Lưu đầu ra của hàm print_tree_node vào một biến
#             import io
#             from contextlib import redirect_stdout
            
#             buffer = io.StringIO()
#             with redirect_stdout(buffer):
#                 _, _, tree = self.video_manager.videos[vid]
#                 from .visualize import print_tree_node
#                 print_tree_node(tree.root)
            
#             # Lấy nội dung và hiển thị
#             tree_text = buffer.getvalue()
#             self.tree_text.insert(tk.END, tree_text)
#         else:
#             self.tree_text.insert(tk.END, "Video không tồn tại!")
    
#     def save_data(self):
#         from .persistence import save_data
#         if save_data(self.video_manager):
#             messagebox.showinfo("Thành công", "Đã lưu dữ liệu!")
#         else:
#             messagebox.showerror("Lỗi", "# src/gui.py (cập nhật)
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# import os
# import logging
# from .database import VideoManager
# from .persistence import save_data, load_data
# from .visualize import visualize_tree

# # Configure logging
# logger = logging.getLogger(__name__)

# class VideoDBApp:
#     def __init__(self, root, video_manager):
#         self.root = root
#         self.video_manager = video_manager
        
#         # Thiết lập cửa sổ chính
#         self.root.title("Hệ thống Cơ sở dữ liệu Video - MongoDB")
#         self.root.geometry("900x600")
        
#         # Frame trạng thái
#         self.status_frame = ttk.Frame(root)
#         self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
#         # Hiển thị trạng thái kết nối MongoDB
#         self.connection_status = tk.StringVar(value="Trạng thái DB: Đã kết nối")
#         ttk.Label(self.status_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=10)
        
#         # Kiểm tra kết nối MongoDB
#         self.check_mongodb_connection()
        
#         # Tạo tab control
#         self.tab_control = ttk.Notebook(root)
        
#         # Tab 1: Quản lý Video
#         self.tab_videos = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_videos, text="Quản lý Video")
#         self.setup_videos_tab()
        
#         # Tab 2: Quản lý Đối tượng
#         self.tab_objects = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_objects, text="Quản lý Đối tượng")
#         self.setup_objects_tab()
        
#         # Tab 3: Quản lý Phân đoạn
#         self.tab_segments = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_segments, text="Quản lý Phân đoạn")
#         self.setup_segments_tab()
        
#         # Tab 4: Tìm kiếm
#         self.tab_search = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_search, text="Tìm kiếm")
#         self.search_type_var = tk.StringVar(value="find_video_with_object")
#         self.setup_search_tab()
        
#         # Tab 5: Nhận diện đối tượng
#         self.tab_detection = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_detection, text="Nhận diện đối tượng")
#         self.setup_detection_tab()

#         # Tab 6: Thống kê
#         self.tab_stats = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_stats, text="Thống kê")
#         self.setup_stats_tab()
        
#         self.tab_control.pack(expand=1, fill="both")
        
#         # Menu
#         self.menu_bar = tk.Menu(root)
#         self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
#         self.file_menu.add_command(label="Lưu dữ liệu", command=self.save_data)
#         self.file_menu.add_command(label="Tải dữ liệu", command=self.load_data)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Xuất báo cáo", command=self.export_report)
#         self.file_menu.add_command(label="Xuất CSV", command=self.export_csv)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Cài đặt DB", command=self.show_db_settings)
#         self.file_menu.add_separator()
#         self.file_menu.add_command(label="Thoát", command=root.quit)
#         self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
#         self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
#         self.help_menu.add_command(label="Hướng dẫn sử dụng", command=self.show_help)
#         self.help_menu.add_command(label="Thông tin", command=self.show_about)
#         self.menu_bar.add_cascade(label="Trợ giúp", menu=self.help_menu)
        
#         root.config(menu=self.menu_bar)
    
#     def check_mongodb_connection(self):
#         """Kiểm tra kết nối với MongoDB"""
#         try:
#             from .mongodb import get_mongodb_client
#             client = get_mongodb_client()
#             # Thử ping để kiểm tra kết nối
#             client.db.command('ping')
#             self.connection_status.set("Trạng thái DB: MongoDB đã kết nối")
#             return True
#         except Exception as e:
#             logger.error(f"Lỗi kết nối MongoDB: {e}")
#             self.connection_status.set("Trạng thái DB: Lỗi kết nối MongoDB")
#             return False
    
#     def show_db_settings(self):
#         """Hiển thị cửa sổ cài đặt kết nối DB"""
#         # Tạo cửa sổ cài đặt
#         settings_window = tk.Toplevel(self.root)
#         settings_window.title("Cài đặt kết nối MongoDB")
#         settings_window.geometry("500x300")
#         settings_window.grab_set()  # Modal window
        
#         # Frame chính
#         main_frame = ttk.Frame(settings_window, padding=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
        
#         # Tiêu đề
#         ttk.Label(main_frame, text="Cài đặt kết nối MongoDB", font=("Arial", 14, "bold")).pack(pady=10)
        
#         # Trường nhập liệu
#         form_frame = ttk.Frame(main_frame)
#         form_frame.pack(fill=tk.BOTH, pady=10)
        
#         # Connection string
#         ttk.Label(form_frame, text="Connection string:").grid(row=0, column=0, sticky=tk.W, pady=5)
#         connection_var = tk.StringVar()
        
#         # Lấy connection string hiện tại
#         try:
#             from .config import MONGODB_URI
#             connection_var.set(MONGODB_URI)
#         except Exception:
#             connection_var.set("mongodb+srv://username:password@cluster.mongodb.net/videoDatabase")
        
#         ttk.Entry(form_frame, textvariable=connection_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        
#         # Database name
#         ttk.Label(form_frame, text="Tên Database:").grid(row=1, column=0, sticky=tk.W, pady=5)
#         db_name_var = tk.StringVar(value="videoDatabase")
#         ttk.Entry(form_frame, textvariable=db_name_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        
#         # Tùy chọn lưu trữ
#         storage_frame = ttk.LabelFrame(main_frame, text="Phương thức lưu trữ")
#         storage_frame.pack(fill=tk.X, pady=10)
        
#         storage_var = tk.BooleanVar(value=True)  # True = MongoDB, False = JSON
#         ttk.Radiobutton(storage_frame, text="Sử dụng MongoDB", variable=storage_var, value=True).pack(anchor=tk.W, padx=20, pady=5)
#         ttk.Radiobutton(storage_frame, text="Sử dụng JSON (local)", variable=storage_var, value=False).pack(anchor=tk.W, padx=20, pady=5)
        
#         # Nút lưu và kiểm tra kết nối
#         button_frame = ttk.Frame(main_frame)
#         button_frame.pack(fill=tk.X, pady=10)
        
#         def save_settings():
#             try:
#                 # Cập nhật file config
#                 with open("src/config.py", "w", encoding="utf-8") as f:
#                     f.write(f"# src/config.py\n")
#                     f.write(f"# Cấu hình cho MongoDB Atlas\n\n")
#                     f.write(f"# Constants for MongoDB connection\n")
#                     f.write(f"MONGODB_URI = \"{connection_var.get()}\"\n")
#                     f.write(f"DATABASE_NAME = \"{db_name_var.get()}\"\n\n")
#                     f.write(f"# Collection names\n")
#                     f.write(f"VIDEO_COLLECTION = \"videos\"\n")
#                     f.write(f"OBJECT_COLLECTION = \"objects\"\n")
#                     f.write(f"SEGMENT_COLLECTION = \"segments\"\n")
#                     f.write(f"\n# Use MongoDB or JSON\n")
#                     f.write(f"USE_MONGODB = {storage_var.get()}\n")
                
#                 # Cập nhật persistence.py
#                 with open("src/persistence.py", "r", encoding="utf-8") as f:
#                     content = f.read()
                
#                 # Cập nhật flag USE_MONGODB
#                 import re
#                 new_content = re.sub(
#                     r"USE_MONGODB = (True|False)", 
#                     f"USE_MONGODB = {storage_var.get()}", 
#                     content
#                 )
                
#                 with open("src/persistence.py", "w", encoding="utf-8") as f:
#                     f.write(new_content)
                
#                 messagebox.showinfo("Thành công", "Đã lưu cài đặt. Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
#                 settings_window.destroy()
                
#             except Exception as e:
#                 messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
        
#         def test_connection():
#             try:
#                 from pymongo import MongoClient
#                 import certifi
                
#                 # Thử kết nối
#                 client = MongoClient(connection_var.get(), tlsCAFile=certifi.where())
#                 client.admin.command('ping')
#                 messagebox.showinfo("Thành công", "Kết nối đến MongoDB thành công!")
#             except Exception as e:
#                 messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến MongoDB: {str(e)}")
        
#         ttk.Button(button_frame, text="Kiểm tra kết nối", command=test_connection).pack(side=tk.LEFT, padx=5)
#         ttk.Button(button_frame, text="Lưu cài đặt", command=save_settings).pack(side=tk.RIGHT, padx=5)
#         ttk.Button(button_frame, text="Hủy", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
#     def setup_videos_tab(self):
#         # Frame bên trái: Danh sách video
#         left_frame = ttk.Frame(self.tab_videos)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Video", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame tìm kiếm
#         search_frame = ttk.Frame(left_frame)
#         search_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
#         self.video_search_var = tk.StringVar()
#         ttk.Entry(search_frame, textvariable=self.video_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
#         ttk.Button(search_frame, text="Tìm", command=self.search_videos).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách video
#         columns = ("ID", "Tên", "Số Frame")
#         self.videos_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.videos_tree.heading(col, text=col)
#             self.videos_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.videos_tree.yview)
#         self.videos_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.videos_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.videos_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_videos_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa video
#         ttk.Button(button_frame, text="Xóa", command=self.delete_video).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm/Chỉnh sửa video
#         right_frame = ttk.Frame(self.tab_videos)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm/Chỉnh sửa Video", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm video
#         ttk.Label(right_frame, text="Tên video:").pack(anchor=tk.W, pady=5)
#         self.video_name_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.video_name_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Số frame:").pack(anchor=tk.W, pady=5)
#         self.video_frames_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.video_frames_var, width=30).pack(fill=tk.X, pady=5)
        
#         # Nút thêm/cập nhật
#         self.video_action_button = ttk.Button(right_frame, text="Thêm Video", command=self.add_video)
#         self.video_action_button.pack(pady=10)
        
#         # Biến để theo dõi ID video đang chỉnh sửa
#         self.editing_video_id = None
        
#         # Nút hủy chỉnh sửa
#         self.cancel_edit_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_video)
#         self.cancel_edit_button.pack(pady=5)
#         self.cancel_edit_button.pack_forget()  # Ẩn đi ban đầu
        
#         # Nút hiển thị cây phân đoạn
#         ttk.Button(right_frame, text="Hiển thị Frame Segment Tree", command=self.show_tree).pack(pady=5)
        
#         # Trường hiển thị chi tiết cây
#         ttk.Label(right_frame, text="Cấu trúc cây:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
#         self.tree_text = tk.Text(right_frame, height=15, width=40)
#         self.tree_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
#         # Làm mới danh sách video
#         self.refresh_videos_list()
    
#     def setup_objects_tab(self):
#         # Frame bên trái: Danh sách đối tượng
#         left_frame = ttk.Frame(self.tab_objects)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame tìm kiếm
#         search_frame = ttk.Frame(left_frame)
#         search_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
#         self.object_search_var = tk.StringVar()
#         ttk.Entry(search_frame, textvariable=self.object_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
#         ttk.Button(search_frame, text="Tìm", command=self.search_objects).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách đối tượng
#         columns = ("ID", "Tên", "Loại")
#         self.objects_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.objects_tree.heading(col, text=col)
#             self.objects_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.objects_tree.yview)
#         self.objects_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.objects_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.objects_tree.bind("<<TreeviewSelect>>", self.on_object_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_objects_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa đối tượng
#         ttk.Button(button_frame, text="Xóa", command=self.delete_object).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm/Chỉnh sửa đối tượng
#         right_frame = ttk.Frame(self.tab_objects)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm/Chỉnh sửa Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm đối tượng
#         ttk.Label(right_frame, text="Tên đối tượng:").pack(anchor=tk.W, pady=5)
#         self.object_name_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.object_name_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Loại đối tượng:").pack(anchor=tk.W, pady=5)
#         self.object_type_var = tk.StringVar()
#         object_types = ["Person", "Vehicle", "Object", "Animal", "Other"]
#         ttk.Combobox(right_frame, textvariable=self.object_type_var, values=object_types, width=28).pack(fill=tk.X, pady=5)
        
#         # Nút thêm/cập nhật
#         self.object_action_button = ttk.Button(right_frame, text="Thêm Đối tượng", command=self.add_object)
#         self.object_action_button.pack(pady=10)
        
#         # Biến để theo dõi ID đối tượng đang chỉnh sửa
#         self.editing_object_id = None
        
#         # Nút hủy chỉnh sửa
#         self.cancel_edit_obj_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_object)
#         self.cancel_edit_obj_button.pack(pady=5)
#         self.cancel_edit_obj_button.pack_forget()  # Ẩn đi ban đầu
        
#         # Frame hiển thị phân đoạn của đối tượng
#         segments_frame = ttk.LabelFrame(right_frame, text="Phân đoạn của đối tượng")
#         segments_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
#         # Treeview hiển thị phân đoạn
#         columns = ("Video", "Frame Bắt đầu", "Frame Kết thúc")
#         self.object_segments_tree = ttk.Treeview(segments_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.object_segments_tree.heading(col, text=col)
#             self.object_segments_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(segments_frame, orient="vertical", command=self.object_segments_tree.yview)
#         self.object_segments_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.object_segments_tree.pack(fill=tk.BOTH, expand=True)
        
#         # Làm mới danh sách đối tượng
#         self.refresh_objects_list()

#     def setup_segments_tab(self):
#         # Frame bên trái: Danh sách phân đoạn
#         left_frame = ttk.Frame(self.tab_segments)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(left_frame, text="Danh sách Phân đoạn", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Frame lọc
#         filter_frame = ttk.Frame(left_frame)
#         filter_frame.pack(fill=tk.X, pady=5)
        
#         ttk.Label(filter_frame, text="Lọc theo video:").pack(side=tk.LEFT, padx=5)
#         self.filter_video_var = tk.StringVar()
#         self.filter_video_combo = ttk.Combobox(filter_frame, textvariable=self.filter_video_var, width=20)
#         self.filter_video_combo.pack(side=tk.LEFT, padx=5)
        
#         ttk.Label(filter_frame, text="Lọc theo đối tượng:").pack(side=tk.LEFT, padx=5)
#         self.filter_object_var = tk.StringVar()
#         self.filter_object_combo = ttk.Combobox(filter_frame, textvariable=self.filter_object_var, width=20)
#         self.filter_object_combo.pack(side=tk.LEFT, padx=5)
        
#         ttk.Button(filter_frame, text="Lọc", command=self.filter_segments).pack(side=tk.LEFT, padx=5)
#         ttk.Button(filter_frame, text="Xóa bộ lọc", command=self.clear_segment_filters).pack(side=tk.LEFT, padx=5)
        
#         # Treeview để hiển thị danh sách phân đoạn
#         columns = ("ID", "Video", "Đối tượng", "Frame Bắt đầu", "Frame Kết thúc")
#         self.segments_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
#         # Thiết lập các cột
#         for col in columns:
#             self.segments_tree.heading(col, text=col)
#             self.segments_tree.column(col, width=100)
        
#         # Thêm scrollbar
#         scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.segments_tree.yview)
#         self.segments_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.segments_tree.pack(fill=tk.BOTH, expand=True)
        
#         self.segments_tree.bind("<<TreeviewSelect>>", self.on_segment_select)
        
#         # Frame nút
#         button_frame = ttk.Frame(left_frame)
#         button_frame.pack(fill=tk.X, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(button_frame, text="Làm mới", command=self.refresh_segments_list).pack(side=tk.LEFT, padx=5)
        
#         # Nút xóa phân đoạn
#         ttk.Button(button_frame, text="Xóa", command=self.delete_segment).pack(side=tk.LEFT, padx=5)
        
#         # Frame bên phải: Thêm phân đoạn
#         right_frame = ttk.Frame(self.tab_segments)
#         right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tiêu đề
#         ttk.Label(right_frame, text="Thêm Phân đoạn Mới", font=("Arial", 12, "bold")).pack(pady=5)
        
#         # Form thêm phân đoạn
#         # Video
#         ttk.Label(right_frame, text="Video:").pack(anchor=tk.W, pady=5)
#         self.segment_video_var = tk.StringVar()
#         self.segment_video_combo = ttk.Combobox(right_frame, textvariable=self.segment_video_var, width=28)
#         self.segment_video_combo.pack(fill=tk.X, pady=5)
        
#         # Đối tượng
#         ttk.Label(right_frame, text="Đối tượng:").pack(anchor=tk.W, pady=5)
#         self.segment_object_var = tk.StringVar()
#         self.segment_object_combo = ttk.Combobox(right_frame, textvariable=self.segment_object_var, width=28)
#         self.segment_object_combo.pack(fill=tk.X, pady=5)
        
#         # Frame bắt đầu và kết thúc
#         ttk.Label(right_frame, text="Frame bắt đầu:").pack(anchor=tk.W, pady=5)
#         self.start_frame_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.start_frame_var, width=30).pack(fill=tk.X, pady=5)
        
#         ttk.Label(right_frame, text="Frame kết thúc:").pack(anchor=tk.W, pady=5)
#         self.end_frame_var = tk.StringVar()
#         ttk.Entry(right_frame, textvariable=self.end_frame_var, width=30).pack(fill=tk.X, pady=5)
        
#         # Nút thêm
#         ttk.Button(right_frame, text="Thêm Phân đoạn", command=self.add_segment).pack(pady=10)
        
#         # Làm mới danh sách combobox
#         self.refresh_combo_lists()
        
#         # Làm mới danh sách phân đoạn
#         self.refresh_segments_list()