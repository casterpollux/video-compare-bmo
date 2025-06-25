#!/usr/bin/env python3
"""
Standalone test script for Video Compare Tool
This script creates mock video tensors and tests the video comparison functionality
without requiring ComfyUI dependencies
"""

import torch
import numpy as np
from typing import Dict, Any, Tuple


class Video_Compare_BMO_Standalone:
    """
    Standalone version of VideoCompareNode for testing without ComfyUI dependencies
    """

    def __init__(self):
        pass

    def compare_videos(
        self,
        video_a: torch.Tensor,
        video_b: torch.Tensor,
        comparison_mode: str = "slider_blend",
        split_position: float = 0.5,
        sync_playback: bool = True,
        output_fps: int = 30
    ) -> Tuple[torch.Tensor]:
        """Main function to compare two videos based on the selected mode."""
        # Ensure videos are in the correct format
        if video_a.dim() != 4 or video_b.dim() != 4:
            raise ValueError("Videos must be 4D tensors (B, H, W, C)")

        # Synchronize video lengths if needed
        if sync_playback:
            video_a, video_b = self._sync_videos(video_a, video_b)

        # Resize videos to match dimensions
        video_a, video_b = self._match_dimensions(video_a, video_b)

        # Perform comparison based on mode
        if comparison_mode == "side_by_side":
            compared_video = self._side_by_side_compare(video_a, video_b)
        elif comparison_mode == "slider_blend":
            compared_video = self._slider_blend_compare(video_a, video_b, split_position)
        elif comparison_mode == "split_screen":
            compared_video = self._split_screen_compare(video_a, video_b, split_position)
        else:
            raise ValueError(f"Unknown comparison mode: {comparison_mode}")

        return (compared_video,)

    def _sync_videos(self, video_a: torch.Tensor, video_b: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Synchronize video lengths by matching the shorter video to the longer one."""
        frames_a = video_a.shape[0]
        frames_b = video_b.shape[0]

        if frames_a == frames_b:
            return video_a, video_b

        # Determine target length (use the shorter video to avoid frame loss)
        target_frames = min(frames_a, frames_b)

        # Trim videos to match length
        video_a = video_a[:target_frames]
        video_b = video_b[:target_frames]

        return video_a, video_b

    def _match_dimensions(self, video_a: torch.Tensor, video_b: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Match video dimensions by resizing to the smaller common size."""
        _, h_a, w_a, c_a = video_a.shape
        _, h_b, w_b, c_b = video_b.shape

        # Use minimum dimensions to avoid upscaling
        target_h = min(h_a, h_b)
        target_w = min(w_a, w_b)
        target_c = min(c_a, c_b)

        # Resize if needed (simple crop/pad approach)
        video_a = self._resize_video(video_a, target_h, target_w, target_c)
        video_b = self._resize_video(video_b, target_h, target_w, target_c)

        return video_a, video_b

    def _resize_video(self, video: torch.Tensor, target_h: int, target_w: int, target_c: int) -> torch.Tensor:
        """Resize video to target dimensions."""
        frames, h, w, c = video.shape

        # Center crop if larger
        if h > target_h:
            start_h = (h - target_h) // 2
            video = video[:, start_h:start_h + target_h, :, :]
        if w > target_w:
            start_w = (w - target_w) // 2
            video = video[:, :, start_w:start_w + target_w, :]
        if c > target_c:
            video = video[:, :, :, :target_c]

        # Pad if smaller
        if h < target_h or w < target_w or c < target_c:
            pad_h = max(0, target_h - h)
            pad_w = max(0, target_w - w)
            pad_c = max(0, target_c - c)
            
            padding = (0, pad_c, 0, pad_w, 0, pad_h, 0, 0)
            video = torch.nn.functional.pad(video, padding, mode='constant', value=0)

        return video

    def _side_by_side_compare(self, video_a: torch.Tensor, video_b: torch.Tensor) -> torch.Tensor:
        """Create a side-by-side comparison of two videos."""
        # Concatenate videos horizontally
        compared_video = torch.cat([video_a, video_b], dim=2)  # Concatenate along width dimension
        return compared_video

    def _slider_blend_compare(self, video_a: torch.Tensor, video_b: torch.Tensor, split_position: float) -> torch.Tensor:
        """Create a blended comparison based on split position."""
        # Linear interpolation between the two videos
        alpha = split_position
        compared_video = (1 - alpha) * video_a + alpha * video_b
        return compared_video.clamp(0, 1)

    def _split_screen_compare(self, video_a: torch.Tensor, video_b: torch.Tensor, split_position: float) -> torch.Tensor:
        """Create a split-screen comparison with a vertical divider."""
        frames, h, w, c = video_a.shape
        split_x = int(w * split_position)

        # Create output tensor
        compared_video = torch.zeros_like(video_a)

        # Left side: video_a, Right side: video_b
        compared_video[:, :, :split_x, :] = video_a[:, :, :split_x, :]
        compared_video[:, :, split_x:, :] = video_b[:, :, split_x:, :]

        return compared_video


def create_mock_video(frames: int = 30, height: int = 240, width: int = 320, channels: int = 3) -> torch.Tensor:
    """Create a mock video tensor for testing."""
    # Create a gradient pattern that changes over time
    video = torch.zeros(frames, height, width, channels)
    
    for frame in range(frames):
        # Create a time-varying pattern
        x = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)
        y = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        t = frame / frames
        
        # Different patterns for different channels
        if channels >= 1:  # Red channel
            video[frame, :, :, 0] = torch.sin(2 * np.pi * (x + t)) * 0.5 + 0.5
        if channels >= 2:  # Green channel
            video[frame, :, :, 1] = torch.sin(2 * np.pi * (y + t)) * 0.5 + 0.5
        if channels >= 3:  # Blue channel
            video[frame, :, :, 2] = torch.sin(2 * np.pi * (x * y + t)) * 0.5 + 0.5
    
    return video


