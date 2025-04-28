# main.py (cập nhật để sử dụng MongoDB và cấu trúc GUI mới)
import tkinter as tk
import logging
import sys
from src.database import VideoManager
from data.sample_data import load_sample_data
from src.persistence import load_data, save_data
from src.gui import VideoDBApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Tạo cửa sổ gốc
    root = tk.Tk()
    root.title("Hệ thống Cơ sở dữ liệu Video (MongoDB)")
    
    # Kiểm tra xem có dữ liệu đã lưu không
    logger.info("Đang tải dữ liệu...")
    video_manager = load_data()
    
    # Nếu không có hoặc có lỗi, tải dữ liệu mẫu
    if not video_manager:
        logger.info("Không tìm thấy dữ liệu đã lưu, đang tải dữ liệu mẫu...")
        video_manager = load_sample_data()
        
        # Lưu dữ liệu mẫu vào MongoDB
        if save_data(video_manager):
            logger.info("Đã lưu dữ liệu mẫu vào cơ sở dữ liệu")
    
    # Tạo ứng dụng
    app = VideoDBApp(root, video_manager)
    
    # Cài đặt kích thước cửa sổ
    root.geometry("1000x700")
    
    # Chạy vòng lặp sự kiện
    try:
        root.mainloop()
    except Exception as e:
        logger.error(f"Lỗi không xử lý được trong mainloop: {e}")
    finally:
        # Đảm bảo lưu dữ liệu trước khi thoát
        save_data(video_manager)
        logger.info("Đã lưu dữ liệu trước khi thoát")
        
        # Đóng kết nối MongoDB nếu cần
        try:
            from src.mongodb import get_mongodb_client
            get_mongodb_client().close_connection()
        except Exception as e:
            logger.error(f"Lỗi khi đóng kết nối MongoDB: {e}")

if __name__ == "__main__":
    main()