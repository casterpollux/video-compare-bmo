# Video_Compare_BMO - Safe Installation Guide

## ⚠️ IMPORTANT: Safe Installation Only

**DO NOT use PowerShell commands or manual file manipulation to install this node.**  
**Use only the provided safe installation script.**

## What This Node Does

Video_Compare_BMO allows side-by-side comparison of two video sequences in ComfyUI with:
- Interactive slider comparison
- Side-by-side view
- Split-screen mode
- Adjustable frame rate (1-60 FPS, default: 30)

## Safe Installation Method

### Option 1: Using the Safe Installation Script (Recommended)

1. **Navigate to this directory** in your terminal/command prompt
2. **Run the safe installation script**:
   ```bash
   python safe_install.py
   ```
3. **Enter your ComfyUI path** when prompted (or press Enter for default)
4. **Restart ComfyUI completely** (don't just refresh browser)

### Option 2: Manual Copy (Advanced Users Only)

If you must copy manually:

1. **Copy these files only**:
   - `video_compare_bmo.py`
   - `__init__.py`
   - `web/` directory (entire folder)

2. **Copy to**: `[ComfyUI]/custom_nodes/Video_Compare_BMO/`

3. **Restart ComfyUI completely**

## Node Configuration

The node is pre-configured with safe defaults:

```python
"frame_rate": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1})
```

- **Default FPS**: 30 (standard video rate)
- **Range**: 1-60 FPS (covers all practical use cases)
- **User adjustable**: Yes, via the node interface

## Troubleshooting

### Frame Rate Validation Error
If you see: `Value 0 smaller than min of 1: frame_rate`

**Solution**: Completely restart ComfyUI (not just browser refresh)

### Node Not Appearing
1. Check that all files are in the correct location
2. Restart ComfyUI completely
3. Check console for error messages

### Environment Corruption
**Never use PowerShell timestamp manipulation or risky system commands.**
If your environment gets corrupted, you may need to reinstall ComfyUI.

## File Structure

```
Video_Compare_BMO/
├── video_compare_bmo.py      # Main node implementation
├── __init__.py               # ComfyUI registration
├── web/
│   ├── video_compare_bmo.js  # Frontend interface
│   └── video_compare_bmo.css # Styling
├── safe_install.py           # Safe installation script
└── SAFE_INSTALLATION.md     # This guide
```

## Usage

1. Add "Video Compare BMO" node to your workflow
2. Connect two IMAGE inputs (video sequences)
3. Choose comparison mode: slider_blend, side_by_side, or split_screen
4. Adjust frame rate if needed (default 30 FPS works for most cases)
5. Run the workflow

The node will create an interactive video comparison widget in the UI.

## Support

If you encounter issues:
1. First try restarting ComfyUI completely
2. Check that frame_rate is set to a value between 1-60
3. Verify all files are correctly installed
4. Check ComfyUI console for error messages

**Remember: Always use safe installation methods to avoid environment corruption.** 