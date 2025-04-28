from .models import FrameSegmentTree

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

    def visualize_tree(self, video_id):
        """Hiển thị cấu trúc Frame Segment Tree của một video"""
        if video_id not in self.videos:
            return False
        
        from .visualize import visualize_tree
        _, _, tree = self.videos[video_id]
        visualize_tree(tree)
        return True