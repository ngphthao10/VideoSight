import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class SearchTab:
    def __init__(self, parent, video_manager, search_type_var):
        self.parent = parent
        self.video_manager = video_manager
        self.search_type_var = search_type_var
        self.setup_ui()
        
    def setup_ui(self):
        # Frame tìm kiếm
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(search_frame, text="Tìm kiếm", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Các tùy chọn tìm kiếm
        search_options = ttk.LabelFrame(search_frame, text="Tùy chọn tìm kiếm")
        search_options.pack(fill=tk.X, pady=10)
        
        # Tìm video chứa đối tượng
        ttk.Radiobutton(
            search_options, 
            text="Tìm video chứa đối tượng", 
            value="find_video_with_object", 
            variable=self.search_type_var, 
            command=self.update_search_conditions
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Tìm đối tượng trong đoạn video
        ttk.Radiobutton(
            search_options, 
            text="Tìm đối tượng trong đoạn video", 
            value="find_objects_in_video", 
            variable=self.search_type_var, 
            command=self.update_search_conditions
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Tìm kiếm nâng cao
        ttk.Radiobutton(
            search_options, 
            text="Tìm kiếm nâng cao", 
            value="advanced_search", 
            variable=self.search_type_var, 
            command=self.update_search_conditions
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Frame điều kiện tìm kiếm
        self.search_conditions = ttk.LabelFrame(search_frame, text="Điều kiện tìm kiếm")
        self.search_conditions.pack(fill=tk.X, pady=10)
        
        # Điều kiện theo tùy chọn
        self.object_search_frame = ttk.Frame(self.search_conditions)
        ttk.Label(self.object_search_frame, text="Tên đối tượng:").pack(side=tk.LEFT, padx=5)
        self.search_object_var = tk.StringVar()
        ttk.Entry(self.object_search_frame, textvariable=self.search_object_var, width=30).pack(side=tk.LEFT, padx=5)
        
        self.video_search_frame = ttk.Frame(self.search_conditions)
        ttk.Label(self.video_search_frame, text="ID Video:").pack(side=tk.LEFT, padx=5)
        self.search_video_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_video_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.video_search_frame, text="Frame bắt đầu:").pack(side=tk.LEFT, padx=5)
        self.search_start_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_start_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.video_search_frame, text="Frame kết thúc:").pack(side=tk.LEFT, padx=5)
        self.search_end_var = tk.StringVar()
        ttk.Entry(self.video_search_frame, textvariable=self.search_end_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame tìm kiếm nâng cao
        self.advanced_search_frame = ttk.Frame(self.search_conditions)
        # Tạo bảng tùy chọn tìm kiếm nâng cao
        ttk.Label(self.advanced_search_frame, text="Loại đối tượng:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_object_type_var = tk.StringVar()
        object_types = ["Tất cả", "Person", "Vehicle", "Object", "Animal", "Other"]
        ttk.Combobox(self.advanced_search_frame, textvariable=self.adv_object_type_var, values=object_types, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.advanced_search_frame, text="Khoảng frames:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        frame_range_frame = ttk.Frame(self.advanced_search_frame)
        frame_range_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_min_frame_var = tk.StringVar()
        ttk.Entry(frame_range_frame, textvariable=self.adv_min_frame_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_range_frame, text="-").pack(side=tk.LEFT)
        self.adv_max_frame_var = tk.StringVar()
        ttk.Entry(frame_range_frame, textvariable=self.adv_max_frame_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Chỉ hiển thị frame thích hợp theo tùy chọn đã chọn
        self.update_search_conditions()
        
        # Nút tìm kiếm
        ttk.Button(search_frame, text="Tìm kiếm", command=self.perform_search).pack(pady=10)
        
        # Kết quả tìm kiếm
        result_frame = ttk.LabelFrame(search_frame, text="Kết quả tìm kiếm")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview để hiển thị kết quả
        self.result_tree = ttk.Treeview(result_frame, show="headings")
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
    
    def update_search_conditions(self):
        """Cập nhật điều kiện tìm kiếm dựa trên tùy chọn tìm kiếm"""
        # Lấy kiểu tìm kiếm hiện tại
        search_type = self.search_type_var.get()
        
        # Ẩn tất cả các frame điều kiện
        self.object_search_frame.pack_forget()
        self.video_search_frame.pack_forget()
        self.advanced_search_frame.pack_forget()
        
        # Hiển thị frame phù hợp
        if search_type == "find_video_with_object":
            self.object_search_frame.pack(fill=tk.X, pady=10)
        elif search_type == "find_objects_in_video":
            self.video_search_frame.pack(fill=tk.X, pady=10)
        elif search_type == "advanced_search":
            self.advanced_search_frame.pack(fill=tk.X, pady=10)
    
    def perform_search(self):
        """Thực hiện tìm kiếm dựa trên tùy chọn và điều kiện"""
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
        
        elif search_type == "advanced_search":
            columns = ("Video", "Đối tượng", "Loại", "Frame Bắt đầu", "Frame Kết thúc")
            self.result_tree["columns"] = columns
            for col in columns:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)
            
            # Thực hiện tìm kiếm nâng cao
            object_type = self.adv_object_type_var.get()
            if object_type == "Tất cả":
                object_type = ""
            
            try:
                min_frame = int(self.adv_min_frame_var.get()) if self.adv_min_frame_var.get() else 0
                max_frame = int(self.adv_max_frame_var.get()) if self.adv_max_frame_var.get() else float('inf')
            except ValueError:
                messagebox.showerror("Lỗi", "Frame phải là số nguyên!")
                return
            
            # Tìm tất cả các đối tượng phù hợp với loại
            matching_objects = []
            if object_type:
                matching_objects = self.video_manager.search_objects_by_type(object_type)
            else:
                matching_objects = self.video_manager.get_all_objects()
            
            # Tìm các phân đoạn phù hợp
            results = []
            for oid, obj_name, obj_type in matching_objects:
                segments = self.video_manager.get_segments_for_object(oid)
                for vid, video_name, start, end in segments:
                    # Kiểm tra điều kiện khoảng frame
                    if (start <= max_frame and end >= min_frame):
                        results.append((vid, video_name, oid, obj_name, obj_type, start, end))
            
            if not results:
                messagebox.showinfo("Kết quả", "Không tìm thấy kết quả phù hợp")
            else:
                # Hiển thị kết quả
                for vid, video_name, oid, obj_name, obj_type, start, end in results:
                    self.result_tree.insert("", tk.END, values=(video_name, obj_name, obj_type, start, end))