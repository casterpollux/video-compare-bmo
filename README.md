# Video Compare BMO for ComfyUI

A custom ComfyUI node that allows side-by-side comparison of two videos with an interactive slider interface, inspired by rgthree's image compare tool.


![demo 1](https://github.com/casterpollux/video-compare-bmo/blob/master/examples/diff.gif)
![demo 2](https://github.com/casterpollux/video-compare-bmo/blob/master/examples/horixzontal.gif)
![demo 3](https://github.com/casterpollux/video-compare-bmo/blob/master/examples/side.gif)



## Features

- **Interactive Slider**: Real-time comparison with a draggable slider
- **Multiple Comparison Modes**:
  - **Slider Blend**: Smoothly blend between two videos using alpha compositing
  - **Split Screen**: Split-screen view with adjustable vertical divider
  - **Side by Side**: Traditional side-by-side comparison
- **Synchronized Playback**: Keep both videos in sync during playback
- **Preview Dialog**: Dedicated comparison interface with video controls
- **Responsive Design**: Works on different screen sizes

## Installation

1. Clone or download this repository to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   git clone https://github.com/yourusername/video-compare-bmo.git
   ```

2. Restart ComfyUI

3. The "Video Compare BMO" node will appear in the `bmo` category

## Usage

### Basic Usage

1. **Add the Node**: In ComfyUI, add the "Video Compare BMO" node from the `bmo` category

2. **Connect Videos**: Connect two video sources to the `video_a` and `video_b` inputs

3. **Configure Settings**:
   - **Comparison Mode**: Choose between `slider_blend`, `split_screen`, or `side_by_side`
   - **Split Position**: Adjust the slider position (0.0 = full video A, 1.0 = full video B)
   - **Sync Playback**: Enable/disable video synchronization
   - **Output FPS**: Set the output frame rate

4. **Preview**: Click the "Preview Comparison" button to open the interactive comparison dialog

### Comparison Modes

#### Slider Blend Mode
Smoothly blends between the two videos based on the split position:
- `0.0`: Shows only video A
- `0.5`: Shows 50% blend of both videos
- `1.0`: Shows only video B

#### Split Screen Mode
Creates a vertical split-screen view:
- Left side shows video A
- Right side shows video B
- Slider controls the position of the vertical divider

#### Side by Side Mode
Places both videos side by side horizontally for easy comparison.

### Interactive Preview

The preview dialog provides:
- **Real-time comparison** with interactive slider
- **Synchronized video playback** controls
- **Play/Pause/Reset** buttons
- **Visual slider line** showing the current split position

## API Reference

### Input Types

```python
{
    "required": {
        "video_a": ("VIDEO",),      # First video for comparison
        "video_b": ("VIDEO",),      # Second video for comparison
    },
    "optional": {
        "comparison_mode": (["side_by_side", "slider_blend", "split_screen"],),
        "split_position": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
        "sync_playback": ("BOOLEAN", {"default": True}),
        "output_fps": ("INT", {"default": 30, "min": 1, "max": 120}),
    }
}
```

### Output Types

- `compared_video`: The resulting comparison video tensor

## Examples

### Example 1: Basic Video Comparison
```
Load Video A → Video Compare BMO → Save Video
Load Video B → ↗
```

### Example 2: AI Model Comparison
```
Text Prompt → AI Video Model A → Video Compare BMO → Preview
          → AI Video Model B → ↗
```

### Example 3: Before/After Comparison
```
Original Video → Video Processing → Video Compare BMO → Save Result
             → ↗
```

## Technical Details

### Video Processing
- Videos are automatically synchronized to the same length (using the shorter duration)
- Dimensions are matched by cropping/padding to the smaller common size
- Supports different frame rates with configurable output FPS

### Performance Considerations
- Uses efficient tensor operations for real-time blending
- Memory usage scales with video resolution and length
- Optimized for GPU acceleration when available

## Troubleshooting

### Common Issues

1. **Videos not loading in preview**:
   - Ensure videos are in a supported format (MP4, WebM, etc.)
   - Check that video tensors are properly formatted (B, H, W, C)

2. **Synchronization issues**:
   - Enable "Sync Playback" option
   - Ensure both videos have similar frame rates

3. **Performance issues**:
   - Reduce video resolution for better performance
   - Lower the output FPS if needed

### Error Messages

- `"Videos must be 4D tensors (B, H, W, C)"`: Input videos are not in the correct tensor format
- `"Unknown comparison mode"`: Invalid comparison mode specified

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by [rgthree's ComfyUI extensions](https://github.com/rgthree/rgthree-comfy)
- Built for the ComfyUI community

## Changelog

### v1.0.0
- Initial release
- Three comparison modes
- Interactive preview dialog
- Synchronized playback
- Responsive design 
