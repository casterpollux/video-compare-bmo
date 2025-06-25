#!/usr/bin/env python3
"""
Test script for Video Compare Tool
This script creates mock video tensors and tests the video comparison functionality
"""

import torch
import numpy as np
from video_compare_bmo import Video_Compare_BMO


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
    
    node = Video_Compare_BMO()
    
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
    
    node = Video_Compare_BMO()
    
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
    
    node = Video_Compare_BMO()
    
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
    
    node = Video_Compare_BMO()
    
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
    
    node = Video_Compare_BMO()
    
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
    print("Running Video Compare Tool Tests")
    print("=" * 40)
    
    try:
        test_video_sync()
        test_dimension_matching()
        test_comparison_modes()
        test_full_comparison()
        test_edge_cases()
        
        print("\n" + "=" * 40)
        print("🎉 All tests passed successfully!")
        print("\nThe Video Compare Tool is ready for use in ComfyUI.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main() 