import tkinter as tk
from tkinter import ttk, messagebox
import re
import logging

logger = logging.getLogger(__name__)

def show_db_settings(parent, callback_on_success=None):
    """Hiển thị cửa sổ cài đặt kết nối DB
    
    Args:
        parent: Widget cha
        callback_on_success: Hàm callback được gọi khi lưu cài đặt thành công
    """
    # Tạo cửa sổ cài đặt
    settings_window = tk.Toplevel(parent)
    settings_window.title("Cài đặt kết nối MongoDB")
    settings_window.geometry("500x300")
    settings_window.grab_set()  # Modal window
    
    # Frame chính
    main_frame = ttk.Frame(settings_window, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Tiêu đề
    ttk.Label(main_frame, text="Cài đặt kết nối MongoDB", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Trường nhập liệu
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.BOTH, pady=10)
    
    # Connection string
    ttk.Label(form_frame, text="Connection string:").grid(row=0, column=0, sticky=tk.W, pady=5)
    connection_var = tk.StringVar()
    
    # Lấy connection string hiện tại
    try:
        from ..config import MONGODB_URI
        connection_var.set(MONGODB_URI)
    except Exception:
        connection_var.set("mongodb+srv://username:password@cluster.mongodb.net/videoDatabase")
    
    ttk.Entry(form_frame, textvariable=connection_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    
    # Database name
    ttk.Label(form_frame, text="Tên Database:").grid(row=1, column=0, sticky=tk.W, pady=5)
    db_name_var = tk.StringVar(value="videoDatabase")
    ttk.Entry(form_frame, textvariable=db_name_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    
    # Tùy chọn lưu trữ
    storage_frame = ttk.LabelFrame(main_frame, text="Phương thức lưu trữ")
    storage_frame.pack(fill=tk.X, pady=10)
    
    storage_var = tk.BooleanVar(value=True)  # True = MongoDB, False = JSON
    ttk.Radiobutton(storage_frame, text="Sử dụng MongoDB", variable=storage_var, value=True).pack(anchor=tk.W, padx=20, pady=5)
    ttk.Radiobutton(storage_frame, text="Sử dụng JSON (local)", variable=storage_var, value=False).pack(anchor=tk.W, padx=20, pady=5)
    
    # Nút lưu và kiểm tra kết nối
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    def save_settings():
        try:
            # Cập nhật file config
            with open("src/config.py", "w", encoding="utf-8") as f:
                f.write(f"# src/config.py\n")
                f.write(f"# Cấu hình cho MongoDB Atlas\n\n")
                f.write(f"# Constants for MongoDB connection\n")
                f.write(f"MONGODB_URI = \"{connection_var.get()}\"\n")
                f.write(f"DATABASE_NAME = \"{db_name_var.get()}\"\n\n")
                f.write(f"# Collection names\n")
                f.write(f"VIDEO_COLLECTION = \"videos\"\n")
                f.write(f"OBJECT_COLLECTION = \"objects\"\n")
                f.write(f"SEGMENT_COLLECTION = \"segments\"\n")
                f.write(f"\n# Use MongoDB or JSON\n")
                f.write(f"USE_MONGODB = {storage_var.get()}\n")
            
            # Cập nhật persistence.py
            try:
                with open("src/persistence.py", "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Cập nhật flag USE_MONGODB
                new_content = re.sub(
                    r"USE_MONGODB = (True|False)", 
                    f"USE_MONGODB = {storage_var.get()}", 
                    content
                )
                
                with open("src/persistence.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
            except Exception as e:
                logger.error(f"Lỗi khi cập nhật persistence.py: {e}")
            
            messagebox.showinfo("Thành công", "Đã lưu cài đặt. Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
            
            # Gọi callback nếu có
            if callback_on_success and callable(callback_on_success):
                callback_on_success()
                
            settings_window.destroy()
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt: {e}")
            messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
    
    def test_connection():
        try:
            from pymongo import MongoClient
            import certifi
            
            # Thử kết nối
            client = MongoClient(connection_var.get(), tlsCAFile=certifi.where())
            client.admin.command('ping')
            messagebox.showinfo("Thành công", "Kết nối đến MongoDB thành công!")
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra kết nối MongoDB: {e}")
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến MongoDB: {str(e)}")
    
    ttk.Button(button_frame, text="Kiểm tra kết nối", command=test_connection).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Lưu cài đặt", command=save_settings).pack(side=tk.RIGHT, padx=5)
    ttk.Button(button_frame, text="Hủy", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)