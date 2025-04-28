import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = "videoDB"

# Collection names
VIDEO_COLLECTION = "videos"
OBJECT_COLLECTION = "objects"
SEGMENT_COLLECTION = "segments"