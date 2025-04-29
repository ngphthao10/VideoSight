import tkinter as tk
from tkinter import ttk, messagebox
import io
from contextlib import redirect_stdout
import logging

logger = logging.getLogger(__name__)

class VideoTab:
    def __init__(self, parent, video_manager):
        self.parent = parent
        self.video_manager = video_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Frame bên trái: Danh sách video
        left_frame = ttk.Frame(self.parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(left_frame, text="Danh sách Video", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame tìm kiếm
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.video_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.video_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Tìm", command=self.search_videos).pack(side=tk.LEFT, padx=5)
        
        # Treeview để hiển thị danh sách video
        columns = ("ID", "Tên", "Số Frame")
        self.videos_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Thiết lập các cột
        for col in columns:
            self.videos_tree.heading(col, text=col)
            self.videos_tree.column(col, width=100)
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.videos_tree.yview)
        self.videos_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.videos_tree.pack(fill=tk.BOTH, expand=True)
        
        self.videos_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
        # Frame nút
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Nút làm mới danh sách
        ttk.Button(button_frame, text="Làm mới", command=self.refresh_videos_list).pack(side=tk.LEFT, padx=5)
        
        # Nút xóa video
        ttk.Button(button_frame, text="Xóa", command=self.delete_video).pack(side=tk.LEFT, padx=5)
        
        # Frame bên phải: Thêm/Chỉnh sửa video
        right_frame = ttk.Frame(self.parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tiêu đề
        ttk.Label(right_frame, text="Thêm/Chỉnh sửa Video", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Form thêm video
        ttk.Label(right_frame, text="Tên video:").pack(anchor=tk.W, pady=5)
        self.video_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.video_name_var, width=30).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Số frame:").pack(anchor=tk.W, pady=5)
        self.video_frames_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.video_frames_var, width=30).pack(fill=tk.X, pady=5)
        
        # Nút thêm/cập nhật
        self.video_action_button = ttk.Button(right_frame, text="Thêm Video", command=self.add_video)
        self.video_action_button.pack(pady=10)
        
        # Biến để theo dõi ID video đang chỉnh sửa
        self.editing_video_id = None
        
        # Nút hủy chỉnh sửa
        self.cancel_edit_button = ttk.Button(right_frame, text="Hủy", command=self.cancel_edit_video)
        self.cancel_edit_button.pack(pady=5)
        self.cancel_edit_button.pack_forget()  # Ẩn đi ban đầu
        
        # Nút hiển thị cây phân đoạn
        ttk.Button(right_frame, text="Hiển thị Frame Segment Tree", command=self.show_tree).pack(pady=5)
        
        # Trường hiển thị chi tiết cây
        ttk.Label(right_frame, text="Cấu trúc cây:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.tree_text = tk.Text(right_frame, height=15, width=40)
        self.tree_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Làm mới danh sách video
        self.refresh_videos_list()
    
    def refresh_data(self, video_manager):
        """Cập nhật dữ liệu khi có thay đổi từ bên ngoài"""
        self.video_manager = video_manager
        self.refresh_videos_list()
    
    def refresh_videos_list(self):
        """Làm mới danh sách video"""
        # Xóa dữ liệu cũ
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        # Lấy danh sách video
        videos = self.video_manager.get_all_videos()
        
        # Thêm vào treeview
        for vid, name, frames in videos:
            self.videos_tree.insert("", tk.END, values=(vid, name, frames))
    
    def search_videos(self):
        """Tìm kiếm video theo tên"""
        search_term = self.video_search_var.get().strip()
        if not search_term:
            self.refresh_videos_list()
            return
        
        # Tìm kiếm
        results = self.video_manager.search_videos_by_name(search_term)
        
        # Hiển thị kết quả
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        for vid, name, frames in results:
            self.videos_tree.insert("", tk.END, values=(vid, name, frames))
    
    def on_video_select(self, event):
        """Xử lý sự kiện khi chọn một video trong danh sách"""
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
        
        # Cập nhật trạng thái chỉnh sửa
        self.editing_video_id = vid
        self.video_action_button.config(text="Cập nhật Video")
        
        # Hiển thị nút hủy
        self.cancel_edit_button.pack(pady=5)
    
    def add_video(self):
        """Thêm hoặc cập nhật video"""
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
        
        # Kiểm tra xem đang thêm mới hay cập nhật
        if self.editing_video_id is not None:
            # Cập nhật video
            success = self.video_manager.update_video(self.editing_video_id, video_name, frames)
            if success:
                messagebox.showinfo("Thành công", f"Đã cập nhật video ID: {self.editing_video_id}")
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật video!")
                return
        else:
            # Thêm video mới
            video_id = self.video_manager.add_video_if_not_exists(video_name, frames)
            messagebox.showinfo("Thành công", f"Đã thêm video ID: {video_id}")
        
        # Làm mới danh sách
        self.refresh_videos_list()
        
        # Xóa form
        self.cancel_edit_video()
    
    def cancel_edit_video(self):
        """Hủy chỉnh sửa video"""
        self.editing_video_id = None
        self.video_name_var.set("")
        self.video_frames_var.set("")
        self.video_action_button.config(text="Thêm Video")
        self.cancel_edit_button.pack_forget()
    
    def delete_video(self):
        """Xóa video"""
        selected_item = self.videos_tree.selection()
        if not selected_item:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một video để xóa!")
            return
        
        # Lấy thông tin video
        video_values = self.videos_tree.item(selected_item[0], "values")
        vid = int(video_values[0])
        
        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa video {video_values[1]} và tất cả phân đoạn liên quan?")
        if not confirm:
            return
        
        # Xóa video
        if self.video_manager.delete_video(vid):
            messagebox.showinfo("Thành công", "Đã xóa video và các phân đoạn liên quan!")
            
            # Làm mới danh sách
            self.refresh_videos_list()
            
            # Xóa form nếu đang chỉnh sửa video này
            if self.editing_video_id == vid:
                self.cancel_edit_video()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa video!")
    
    def show_tree(self):
        """Hiển thị cấu trúc Frame Segment Tree của video đã chọn"""
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
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                _, _, tree = self.video_manager.videos[vid]
                from ..visualize import print_tree_node
                print_tree_node(tree.root)
            
            # Lấy nội dung và hiển thị
            tree_text = buffer.getvalue()
            self.tree_text.insert(tk.END, tree_text)
        else:
            self.tree_text.insert(tk.END, "Video không tồn tại!")