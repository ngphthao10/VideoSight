# src/gui/object_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class ObjectTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Frame bên trái: Danh sách đối tượng
        left_frame = ttk.Frame(self.parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame tìm kiếm
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.object_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.object_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Tìm", command=self.search_objects).pack(side=tk.LEFT, padx=5)
        
        # Treeview để hiển thị danh sách đối tượng
        columns = ("ID", "Tên", "Loại")
        self.objects_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.objects_tree.heading(col, text=col)
            self.objects_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.objects_tree.yview)
        self.objects_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.objects_tree.pack(fill=tk.BOTH, expand=True)
        
        self.objects_tree.bind("<<TreeviewSelect>>", self.on_object_select)
        
        # Frame nút
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Nút làm mới danh sách
        ttk.Button(button_frame, text="Làm mới", command=self.refresh_objects_list).pack(side=tk.LEFT, padx=5)
        
        # Nút xóa đối tượng
        ttk.Button(button_frame, text="Xóa", command=self.delete_object).pack(side=tk.LEFT, padx=5)
        
        # Frame bên phải: Thêm/Chỉnh sửa đối tượng
        right_frame = ttk.Frame(self.parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(right_frame, text="Thêm/Chỉnh sửa Đối tượng", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Form thêm đối tượng
        ttk.Label(right_frame, text="Tên đối tượng:").pack(anchor=tk.W, pady=5)
        self.object_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.object_name_var, width=30).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Loại đối tượng:").pack(anchor=tk.W, pady=5)
        self.object_type_var = tk.StringVar()
        object_types = ["Person", "Vehicle", "Object", "Animal", "Other"]
        ttk.Combobox(right_frame, textvariable=self.object_type_var, values=object_types, width=28).pack(fill=tk.X, pady=5)
        
        # Nút thêm/cập nhật
        self.object_action_button = ttk.Button(right_frame, text="Thêm Đối tượng", command=self.add_object)
        self.object_action_button.pack(pady=10)
        
        # Biến để theo dõi ID đối tượng đang chỉnh sửa
        self.editing_object_id = None
        
        # Nút hủy chỉnh sửa
        self.cancel_edit_obj_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_object)
        self.cancel_edit_obj_button.pack(pady=5)
        self.cancel_edit_obj_button.pack_forget()  # Ẩn đi ban đầu
        
        # Frame hiển thị phân đoạn của đối tượng
        segments_frame = ttk.LabelFrame(right_frame, text="Phân đoạn của đối tượng")
        segments_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview hiển thị phân đoạn
        columns = ("Video", "Frame Bắt đầu", "Frame Kết thúc")
        self.object_segments_tree = ttk.Treeview(segments_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.object_segments_tree.heading(col, text=col)
            self.object_segments_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(segments_frame, orient="vertical", command=self.object_segments_tree.yview)
        self.object_segments_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.object_segments_tree.pack(fill=tk.BOTH, expand=True)
        
        # Làm mới danh sách đối tượng
        self.refresh_objects_list()
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
        self.refresh_objects_list()
    
    def refresh_objects_list(self):
        """Làm mới danh sách đối tượng"""
        # Xóa dữ liệu cũ
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)
        
        # Lấy danh sách đối tượng
        objects = self.video_manager.get_all_objects()
        
        # Thêm vào treeview
        for oid, name, obj_type in objects:
            self.objects_tree.insert("", tk.END, values=(oid, name, obj_type))
    
    def search_objects(self):
        """Tìm kiếm đối tượng theo tên"""
        search_term = self.object_search_var.get().strip()
        if not search_term:
            self.refresh_objects_list()
            return
        
        # Tìm kiếm
        results = self.video_manager.search_objects_by_name(search_term)
        
        # Hiển thị kết quả
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)
        
        for oid, name, obj_type in results:
            self.objects_tree.insert("", tk.END, values=(oid, name, obj_type))
    
    def on_object_select(self, event):
        """Xử lý sự kiện khi chọn một đối tượng trong danh sách"""
        # Lấy item được chọn
        selected_item = self.objects_tree.selection()
        if not selected_item:
            return
        
        # Lấy thông tin đối tượng
        object_values = self.objects_tree.item(selected_item[0], "values")
        oid = int(object_values[0])
        
        # Hiển thị thông tin chi tiết
        self.object_name_var.set(object_values[1])
        self.object_type_var.set(object_values[2])
        
        # Cập nhật trạng thái chỉnh sửa
        self.editing_object_id = oid
        self.object_action_button.config(text="Cập nhật Đối tượng")
        
        # Hiển thị nút hủy
        self.cancel_edit_obj_button.pack(pady=5)
        
        # Hiển thị các phân đoạn của đối tượng
        self.display_object_segments(oid)
    
    def display_object_segments(self, object_id):
        """Hiển thị danh sách phân đoạn của đối tượng"""
        # Xóa dữ liệu cũ
        for item in self.object_segments_tree.get_children():
            self.object_segments_tree.delete(item)
        
        # Lấy các phân đoạn của đối tượng
        segments = self.video_manager.get_segments_for_object(object_id)
        
        # Thêm vào treeview
        for vid, video_name, start, end in segments:
            self.object_segments_tree.insert("", tk.END, values=(video_name, start, end))
    
    def add_object(self):
        """Thêm hoặc cập nhật đối tượng"""
        # Lấy thông tin từ form
        object_name = self.object_name_var.get().strip()
        object_type = self.object_type_var.get().strip()
        
        if not object_name or not object_type:
            messagebox.showerror("Lỗi", "Tên và loại đối tượng không được để trống!")
            return
        
        # Kiểm tra xem đang thêm mới hay cập nhật
        if self.editing_object_id is not None:
            # Cập nhật đối tượng
            success = self.video_manager.update_object(self.editing_object_id, object_name, object_type)
            if success:
                messagebox.showinfo("Thành công", f"Đã cập nhật đối tượng ID: {self.editing_object_id}")
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật đối tượng!")
                return
        else:
            # Thêm đối tượng mới
            object_id = self.video_manager.add_object_if_not_exists(object_name, object_type)
            messagebox.showinfo("Thành công", f"Đã thêm đối tượng ID: {object_id}")
        
        # Làm mới danh sách
        self.refresh_objects_list()
        
        # Xóa form
        self.cancel_edit_object()
    
    def cancel_edit_object(self):
        """Hủy chỉnh sửa đối tượng"""
        self.editing_object_id = None
        self.object_name_var.set("")
        self.object_type_var.set("")
        self.object_action_button.config(text="Thêm Đối tượng")
        self.cancel_edit_obj_button.pack_forget()
        
        # Xóa danh sách phân đoạn
        for item in self.object_segments_tree.get_children():
            self.object_segments_tree.delete(item)
    
    def delete_object(self):
        """Xóa đối tượng"""
        selected_item = self.objects_tree.selection()
        if not selected_item:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một đối tượng để xóa!")
            return
        
        # Lấy thông tin đối tượng
        object_values = self.objects_tree.item(selected_item[0], "values")
        oid = int(object_values[0])
        
        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa đối tượng {object_values[1]} và tất cả phân đoạn liên quan?")
        if not confirm:
            return
        
        # Xóa đối tượng
        if self.video_manager.delete_object(oid):
            messagebox.showinfo("Thành công", "Đã xóa đối tượng và các phân đoạn liên quan!")
            
            # Làm mới danh sách
            self.refresh_objects_list()
            
            # Xóa form nếu đang chỉnh sửa đối tượng này
            if self.editing_object_id == oid:
                self.cancel_edit_object()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa đối tượng!")