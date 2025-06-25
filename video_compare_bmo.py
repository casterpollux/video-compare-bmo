import torch
import numpy as np
import os
import json
import cv2
import uuid
from typing import Dict, Any
from PIL import Image
import tempfile

# ComfyUI-specific imports with fallback for IDE compatibility
try:
    import folder_paths  # type: ignore
except ImportError:
    # This will only happen in development environment, not in ComfyUI
    class MockFolderPaths:
        @staticmethod
        def get_temp_directory():
            return tempfile.gettempdir()
    folder_paths = MockFolderPaths()

class Video_Compare_BMO:
    """
    A ComfyUI node that allows side-by-side comparison of two videos.
    This is an endpoint node that displays videos internally without outputs.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for the video compare node."""
        return {
            "required": {
                "video_a": ("IMAGE",),
                "video_b": ("IMAGE",),
                "comparison_mode": (["slider", "side_by_side"], {"default": "slider"}),
                "slider_direction": (["horizontal", "vertical", "diagonal"], {"default": "horizontal"}),
                "frame_rate": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1}),
            },
        }

    RETURN_TYPES = ()  # No outputs - this is an endpoint node
    OUTPUT_NODE = True
    FUNCTION = "compare_videos"
    CATEGORY = "BMO"
    DESCRIPTION = "Compare two video sequences side-by-side with interactive controls"

    def compare_videos(self, **kwargs):
        # Extract parameters by name to avoid order issues
        video_a = kwargs.get('video_a')
        video_b = kwargs.get('video_b') 
        comparison_mode = kwargs.get('comparison_mode', 'slider')
        slider_direction = kwargs.get('slider_direction', 'horizontal')
        frame_rate = kwargs.get('frame_rate', 30)
        
        # Debug: Print all received parameters
        print(f"[Video_Compare_BMO] DEBUG - Received kwargs: {list(kwargs.keys())}")
        print(f"[Video_Compare_BMO] DEBUG - Received parameters:")
        print(f"  video_a: {type(video_a)} shape: {video_a.shape if hasattr(video_a, 'shape') else 'N/A'}")
        print(f"  video_b: {type(video_b)} shape: {video_b.shape if hasattr(video_b, 'shape') else 'N/A'}")
        print(f"  comparison_mode: {comparison_mode} (type: {type(comparison_mode)})")
        print(f"  slider_direction: {slider_direction} (type: {type(slider_direction)})")
        print(f"  frame_rate: {frame_rate} (type: {type(frame_rate)})")
        
        print(f"[Video_Compare_BMO] Starting comparison with mode: {comparison_mode}, direction: {slider_direction}")
        print(f"[Video_Compare_BMO] Video A shape: {video_a.shape}")
        print(f"[Video_Compare_BMO] Video B shape: {video_b.shape}")
        
        # Convert tensors to numpy arrays
        frames_a = (video_a.cpu().numpy() * 255).astype(np.uint8)
        frames_b = (video_b.cpu().numpy() * 255).astype(np.uint8)
        
        # Ensure both videos have the same number of frames
        min_frames = min(len(frames_a), len(frames_b))
        frames_a = frames_a[:min_frames]
        frames_b = frames_b[:min_frames]
        
        print(f"[Video_Compare_BMO] Processing {min_frames} frames")
        
        # Create video files for the frontend
        temp_dir = folder_paths.get_temp_directory()
        video_id = str(uuid.uuid4())[:8]
        
        if comparison_mode == 'side_by_side':
            # Create a single concatenated video for side-by-side mode
            combined_frames = self.create_side_by_side_frames(frames_a, frames_b)
            combined_path = os.path.join(temp_dir, f"video_compare_combined_{video_id}.mov")
            self.save_video(combined_frames, combined_path, frame_rate)
            
            # Return single video URL for side-by-side mode
            return {
                "ui": {
                    "video_a_url": [f"/view?filename={os.path.basename(combined_path)}&type=temp&subfolder="],
                    "video_b_url": [""],  # Empty for side-by-side mode
                    "comparison_mode": [comparison_mode],
                    "slider_direction": [slider_direction],
                    "frame_count": [min_frames],
                    "frame_rate": [frame_rate]
                }
            }
        else:
            # Create separate videos for slider mode
            video_a_path = os.path.join(temp_dir, f"video_compare_a_{video_id}.mov")
            video_b_path = os.path.join(temp_dir, f"video_compare_b_{video_id}.mov")
            
            # Save videos
            self.save_video(frames_a, video_a_path, frame_rate)
            self.save_video(frames_b, video_b_path, frame_rate)
            
            # Return separate video URLs for slider mode
            return {
                "ui": {
                    "video_a_url": [f"/view?filename={os.path.basename(video_a_path)}&type=temp&subfolder="],
                    "video_b_url": [f"/view?filename={os.path.basename(video_b_path)}&type=temp&subfolder="],
                    "comparison_mode": [comparison_mode],
                    "slider_direction": [slider_direction],
                    "frame_count": [min_frames],
                    "frame_rate": [frame_rate]
                }
            }
    
    def create_side_by_side_frames(self, frames_a, frames_b):
        """Create side-by-side concatenated frames"""
        print(f"[Video_Compare_BMO] Creating side-by-side frames")
        
        # Get dimensions
        height_a, width_a = frames_a[0].shape[:2]
        height_b, width_b = frames_b[0].shape[:2]
        
        # Use the smaller height to maintain aspect ratio
        target_height = min(height_a, height_b)
        
        # Calculate proportional widths
        width_a_scaled = int(width_a * target_height / height_a)
        width_b_scaled = int(width_b * target_height / height_b)
        
        combined_frames = []
        
        for i in range(len(frames_a)):
            # Resize frames to target height while maintaining aspect ratio
            frame_a_resized = cv2.resize(frames_a[i], (width_a_scaled, target_height))
            frame_b_resized = cv2.resize(frames_b[i], (width_b_scaled, target_height))
            
            # Concatenate horizontally
            combined_frame = np.hstack((frame_a_resized, frame_b_resized))
            combined_frames.append(combined_frame)
        
        print(f"[Video_Compare_BMO] Created {len(combined_frames)} side-by-side frames with size: {combined_frames[0].shape}")
        return np.array(combined_frames)

    def save_video(self, frames, output_path, fps):
        """Save frames as video file using OpenCV with web-compatible codec"""
        if len(frames) == 0:
            print("[Video_Compare_BMO] Warning: No frames to save")
            return
            
        height, width = frames[0].shape[:2]
        
        # Use H.264 (avc1) codec for better web browser compatibility
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        try:
            for frame in frames:
                # Convert RGB to BGR for OpenCV
                if len(frame.shape) == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    frame_bgr = frame
                out.write(frame_bgr)
            
            print(f"[Video_Compare_BMO] Saved video: {output_path}")
        except Exception as e:
            print(f"[Video_Compare_BMO] Error saving video: {e}")
        finally:
            out.release()

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "Video_Compare_BMO": Video_Compare_BMO
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Video_Compare_BMO": "Video Compare BMO"
} 