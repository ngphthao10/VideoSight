# src/persistence.py
import json
import os

def save_data(video_manager, filename="data/video_data.json"):
    """Lưu dữ liệu từ VideoManager xuống file JSON"""
    data = {
        "videos": {},
        "objects": {},
        "segments": []
    }
    
    # Lưu thông tin video (không lưu cây vì sẽ tái tạo khi load)
    for vid, (name, frames, _) in video_manager.videos.items():
        data["videos"][str(vid)] = {"name": name, "frames": frames}
    
    # Lưu thông tin đối tượng
    for oid, (name, obj_type) in video_manager.objects.items():
        data["objects"][str(oid)] = {"name": name, "type": obj_type}
    
    # Lưu thông tin phân đoạn
    for vid, oid, start, end in video_manager.segments:
        data["segments"].append({
            "video_id": vid,
            "object_id": oid,
            "start_frame": start,
            "end_frame": end
        })
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Lưu xuống file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    return True

def load_data(filename="data/video_data.json"):
    """Tải dữ liệu từ file JSON vào VideoManager mới"""
    from .database import VideoManager
    
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tạo VideoManager mới
        manager = VideoManager()
        
        # Thêm video
        for vid_str, video_info in data["videos"].items():
            vid = int(vid_str)
            manager.add_video(vid, video_info["name"], video_info["frames"])
        
        # Thêm đối tượng
        for oid_str, obj_info in data["objects"].items():
            oid = int(oid_str)
            manager.add_object(oid, obj_info["name"], obj_info["type"])
        
        # Thêm phân đoạn
        for segment in data["segments"]:
            manager.add_segment(
                segment["video_id"],
                segment["object_id"],
                segment["start_frame"],
                segment["end_frame"]
            )
        
        return manager
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {e}")
        return None