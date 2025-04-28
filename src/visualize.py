# src/visualize.py
def print_tree_node(node, level=0, prefix="Root: "):
    """In cấu trúc của cây theo dạng văn bản"""
    if node is None:
        return
    
    # In thông tin của node hiện tại
    indent = "  " * level
    object_list = ", ".join([str(obj) for obj in node.objects])
    print(f"{indent}{prefix}[{node.start}, {node.end}) - Objects: [{object_list}]")
    
    # In các node con
    if node.left:
        print_tree_node(node.left, level + 1, "L: ")
    if node.right:
        print_tree_node(node.right, level + 1, "R: ")

def visualize_tree(tree):
    """Trực quan hóa Frame Segment Tree"""
    print("\n--- Frame Segment Tree Visualization ---")
    print_tree_node(tree.root)
    print("---------------------------------------\n")