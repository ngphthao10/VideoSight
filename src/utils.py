def generate_report(video_manager, filename="report.txt"):
    """Tạo báo cáo thống kê về dữ liệu video"""
    with open(filename, 'w', encoding='utf-8') as f:
        # Thống kê tổng quan
        videos = video_manager.get_all_videos()
        objects = video_manager.get_all_objects()
        
        f.write("=== BÁO CÁO THỐNG KÊ CƠ SỞ DỮ LIỆU VIDEO ===\n\n")
        f.write(f"Tổng số video: {len(videos)}\n")
        f.write(f"Tổng số đối tượng: {len(objects)}\n")
        f.write(f"Tổng số phân đoạn: {len(video_manager.segments)}\n\n")
        
        # Danh sách video
        f.write("--- DANH SÁCH VIDEO ---\n")
        for vid, name, frames in videos:
            f.write(f"ID: {vid}, Tên: {name}, Số frame: {frames}\n")
        f.write("\n")
        
        # Danh sách đối tượng
        f.write("--- DANH SÁCH ĐỐI TƯỢNG ---\n")
        for oid, name, obj_type in objects:
            f.write(f"ID: {oid}, Tên: {name}, Loại: {obj_type}\n")
        f.write("\n")
        
        # Thống kê theo video
        f.write("--- THỐNG KÊ THEO VIDEO ---\n")
        for vid, name, _ in videos:
            objects_in_video = set()
            for v, o, _, _ in video_manager.segments:
                if v == vid:
                    objects_in_video.add(o)
            
            f.write(f"Video {name} (ID: {vid}):\n")
            f.write(f"  - Số đối tượng: {len(objects_in_video)}\n")
            f.write(f"  - Số phân đoạn: {sum(1 for v, _, _, _ in video_manager.segments if v == vid)}\n")
        f.write("\n")
        
        # Thống kê theo đối tượng
        f.write("--- THỐNG KÊ THEO ĐỐI TƯỢNG ---\n")
        for oid, name, _ in objects:
            videos_with_object = set()
            for v, o, _, _ in video_manager.segments:
                if o == oid:
                    videos_with_object.add(v)
            
            f.write(f"Đối tượng {name} (ID: {oid}):\n")
            f.write(f"  - Xuất hiện trong {len(videos_with_object)} video\n")
            f.write(f"  - Số phân đoạn: {sum(1 for _, o, _, _ in video_manager.segments if o == oid)}\n")
        
    return filename

def export_to_csv(video_manager, filename="data/export.csv"):
    """Xuất dữ liệu segment ra file CSV"""
    import csv
    import os
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Viết header
        writer.writerow(['Video ID', 'Video Name', 'Object ID', 'Object Name', 'Object Type', 'Start Frame', 'End Frame'])
        
        # Viết dữ liệu
        for vid, oid, start, end in video_manager.segments:
            video_name = video_manager.videos[vid][0]
            object_name, object_type = video_manager.objects[oid]
            
            writer.writerow([vid, video_name, oid, object_name, object_type, start, end])
    
    return filename