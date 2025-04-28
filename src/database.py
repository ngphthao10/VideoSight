from .models import FrameSegmentTree
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoManager:
    def __init__(self):
        self.videos = {}  # video_id -> (video_name, total_frames, tree)
        self.objects = {}  # object_id -> (object_name, object_type)
        self.segments = []  # [(video_id, object_id, start_frame, end_frame)]
        
    def add_video(self, video_id, video_name, total_frames):
        self.videos[video_id] = (video_name, total_frames, FrameSegmentTree(total_frames))
        return video_id
        
    def add_object(self, object_id, object_name, object_type):
        self.objects[object_id] = (object_name, object_type)
        return object_id
        
    def add_segment(self, video_id, object_id, start_frame, end_frame):
        if video_id in self.videos and object_id in self.objects:
            self.segments.append((video_id, object_id, start_frame, end_frame))
            _, _, tree = self.videos[video_id]
            tree.insert_object(object_id, start_frame, end_frame)
            return True
        return False
            
    def find_video_with_object(self, object_name):
        results = []
        object_id = None
        
        # Tìm object_id từ tên đối tượng
        for oid, (name, _) in self.objects.items():
            if name == object_name:
                object_id = oid
                break
                
        if object_id is None:
            return results
            
        # Tìm các video có chứa đối tượng
        for segment in self.segments:
            vid, oid, start, end = segment
            if oid == object_id:
                video_name, _, _ = self.videos[vid]
                results.append((vid, video_name, start, end))
                
        return results
    
    def find_objects_in_video(self, video_id, start_frame, end_frame):
        if video_id not in self.videos:
            return []
            
        _, _, tree = self.videos[video_id]
        object_ids = tree.find_objects(start_frame, end_frame)
        
        results = []
        for oid in object_ids:
            object_name, object_type = self.objects.get(oid, ("Unknown", "Unknown"))
            results.append((oid, object_name, object_type))
            
        return results
        
    def get_all_videos(self):
        return [(vid, name, frames) for vid, (name, frames, _) in self.videos.items()]
        
    def get_all_objects(self):
        return [(oid, name, type_) for oid, (name, type_) in self.objects.items()]

    def get_object_by_name(self, object_name):
        """Tìm đối tượng theo tên"""
        for oid, (name, obj_type) in self.objects.items():
            if name.lower() == object_name.lower():
                return (oid, name, obj_type)
        return None

    def get_segments_for_object(self, object_id, video_id=None):
        """Trả về tất cả các phân đoạn của một đối tượng"""
        results = []
        for seg in self.segments:
            vid, oid, start, end = seg
            if oid == object_id and (video_id is None or vid == video_id):
                video_name = self.videos[vid][0]
                results.append((vid, video_name, start, end))
        return results

    def add_video_if_not_exists(self, video_name, total_frames):
        """Thêm video nếu chưa tồn tại, trả về video_id"""
        # Kiểm tra xem video đã tồn tại chưa
        for vid, (name, _, _) in self.videos.items():
            if name == video_name:
                return vid
        
        # Tạo ID mới
        new_id = max(self.videos.keys(), default=0) + 1
        self.add_video(new_id, video_name, total_frames)
        return new_id

    def add_object_if_not_exists(self, object_name, object_type):
        """Thêm đối tượng nếu chưa tồn tại, trả về object_id"""
        # Kiểm tra xem đối tượng đã tồn tại chưa
        for oid, (name, type_) in self.objects.items():
            if name == object_name and type_ == object_type:
                return oid
        
        # Tạo ID mới
        new_id = max(self.objects.keys(), default=0) + 1
        self.add_object(new_id, object_name, object_type)
        return new_id

    def get_video_by_id(self, video_id):
        """Lấy thông tin video theo ID"""
        if video_id in self.videos:
            name, frames, _ = self.videos[video_id]
            return (video_id, name, frames)
        return None
    
    def delete_video(self, video_id):
        """Xóa video và tất cả phân đoạn liên quan"""
        if video_id not in self.videos:
            return False
        
        # Xóa video
        del self.videos[video_id]
        
        # Xóa các phân đoạn liên quan
        self.segments = [(vid, oid, start, end) for vid, oid, start, end in self.segments if vid != video_id]
        
        logger.info(f"Đã xóa video ID: {video_id} và các phân đoạn liên quan")
        return True
    
    def delete_object(self, object_id):
        """Xóa đối tượng và tất cả phân đoạn liên quan"""
        if object_id not in self.objects:
            return False
        
        # Xóa đối tượng
        del self.objects[object_id]
        
        # Xóa các phân đoạn liên quan
        self.segments = [(vid, oid, start, end) for vid, oid, start, end in self.segments if oid != object_id]
        
        # Cập nhật cây phân đoạn
        for vid, (_, _, tree) in self.videos.items():
            # Làm mới cây phân đoạn cho mỗi video
            _, frames, _ = self.videos[vid]
            new_tree = FrameSegmentTree(frames)
            
            # Thêm lại các phân đoạn không liên quan đến đối tượng đã xóa
            for segment_vid, segment_oid, start, end in self.segments:
                if segment_vid == vid:
                    new_tree.insert_object(segment_oid, start, end)
            
            # Cập nhật cây
            self.videos[vid] = (self.videos[vid][0], self.videos[vid][1], new_tree)
        
        logger.info(f"Đã xóa đối tượng ID: {object_id} và các phân đoạn liên quan")
        return True
    
    def delete_segment(self, video_id, object_id, start_frame, end_frame):
        """Xóa một phân đoạn cụ thể"""
        segment = (video_id, object_id, start_frame, end_frame)
        if segment not in self.segments:
            return False
        
        # Xóa phân đoạn
        self.segments.remove(segment)
        
        # Cập nhật cây phân đoạn
        if video_id in self.videos:
            # Tạo cây mới
            _, frames, _ = self.videos[video_id]
            new_tree = FrameSegmentTree(frames)
            
            # Thêm lại tất cả phân đoạn ngoại trừ phân đoạn bị xóa
            for seg_vid, seg_oid, seg_start, seg_end in self.segments:
                if seg_vid == video_id:
                    new_tree.insert_object(seg_oid, seg_start, seg_end)
            
            # Cập nhật cây
            self.videos[video_id] = (self.videos[video_id][0], self.videos[video_id][1], new_tree)
        
        logger.info(f"Đã xóa phân đoạn: Video {video_id}, Đối tượng {object_id}, Frames {start_frame}-{end_frame}")
        return True
    
    def update_video(self, video_id, new_name=None, new_frames=None):
        """Cập nhật thông tin video"""
        if video_id not in self.videos:
            return False
        
        name, frames, tree = self.videos[video_id]
        
        if new_name is not None:
            name = new_name
        
        if new_frames is not None and new_frames != frames:
            # Nếu số frame thay đổi, cần tạo lại cây phân đoạn
            frames = new_frames
            tree = FrameSegmentTree(frames)
            
            # Thêm lại tất cả các phân đoạn
            for seg_vid, seg_oid, seg_start, seg_end in self.segments:
                if seg_vid == video_id:
                    if seg_end <= frames:  # Chỉ thêm nếu phân đoạn nằm trong khoảng frame mới
                        tree.insert_object(seg_oid, seg_start, seg_end)
                    else:
                        # Cắt bớt phân đoạn nếu vượt quá số frame mới
                        new_end = min(seg_end, frames)
                        if seg_start < new_end:
                            tree.insert_object(seg_oid, seg_start, new_end)
        
        # Cập nhật thông tin video
        self.videos[video_id] = (name, frames, tree)
        
        logger.info(f"Đã cập nhật video ID: {video_id}, Tên: {name}, Frames: {frames}")
        return True
    
    def update_object(self, object_id, new_name=None, new_type=None):
        """Cập nhật thông tin đối tượng"""
        if object_id not in self.objects:
            return False
        
        name, obj_type = self.objects[object_id]
        
        if new_name is not None:
            name = new_name
        
        if new_type is not None:
            obj_type = new_type
        
        # Cập nhật thông tin đối tượng
        self.objects[object_id] = (name, obj_type)
        
        logger.info(f"Đã cập nhật đối tượng ID: {object_id}, Tên: {name}, Loại: {obj_type}")
        return True

    def visualize_tree(self, video_id):
        """Hiển thị cấu trúc Frame Segment Tree của một video"""
        if video_id not in self.videos:
            return False
        
        from .visualize import visualize_tree
        _, _, tree = self.videos[video_id]
        visualize_tree(tree)
        return True
        
    def search_videos_by_name(self, name_part):
        """Tìm kiếm video theo tên (tìm kiếm mờ)"""
        results = []
        name_part = name_part.lower()
        
        for vid, (name, frames, _) in self.videos.items():
            if name_part in name.lower():
                results.append((vid, name, frames))
        
        return results
    
    def search_objects_by_name(self, name_part):
        """Tìm kiếm đối tượng theo tên (tìm kiếm mờ)"""
        results = []
        name_part = name_part.lower()
        
        for oid, (name, obj_type) in self.objects.items():
            if name_part in name.lower():
                results.append((oid, name, obj_type))
        
        return results
    
    def search_objects_by_type(self, object_type):
        """Tìm kiếm đối tượng theo loại"""
        results = []
        object_type = object_type.lower()
        
        for oid, (name, type_) in self.objects.items():
            if object_type in type_.lower():
                results.append((oid, name, type_))
        
        return results
    
    def get_object_statistics(self):
        """Lấy thống kê về số lượng đối tượng theo loại"""
        stats = {}
        
        for _, (_, obj_type) in self.objects.items():
            if obj_type in stats:
                stats[obj_type] += 1
            else:
                stats[obj_type] = 1
        
        return stats
    
    def get_video_statistics(self):
        """Lấy thống kê về các video (số đối tượng, số phân đoạn)"""
        stats = {}
        
        for vid, (name, frames, _) in self.videos.items():
            # Đếm số đối tượng xuất hiện trong video
            unique_objects = set()
            segment_count = 0
            
            for segment_vid, segment_oid, _, _ in self.segments:
                if segment_vid == vid:
                    unique_objects.add(segment_oid)
                    segment_count += 1
            
            stats[vid] = {
                "name": name,
                "frames": frames,
                "object_count": len(unique_objects),
                "segment_count": segment_count
            }
        
        return stats