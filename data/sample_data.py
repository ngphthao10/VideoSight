from src.database import VideoManager

def load_sample_data():
    manager = VideoManager()
    
    # Thêm video mẫu
    manager.add_video(1, "Surveillance Video 1", 1000)
    manager.add_video(2, "Educational Video", 1500)
    
    # Thêm đối tượng mẫu
    manager.add_object(1, "Denis Dopeman", "Person")
    manager.add_object(2, "Jane Shady", "Person")
    manager.add_object(3, "Briefcase", "Object")
    manager.add_object(4, "Car", "Vehicle")
    manager.add_object(5, "Professor", "Person")
    
    # Thêm các đoạn video
    # Video 1: Surveillance
    manager.add_segment(1, 1, 250, 750)  # Denis Dopeman
    manager.add_segment(1, 1, 900, 950)  # Denis Dopeman
    manager.add_segment(1, 2, 100, 400)  # Jane Shady
    manager.add_segment(1, 2, 600, 800)  # Jane Shady
    manager.add_segment(1, 3, 300, 500)  # Briefcase
    manager.add_segment(1, 4, 50, 200)   # Car
    
    # Video 2: Educational
    manager.add_segment(2, 5, 100, 1400) # Professor
    
    return manager