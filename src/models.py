class SegmentTreeNode:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.objects = []
        self.left = None
        self.right = None

class FrameSegmentTree:
    def __init__(self, total_frames):
        self.root = self._build_tree(0, total_frames)
        
    def _build_tree(self, start, end):
        node = SegmentTreeNode(start, end)
        if start + 1 < end:
            mid = (start + end) // 2
            node.left = self._build_tree(start, mid)
            node.right = self._build_tree(mid, end)
        return node
    
    def insert_object(self, object_id, start, end):
        self._insert(self.root, object_id, start, end)
    
    def _insert(self, node, object_id, start, end):
        # Nếu phân đoạn nằm hoàn toàn trong khoảng node
        if start <= node.start and end >= node.end:
            node.objects.append(object_id)
            return
        
        # Nếu phân đoạn không giao với node
        if end <= node.start or start >= node.end:
            return
            
        # Gọi đệ quy cho các node con
        if node.left:
            self._insert(node.left, object_id, start, end)
        if node.right:
            self._insert(node.right, object_id, start, end)
    
    def find_objects(self, start, end):
        result = set()
        self._find(self.root, start, end, result)
        return result
    
    def _find(self, node, start, end, result):
        # Thêm các đối tượng của node hiện tại
        result.update(node.objects)
        
        # Nếu đã là node lá hoặc không giao với phân đoạn cần tìm
        if not node.left or end <= node.start or start >= node.end:
            return
            
        # Gọi đệ quy cho các node con
        self._find(node.left, start, end, result)
        self._find(node.right, start, end, result)