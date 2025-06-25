"""
Video Compare Tool for ComfyUI
A custom node that allows side-by-side comparison of two videos with a slider interface
"""

import os
import shutil
from aiohttp import web
from server import PromptServer

from .video_compare_bmo import Video_Compare_BMO

NODE_CLASS_MAPPINGS = {
    "Video_Compare_BMO": Video_Compare_BMO,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Video_Compare_BMO": "Video Compare BMO",
}

# Register web extensions
WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

# Copy web files to ComfyUI's web extensions directory (similar to RyanOnTheInside approach)
def setup_web_extensions():
    try:
        import folder_paths
        # Get the current node directory
        current_dir = os.path.dirname(__file__)
        web_src_dir = os.path.join(current_dir, "web")
        
        # Find ComfyUI's web directory
        comfyui_dir = folder_paths.base_path
        web_extensions_dir = os.path.join(comfyui_dir, "web", "extensions", "Video_Compare_BMO")
        
        # Create extensions directory if it doesn't exist
        os.makedirs(web_extensions_dir, exist_ok=True)
        
        # Copy JavaScript files
        if os.path.exists(web_src_dir):
            for file_name in os.listdir(web_src_dir):
                if file_name.endswith('.js'):
                    src_file = os.path.join(web_src_dir, file_name)
                    dst_file = os.path.join(web_extensions_dir, file_name)
                    shutil.copy2(src_file, dst_file)
                    print(f"[Video_Compare_BMO] Copied extension file: {file_name}")
        
        print(f"[Video_Compare_BMO] Web extensions registered at: {web_extensions_dir}")
        
    except Exception as e:
        print(f"[Video_Compare_BMO] Failed to setup web extensions: {e}")

# Setup web extensions when the module is imported
setup_web_extensions() 