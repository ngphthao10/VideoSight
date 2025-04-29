import logging
from .mongodb import get_mongodb_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_data_to_mongodb(video_manager):
    """Lưu dữ liệu từ VideoManager xuống MongoDB"""
    try:
        # Lấy client MongoDB
        client = get_mongodb_client()
        
        # Xóa dữ liệu cũ
        client.get_video_collection().delete_many({})
        client.get_object_collection().delete_many({})
        client.get_segment_collection().delete_many({})
        
        # Lưu thông tin video
        video_docs = []
        for vid, (name, frames, _) in video_manager.videos.items():
            video_docs.append({
                "video_id": vid,
                "name": name,
                "frames": frames
            })
        
        if video_docs:
            client.get_video_collection().insert_many(video_docs)
            logger.info(f"Đã lưu {len(video_docs)} video vào MongoDB")
        
        # Lưu thông tin đối tượng
        object_docs = []
        for oid, (name, obj_type) in video_manager.objects.items():
            object_docs.append({
                "object_id": oid,
                "name": name,
                "type": obj_type
            })
        
        if object_docs:
            client.get_object_collection().insert_many(object_docs)
            logger.info(f"Đã lưu {len(object_docs)} đối tượng vào MongoDB")
        
        # Lưu thông tin phân đoạn
        segment_docs = []
        for vid, oid, start, end in video_manager.segments:
            segment_docs.append({
                "video_id": vid,
                "object_id": oid,
                "start_frame": start,
                "end_frame": end
            })
        
        if segment_docs:
            client.get_segment_collection().insert_many(segment_docs)
            logger.info(f"Đã lưu {len(segment_docs)} phân đoạn vào MongoDB")
        
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu dữ liệu vào MongoDB: {e}")
        return False

def load_data_from_mongodb():
    """Tải dữ liệu từ MongoDB vào VideoManager mới"""
    from .database import VideoManager
    
    try:
        # Lấy client MongoDB
        client = get_mongodb_client()
        
        # Tạo VideoManager mới
        manager = VideoManager()
        
        # Tải danh sách video
        videos = list(client.get_video_collection().find({}))
        for video in videos:
            manager.add_video(
                video["video_id"],
                video["name"],
                video["frames"]
            )
        
        # Tải danh sách đối tượng
        objects = list(client.get_object_collection().find({}))
        for obj in objects:
            manager.add_object(
                obj["object_id"],
                obj["name"],
                obj["type"]
            )
        
        # Tải danh sách phân đoạn
        segments = list(client.get_segment_collection().find({}))
        for segment in segments:
            manager.add_segment(
                segment["video_id"],
                segment["object_id"],
                segment["start_frame"],
                segment["end_frame"]
            )
        
        logger.info(f"Đã tải {len(videos)} video, {len(objects)} đối tượng, {len(segments)} phân đoạn từ MongoDB")
        return manager
    except Exception as e:
        logger.error(f"Lỗi khi tải dữ liệu từ MongoDB: {e}")
        return None