# main.py (cập nhật)
import tkinter as tk
from src.database import VideoManager
from data.sample_data import load_sample_data
from src.persistence import load_data
from src.gui import VideoDBApp

def main():
    # Tạo cửa sổ gốc
    root = tk.Tk()
    
    # Kiểm tra xem có dữ liệu đã lưu không
    video_manager = load_data()
    
    # Nếu không có, tải dữ liệu mẫu
    if not video_manager:
        video_manager = load_sample_data()
    
    # Khởi tạo biến cho tìm kiếm
    root.search_type_var = tk.StringVar(value="find_video_with_object")
    
    # Tạo ứng dụng
    app = VideoDBApp(root, video_manager)
    
    # Chạy vòng lặp sự kiện
    root.mainloop()

if __name__ == "__main__":
    main()