def test_video_sync():
    """Test video synchronization functionality."""
    print("Testing video synchronization...")
    
    node = Video_Compare_BMO_Standalone()
    
    # Create videos of different lengths
    video_a = create_mock_video(frames=30)
    video_b = create_mock_video(frames=45)
    
    print(f"Original lengths: Video A = {video_a.shape[0]}, Video B = {video_b.shape[0]}")
    
    synced_a, synced_b = node._sync_videos(video_a, video_b)
    
    print(f"Synced lengths: Video A = {synced_a.shape[0]}, Video B = {synced_b.shape[0]}")
    assert synced_a.shape[0] == synced_b.shape[0], "Videos should have same length after sync"
    print("✓ Video synchronization test passed")


def test_dimension_matching():
    """Test dimension matching functionality."""
    print("\nTesting dimension matching...")
    
    node = Video_Compare_BMO_Standalone()
    
    # Create videos of different dimensions
    video_a = create_mock_video(frames=30, height=240, width=320)
    video_b = create_mock_video(frames=30, height=180, width=240)
    
    print(f"Original dimensions: Video A = {video_a.shape}, Video B = {video_b.shape}")
    
    matched_a, matched_b = node._match_dimensions(video_a, video_b)
    
    print(f"Matched dimensions: Video A = {matched_a.shape}, Video B = {matched_b.shape}")
    assert matched_a.shape == matched_b.shape, "Videos should have same dimensions after matching"
    print("✓ Dimension matching test passed")


def test_comparison_modes():
    """Test all comparison modes."""
    print("\nTesting comparison modes...")
    
    node = Video_Compare_BMO_Standalone()
    
    # Create test videos
    video_a = create_mock_video(frames=10, height=100, width=100)
    video_b = create_mock_video(frames=10, height=100, width=100)
    
    # Test side-by-side mode
    result = node._side_by_side_compare(video_a, video_b)
    expected_width = video_a.shape[2] + video_b.shape[2]
    assert result.shape[2] == expected_width, f"Side-by-side width should be {expected_width}"
    print("✓ Side-by-side comparison test passed")
    
    # Test slider blend mode
    result = node._slider_blend_compare(video_a, video_b, 0.5)
    assert result.shape == video_a.shape, "Blend result should have same shape as input"
    assert torch.all(result >= 0) and torch.all(result <= 1), "Blend result should be in [0, 1] range"
    print("✓ Slider blend comparison test passed")
    
    # Test split screen mode
    result = node._split_screen_compare(video_a, video_b, 0.5)
    assert result.shape == video_a.shape, "Split screen result should have same shape as input"
    print("✓ Split screen comparison test passed")


def test_full_comparison():
    """Test the full comparison pipeline."""
    print("\nTesting full comparison pipeline...")
    
    node = Video_Compare_BMO_Standalone()
    
    # Create test videos
    video_a = create_mock_video(frames=15, height=120, width=160)
    video_b = create_mock_video(frames=20, height=100, width=140)
    
    # Test each comparison mode
    modes = ["side_by_side", "slider_blend", "split_screen"]
    
    for mode in modes:
        print(f"  Testing {mode} mode...")
        result = node.compare_videos(
            video_a=video_a,
            video_b=video_b,
            comparison_mode=mode,
            split_position=0.7,
            sync_playback=True,
            output_fps=30
        )
        
        assert isinstance(result, tuple) and len(result) == 1, "Should return tuple with one element"
        compared_video = result[0]
        assert isinstance(compared_video, torch.Tensor), "Result should be a tensor"
        print(f"    ✓ {mode} mode test passed - output shape: {compared_video.shape}")


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\nTesting edge cases...")
    
    node = Video_Compare_BMO_Standalone()
    
    # Test with identical videos
    video = create_mock_video(frames=10, height=50, width=50)
    result = node.compare_videos(video, video, "slider_blend", 0.5)
    assert torch.allclose(result[0], video, atol=1e-6), "Identical videos should produce same result"
    print("✓ Identical videos test passed")
    
    # Test extreme split positions
    video_a = create_mock_video(frames=5, height=50, width=50)
    video_b = create_mock_video(frames=5, height=50, width=50)
    
    # Split position 0.0 (should show only video A)
    result = node.compare_videos(video_a, video_b, "slider_blend", 0.0)
    assert torch.allclose(result[0], video_a, atol=1e-6), "Split position 0.0 should show only video A"
    print("✓ Extreme split position 0.0 test passed")
    
    # Split position 1.0 (should show only video B)
    result = node.compare_videos(video_a, video_b, "slider_blend", 1.0)
    assert torch.allclose(result[0], video_b, atol=1e-6), "Split position 1.0 should show only video B"
    print("✓ Extreme split position 1.0 test passed")


def main():
    """Run all tests."""
    print("Running Video Compare Tool Tests (Standalone)")
    print("=" * 45)
    
    try:
        test_video_sync()
        test_dimension_matching()
        test_comparison_modes()
        test_full_comparison()
        test_edge_cases()
        
        print("\n" + "=" * 45)
        print("🎉 All tests passed successfully!")
        print("\nThe Video Compare Tool core functionality is working correctly.")
        print("Ready for integration with ComfyUI!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main() 