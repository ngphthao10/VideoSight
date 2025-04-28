# src/mongodb.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
import certifi
from .config import MONGODB_URI, DATABASE_NAME, VIDEO_COLLECTION, OBJECT_COLLECTION, SEGMENT_COLLECTION

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.videos = None
            cls._instance.objects = None
            cls._instance.segments = None
            cls._instance.initialize_connection()
        return cls._instance
    
    def initialize_connection(self):
        """Khởi tạo kết nối với MongoDB Atlas"""
        try:
            # Sử dụng certifi để xác thực SSL
            self.client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
            
            # Kiểm tra kết nối
            self.client.admin.command('ping')
            logger.info("Kết nối thành công đến MongoDB Atlas")
            
            # Lấy database và collections
            self.db = self.client[DATABASE_NAME]
            self.videos = self.db[VIDEO_COLLECTION]
            self.objects = self.db[OBJECT_COLLECTION]
            self.segments = self.db[SEGMENT_COLLECTION]
            
            # Tạo indexes để tối ưu hiệu suất truy vấn
            self.videos.create_index("video_id", unique=True)
            self.objects.create_index("object_id", unique=True)
            self.segments.create_index([("video_id", 1), ("object_id", 1)])
            
        except ConnectionFailure as e:
            logger.error(f"Không thể kết nối đến MongoDB Atlas: {e}")
            raise
        except Exception as e:
            logger.error(f"Lỗi không xác định khi kết nối MongoDB: {e}")
            raise
    
    def close_connection(self):
        """Đóng kết nối với MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Đã đóng kết nối MongoDB")
    
    def get_video_collection(self):
        return self.videos
    
    def get_object_collection(self):
        return self.objects
    
    def get_segment_collection(self):
        return self.segments

# Hàm tiện ích để lấy instance của MongoDB
def get_mongodb_client():
    return MongoDBClient()