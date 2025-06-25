import torch
import numpy as np
import os
import json
import cv2
import uuid
from typing import Dict, Any, Tuple
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
    Simplified version for testing and debugging.
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
                "comparison_mode": (["side_by_side", "slider_blend", "split_screen"], {"default": "slider_blend"}),
                "frame_rate": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("comparison_result",)
    OUTPUT_NODE = True
    FUNCTION = "compare_videos"
    CATEGORY = "BMO"
    DESCRIPTION = "Compare two video sequences side-by-side"

    def compare_videos(self, video_a, video_b, comparison_mode, frame_rate):
        print(f"[Video_Compare_BMO] Starting comparison with mode: {comparison_mode}")
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
        
        video_a_path = os.path.join(temp_dir, f"video_compare_a_{video_id}.mp4")
        video_b_path = os.path.join(temp_dir, f"video_compare_b_{video_id}.mp4")
        
        # Save videos
        self.save_video(frames_a, video_a_path, frame_rate)
        self.save_video(frames_b, video_b_path, frame_rate)
        
        # Create comparison result (for now, just return the first video)
        result_frames = torch.from_numpy(frames_a.astype(np.float32) / 255.0)
        
        # Return data for the frontend
        return {
            "ui": {
                "video_a_url": f"/view?filename={os.path.basename(video_a_path)}&type=temp&subfolder=",
                "video_b_url": f"/view?filename={os.path.basename(video_b_path)}&type=temp&subfolder=",
                "comparison_mode": comparison_mode,
                "frame_count": min_frames,
                "frame_rate": frame_rate
            },
            "result": (result_frames,)
        }
    
    def save_video(self, frames, output_path, fps):
        """Save frames as MP4 video file using OpenCV"""
        if len(frames) == 0:
            print("[Video_Compare_BMO] Warning: No frames to save")
            return
            
        height, width = frames[0].shape[:2]
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
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

    def _sync_videos(self, images_a: torch.Tensor, images_b: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Synchronize video lengths by matching the shorter video."""
        frames_a = images_a.shape[0]
        frames_b = images_b.shape[0]

        if frames_a == frames_b:
            return images_a, images_b

        # Use the shorter video length
        target_frames = min(frames_a, frames_b)
        print(f"[Video_Compare_BMO] Syncing to {target_frames} frames")
        images_a = images_a[:target_frames]
        images_b = images_b[:target_frames]

        return images_a, images_b

    def _match_dimensions(self, images_a: torch.Tensor, images_b: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Match video dimensions."""
        _, h_a, w_a, c_a = images_a.shape
        _, h_b, w_b, c_b = images_b.shape

        # Use minimum dimensions
        target_h = min(h_a, h_b)
        target_w = min(w_a, w_b)
        target_c = min(c_a, c_b)
        
        print(f"[Video_Compare_BMO] Target dimensions: {target_h}x{target_w}x{target_c}")

        # Simple crop/pad approach
        images_a = self._resize_video(images_a, target_h, target_w, target_c)
        images_b = self._resize_video(images_b, target_h, target_w, target_c)

        return images_a, images_b

    def _resize_video(self, images: torch.Tensor, target_h: int, target_w: int, target_c: int) -> torch.Tensor:
        """Resize video to target dimensions."""
        frames, h, w, c = images.shape

        # Center crop if larger
        if h > target_h:
            start_h = (h - target_h) // 2
            images = images[:, start_h:start_h + target_h, :, :]
        if w > target_w:
            start_w = (w - target_w) // 2
            images = images[:, :, start_w:start_w + target_w, :]
        if c > target_c:
            images = images[:, :, :, :target_c]

        # Pad if smaller (simplified)
        if h < target_h or w < target_w or c < target_c:
            pad_h = max(0, target_h - h)
            pad_w = max(0, target_w - w)
            pad_c = max(0, target_c - c)
            
            # Pad: (left, right, top, bottom, front, back)
            padding = (0, pad_c, 0, pad_w, 0, pad_h, 0, 0)
            images = torch.nn.functional.pad(images, padding, mode='constant', value=0)

        return images

    def _side_by_side_compare(self, images_a: torch.Tensor, images_b: torch.Tensor) -> torch.Tensor:
        """Create a side-by-side comparison."""
        print(f"[Video_Compare_BMO] Creating side-by-side comparison")
        compared_images = torch.cat([images_a, images_b], dim=2)  # Concatenate along width
        return compared_images

    def _slider_blend_compare(self, images_a: torch.Tensor, images_b: torch.Tensor, split_position: float) -> torch.Tensor:
        """Create a blended comparison."""
        print(f"[Video_Compare_BMO] Creating blend comparison with alpha={split_position}")
        alpha = split_position
        compared_images = (1 - alpha) * images_a + alpha * images_b
        return compared_images.clamp(0, 1)

    def _split_screen_compare(self, images_a: torch.Tensor, images_b: torch.Tensor, split_position: float) -> torch.Tensor:
        """Create a split-screen comparison."""
        print(f"[Video_Compare_BMO] Creating split-screen comparison at position={split_position}")
        frames, h, w, c = images_a.shape
        split_x = int(w * split_position)
        print(f"[Video_Compare_BMO] Split at x={split_x} (width={w})")

        compared_images = torch.zeros_like(images_a)
        compared_images[:, :, :split_x, :] = images_a[:, :, :split_x, :]
        compared_images[:, :, split_x:, :] = images_b[:, :, split_x:, :]

        return compared_images 