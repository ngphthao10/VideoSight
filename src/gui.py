# src/gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from .database import VideoManager
from .persistence import save_data, load_data
from .visualize import visualize_tree

class VideoDBApp:
    def __init__(self, root, video_manager):
        self.root = root
        self.video_manager = video_manager
        
        # Thiết lập cửa sổ chính
        self.root.title("Hệ thống Cơ sở dữ liệu Video")
        self.root.geometry("900x600")
        
        # Tạo tab control
        self.tab_control = ttk.Notebook(root)
        
        # Tab 1: Quản lý Video
        self.tab_videos = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_videos, text="Quản lý Video")
        self.setup_videos_tab()
        
        # Tab 2: Quản lý Đối tượng
        self.tab_objects = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_objects, text="Quản lý Đối tượng")
        self.setup_objects_tab()
        
        # Tab 3: Quản lý Phân đoạn
        self.tab_segments = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_segments, text="Quản lý Phân đoạn")
        self.setup_segments_tab()
        
        # Tab 4: Tìm kiếm
        self.tab_search = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_search, text="Tìm kiếm")
        self.search_type_var = tk.StringVar(value="find_video_with_object")  # Thêm dòng này
        self.setup_search_tab()

        
        # Tab 5: Nhận diện đối tượng
        self.tab_detection = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_detection, text="Nhận diện đối tượng")
        self.setup_detection_tab()
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Menu
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Lưu dữ liệu", command=self.save_data)
        self.file_menu.add_command(label="Tải dữ liệu", command=self.load_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Xuất báo cáo", command=self.export_report)
        self.file_menu.add_command(label="Xuất CSV", command=self.export_csv)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Thoát", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Hướng dẫn sử dụng", command=self.show_help)
        self.help_menu.add_command(label="Thông tin", command=self.show_about)
        self.menu_bar.add_cascade(label="Trợ giúp", menu=self.help_menu)
        
        root.config(menu=self.menu_bar)
    
    def setup_videos_tab(self):
        # Frame bên trái: Danh sách video
        left_frame = ttk.Frame(self.tab_videos)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Video", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Treeview để hiển thị danh sách video
        columns = ("ID", "Tên", "Số Frame")
        self.videos_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.videos_tree.heading(col, text=col)
            self.videos_tree.column(col, width=100)
        
        self.videos_tree.pack(fill=tk.BOTH, expand=True)
        self.videos_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
        # Nút làm mới danh sách
        ttk.Button(left_frame, text="Làm mới", command=self.refresh_videos_list).pack(pady=5)
        
        # Frame bên phải: Thêm/Chỉnh sửa video
        right_frame = ttk.Frame(self.tab_videos)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(right_frame, text="Thêm Video Mới", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Form thêm video
        ttk.Label(right_frame, text="Tên video:").pack(anchor=tk.W, pady=5)
        self.video_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.video_name_var, width=30).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Số frame:").pack(anchor=tk.W, pady=5)
        self.video_frames_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.video_frames_var, width=30).pack(fill=tk.X, pady=5)
        
        # Nút thêm
        ttk.Button(right_frame, text="Thêm Video", command=self.add_video).pack(pady=10)
        
        # Nút hiển thị cây phân đoạn
        ttk.Button(right_frame, text="Hiển thị Frame Segment Tree", command=self.show_tree).pack(pady=5)
        
        # Trường hiển thị chi tiết cây
        ttk.Label(right_frame, text="Cấu trúc cây:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.tree_text = tk.Text(right_frame, height=15, width=40)
        self.tree_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Làm mới danh sách video
        self.refresh_videos_list()
    
    def setup_objects_tab(self):
        # Frame bên trái: Danh sách đối tượng
        left_frame = ttk.Frame(self.tab_objects)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Treeview để hiển thị danh sách đối tượng
        columns = ("ID", "Tên", "Loại")
        self.objects_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.objects_tree.heading(col, text=col)
            self.objects_tree.column(col, width=100)
        
        self.objects_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nút làm mới danh sách
        ttk.Button(left_frame, text="Làm mới", command=self.refresh_objects_list).pack(pady=5)
        
        # Frame bên phải: Thêm đối tượng
        right_frame = ttk.Frame(self.tab_objects)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(right_frame, text="Thêm Đối tượng Mới", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Form thêm đối tượng
        ttk.Label(right_frame, text="Tên đối tượng:").pack(anchor=tk.W, pady=5)
        self.object_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.object_name_var, width=30).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Loại đối tượng:").pack(anchor=tk.W, pady=5)
        self.object_type_var = tk.StringVar()
        object_types = ["Person", "Vehicle", "Object", "Animal", "Other"]
        ttk.Combobox(right_frame, textvariable=self.object_type_var, values=object_types, width=28).pack(fill=tk.X, pady=5)
        
        # Nút thêm
        ttk.Button(right_frame, text="Thêm Đối tượng", command=self.add_object).pack(pady=10)
        
        # Làm mới danh sách đối tượng
        self.refresh_objects_list()

    def setup_segments_tab(self):
        # Frame bên trái: Danh sách phân đoạn
        left_frame = ttk.Frame(self.tab_segments)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Phân đoạn", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Treeview để hiển thị danh sách phân đoạn
        columns = ("Video", "Đối tượng", "Frame Bắt đầu", "Frame Kết thúc")
        self.segments_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.segments_tree.heading(col, text=col)
            self.segments_tree.column(col, width=100)
        
        self.segments_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nút làm mới danh sách
        ttk.Button(left_frame, text="Làm mới", command=self.refresh_segments_list).pack(pady=5)
        
        # Frame bên phải: Thêm phân đoạn
        right_frame = ttk.Frame(self.tab_segments)
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

    def setup_search_tab(self):
        # Frame tìm kiếm
        search_frame = ttk.Frame(self.tab_search)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(search_frame, text="Tìm kiếm", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Các tùy chọn tìm kiếm
        search_options = ttk.LabelFrame(search_frame, text="Tùy chọn tìm kiếm")
        search_options.pack(fill=tk.X, pady=10)
        
        # Tìm video chứa đối tượng
        ttk.Radiobutton(search_options, text="Tìm video chứa đối tượng", value="find_video_with_object", variable=self.search_type_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Tìm đối tượng trong đoạn video
        ttk.Radiobutton(search_options, text="Tìm đối tượng trong đoạn video", value="find_objects_in_video", variable=self.search_type_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Frame điều kiện tìm kiếm
        search_conditions = ttk.LabelFrame(search_frame, text="Điều kiện tìm kiếm")
        search_conditions.pack(fill=tk.X, pady=10)
        
        # Điều kiện theo tùy chọn
        self.object_search_frame = ttk.Frame(search_conditions)
        ttk.Label(self.object_search_frame, text="Tên đối tượng:").pack(side=tk.LEFT, padx=5)
        self.search_object_var = tk.StringVar()
        ttk.Entry(self.object_search_frame, textvariable=self.search_object_var, width=30).pack(side=tk.LEFT, padx=5)
        
        self.video_search_frame = ttk.Frame(search_conditions)
        ttk.Label(self.video_search_frame, text="ID Video:").pack(side=tk.LEFT, padx=5)
        self.search_video_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_video_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.video_search_frame, text="Frame bắt đầu:").pack(side=tk.LEFT, padx=5)
        self.search_start_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_start_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.video_search_frame, text="Frame kết thúc:").pack(side=tk.LEFT, padx=5)
        self.search_end_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_end_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Chỉ hiển thị frame thích hợp theo tùy chọn đã chọn
        self.update_search_conditions()
        
        # Nút tìm kiếm
        ttk.Button(search_frame, text="Tìm kiếm", command=self.perform_search).pack(pady=10)
        
        # Kết quả tìm kiếm
        result_frame = ttk.LabelFrame(search_frame, text="Kết quả tìm kiếm")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview để hiển thị kết quả
        self.result_tree = ttk.Treeview(result_frame)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    def setup_detection_tab(self):
        # Frame chính
        detection_frame = ttk.Frame(self.tab_detection)
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
        ttk.Scale(detection_options, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.confidence_var, length=200).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(detection_options, textvariable=tk.StringVar(value=lambda: f"{self.confidence_var.get():.2f}")).grid(row=1, column=2, padx=5, pady=5)
        
        # Tần suất lấy mẫu
        ttk.Label(detection_options, text="Tần suất lấy mẫu (frames):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.sample_rate_var = tk.IntVar(value=30)
        ttk.Entry(detection_options, textvariable=self.sample_rate_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Nút bắt đầu phân tích
        ttk.Button(detection_frame, text="Bắt đầu nhận diện", command=self.start_detection).pack(pady=10)
        
        # Thanh tiến trình
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(detection_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var).pack(fill=tk.X, pady=10)
        
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
        
        self.detection_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nút lưu kết quả
        ttk.Button(detection_frame, text="Lưu kết quả vào cơ sở dữ liệu", command=self.save_detection_results).pack(pady=10)
        
    # Các phương thức callback và tiện ích
    def refresh_videos_list(self):
        # Xóa dữ liệu cũ
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        # Lấy danh sách video
        videos = self.video_manager.get_all_videos()
        
        # Thêm vào treeview
        for vid, name, frames in videos:
            self.videos_tree.insert("", tk.END, values=(vid, name, frames))
    
    def refresh_objects_list(self):
        # Xóa dữ liệu cũ
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)
        
        # Lấy danh sách đối tượng
        objects = self.video_manager.get_all_objects()
        
        # Thêm vào treeview
        for oid, name, obj_type in objects:
            self.objects_tree.insert("", tk.END, values=(oid, name, obj_type))
    
    def refresh_segments_list(self):
        # Xóa dữ liệu cũ
        for item in self.segments_tree.get_children():
            self.segments_tree.delete(item)
        
        # Lấy danh sách phân đoạn
        segments = self.video_manager.segments
        
        # Thêm vào treeview
        for vid, oid, start, end in segments:
            video_name = self.video_manager.videos[vid][0]
            object_name = self.video_manager.objects[oid][0]
            self.segments_tree.insert("", tk.END, values=(video_name, object_name, start, end))
    
    def refresh_combo_lists(self):
        # Làm mới danh sách video trong combobox
        videos = self.video_manager.get_all_videos()
        video_names = [f"{vid}: {name}" for vid, name, _ in videos]
        self.segment_video_combo['values'] = video_names
        
        # Làm mới danh sách đối tượng trong combobox
        objects = self.video_manager.get_all_objects()
        object_names = [f"{oid}: {name}" for oid, name, _ in objects]
        self.segment_object_combo['values'] = object_names
    
    def on_video_select(self, event):
        # Lấy item được chọn
        selected_item = self.videos_tree.selection()
        if not selected_item:
            return
        
        # Lấy thông tin video
        video_values = self.videos_tree.item(selected_item[0], "values")
        vid = int(video_values[0])
        
        # Hiển thị thông tin chi tiết
        self.video_name_var.set(video_values[1])
        self.video_frames_var.set(video_values[2])
    
    def add_video(self):
        # Lấy thông tin từ form
        video_name = self.video_name_var.get().strip()
        try:
            frames = int(self.video_frames_var.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi", "Số frame phải là số nguyên!")
            return
        
        if not video_name:
            messagebox.showerror("Lỗi", "Tên video không được để trống!")
            return
        
        # Thêm video mới
        video_id = self.video_manager.add_video_if_not_exists(video_name, frames)
        
        # Làm mới danh sách
        self.refresh_videos_list()
        self.refresh_combo_lists()
        
        # Xóa form
        self.video_name_var.set("")
        self.video_frames_var.set("")
        
        messagebox.showinfo("Thành công", f"Đã thêm video ID: {video_id}")
    
    def add_object(self):
        # Lấy thông tin từ form
        object_name = self.object_name_var.get().strip()
        object_type = self.object_type_var.get().strip()
        
        if not object_name or not object_type:
            messagebox.showerror("Lỗi", "Tên và loại đối tượng không được để trống!")
            return
        
        # Thêm đối tượng mới
        object_id = self.video_manager.add_object_if_not_exists(object_name, object_type)
        
        # Làm mới danh sách
        self.refresh_objects_list()
        self.refresh_combo_lists()
        
        # Xóa form
        self.object_name_var.set("")
        self.object_type_var.set("")
        
        messagebox.showinfo("Thành công", f"Đã thêm đối tượng ID: {object_id}")
    
    def add_segment(self):
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
    
    def show_tree(self):
        # Lấy item được chọn
        selected_item = self.videos_tree.selection()
        if not selected_item:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một video từ danh sách!")
            return
        
        # Lấy ID video
        video_values = self.videos_tree.item(selected_item[0], "values")
        vid = int(video_values[0])
        
        # Xóa nội dung hiện tại
        self.tree_text.delete(1.0, tk.END)
        
        # Lấy cây và hiển thị
        if vid in self.video_manager.videos:
            # Lưu đầu ra của hàm print_tree_node vào một biến
            import io
            from contextlib import redirect_stdout
            
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                _, _, tree = self.video_manager.videos[vid]
                from .visualize import print_tree_node
                print_tree_node(tree.root)
            
            # Lấy nội dung và hiển thị
            tree_text = buffer.getvalue()
            self.tree_text.insert(tk.END, tree_text)
        else:
            self.tree_text.insert(tk.END, "Video không tồn tại!")
    
    def save_data(self):
        from .persistence import save_data
        if save_data(self.video_manager):
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu!")
        else:
            messagebox.showerror("Lỗi", "Không thể lưu dữ liệu!")
    
    def load_data(self):
        from .persistence import load_data
        loaded_manager = load_data()
        if loaded_manager:
            self.video_manager = loaded_manager
            self.refresh_videos_list()
            self.refresh_objects_list()
            self.refresh_segments_list()
            self.refresh_combo_lists()
            messagebox.showinfo("Thành công", "Đã tải dữ liệu!")
        else:
            messagebox.showerror("Lỗi", "Không thể tải dữ liệu!")
    
    def export_report(self):
        from .utils import generate_report
        filename = generate_report(self.video_manager)
        messagebox.showinfo("Thành công", f"Đã xuất báo cáo: {filename}")
    
    def export_csv(self):
        from .utils import export_to_csv
        filename = export_to_csv(self.video_manager)
        messagebox.showinfo("Thành công", f"Đã xuất dữ liệu CSV: {filename}")
    
    def show_help(self):
        help_text = """
        Hướng dẫn sử dụng hệ thống cơ sở dữ liệu video:
        
        1. Quản lý Video: Thêm và xem danh sách video
        2. Quản lý Đối tượng: Thêm và xem danh sách đối tượng
        3. Quản lý Phân đoạn: Thêm phân đoạn xuất hiện của đối tượng trong video
        4. Tìm kiếm: Tìm kiếm video hoặc đối tượng
        5. Nhận diện đối tượng: Phân tích video để tự động nhận diện đối tượng
        
        Menu File:
        - Lưu/Tải dữ liệu: Lưu và tải dữ liệu từ file
        - Xuất báo cáo/CSV: Xuất dữ liệu sang định dạng khác
        """
        messagebox.showinfo("Hướng dẫn sử dụng", help_text)
    
    def show_about(self):
        about_text = """
        Hệ thống Cơ sở dữ liệu Video v1.0
        
        Phát triển dựa trên cấu trúc Frame Segment Tree.
        
        © 2023
        """
        messagebox.showinfo("Thông tin", about_text)
    
    def update_search_conditions(self):
        # Lấy kiểu tìm kiếm hiện tại
        search_type = self.search_type_var.get()
        
        # Ẩn tất cả các frame điều kiện
        self.object_search_frame.pack_forget()
        self.video_search_frame.pack_forget()
        
        # Hiển thị frame phù hợp
        if search_type == "find_video_with_object":
            self.object_search_frame.pack(fill=tk.X, pady=10)
        elif search_type == "find_objects_in_video":
            self.video_search_frame.pack(fill=tk.X, pady=10)
    
    def perform_search(self):
        # Lấy kiểu tìm kiếm
        search_type = self.search_type_var.get()
        
        # Xóa kết quả cũ
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Thiết lập cột phù hợp
        if search_type == "find_video_with_object":
            columns = ("Video ID", "Tên Video", "Frame Bắt đầu", "Frame Kết thúc")
            self.result_tree["columns"] = columns
            for col in columns:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)
            
            # Thực hiện tìm kiếm
            object_name = self.search_object_var.get().strip()
            if not object_name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên đối tượng!")
                return
            
            results = self.video_manager.find_video_with_object(object_name)
            
            if not results:
                messagebox.showinfo("Kết quả", f"Không tìm thấy video nào chứa '{object_name}'")
            else:
                # Hiển thị kết quả
                for vid, name, start, end in results:
                    self.result_tree.insert("", tk.END, values=(vid, name, start, end))
        
        elif search_type == "find_objects_in_video":
            columns = ("Đối tượng ID", "Tên Đối tượng", "Loại")
            self.result_tree["columns"] = columns
            for col in columns:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)
            
            # Thực hiện tìm kiếm
            try:
                video_id = int(self.search_video_var.get().strip())
                start_frame = int(self.search_start_var.get().strip())
                end_frame = int(self.search_end_var.get().strip())
                
                results = self.video_manager.find_objects_in_video(video_id, start_frame, end_frame)
                
                if not results:
                    messagebox.showinfo("Kết quả", f"Không tìm thấy đối tượng nào trong đoạn video từ frame {start_frame} đến {end_frame}")
                else:
                    # Hiển thị kết quả
                    for oid, name, obj_type in results:
                        self.result_tree.insert("", tk.END, values=(oid, name, obj_type))
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập ID và frame dạng số!")
    
    def select_video_file(self):
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
        
        # Thực hiện nhận diện đối tượng (sẽ cài đặt ở phần sau)
        try:
            # Gọi hàm nhận diện (sẽ cài đặt ở phần sau)
            from .detection import detect_objects_in_video
            self.detection_results = detect_objects_in_video(
                video_path, model_name, confidence, sample_rate, 
                progress_callback=self.update_progress
            )
            
            # Hiển thị kết quả
            for result in self.detection_results:
                frame, obj_name, confidence, bbox = result
                self.detection_tree.insert("", tk.END, values=(
                    frame, obj_name, f"{confidence:.2f}",
                    f"({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"
                ))
            
            messagebox.showinfo("Thành công", f"Đã nhận diện {len(self.detection_results)} đối tượng trong video!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhận diện đối tượng: {str(e)}")
            raise e
    
    def update_progress(self, value):
        # Cập nhật thanh tiến trình
        self.progress_var.set(value * 100)
        self.root.update_idletasks()
    
    def save_detection_results(self):
        # Kiểm tra xem có kết quả không
        if not hasattr(self, 'detection_results') or not self.detection_results:
            messagebox.showerror("Lỗi", "Không có kết quả nhận diện nào để lưu!")
            return
        
        # Lấy đường dẫn video
        video_path = self.selected_video_var.get()
        video_name = os.path.basename(video_path)
        
        # Thêm video mới nếu chưa có
        video_id = self.video_manager.add_video_if_not_exists(video_name, 0)  # Số frame sẽ được cập nhật sau
        
        # Xử lý từng kết quả nhận diện
        added_count = 0
        for result in self.detection_results:
            frame, obj_name, confidence, bbox = result
            
            # Thêm đối tượng mới nếu chưa có
            object_id = self.video_manager.add_object_if_not_exists(obj_name, "Detected")
            
            # Thêm phân đoạn (đơn giản hóa: mỗi frame là một phân đoạn)
            if self.video_manager.add_segment(video_id, object_id, frame, frame + 1):
                added_count += 1
        
        # Làm mới các danh sách
        self.refresh_segments_list()
        self.refresh_combo_lists()
        
        messagebox.showinfo("Thành công", f"Đã lưu {added_count} phân đoạn vào cơ sở dữ liệu!")