#!/usr/bin/env python3
"""
Safe installation script for Video_Compare_BMO
This script safely copies files without using risky system commands
"""

import os
import shutil
import sys
from pathlib import Path

def safe_install():
    """Safely install Video_Compare_BMO to ComfyUI"""
    
    # Get current directory (where this script is located)
    current_dir = Path(__file__).parent
    
    # Ask user for ComfyUI path
    print("Video_Compare_BMO Safe Installation")
    print("=" * 40)
    
    default_path = "D:\\COMFY_INSTALLS\\ComfyUI\\custom_nodes"
    comfyui_path = input(f"Enter ComfyUI custom_nodes path (default: {default_path}): ").strip()
    
    if not comfyui_path:
        comfyui_path = default_path
    
    comfyui_path = Path(comfyui_path)
    
    # Validate ComfyUI path
    if not comfyui_path.exists():
        print(f"ERROR: ComfyUI path does not exist: {comfyui_path}")
        return False
    
    # Create target directory
    target_dir = comfyui_path / "Video_Compare_BMO"
    
    # Remove existing installation if it exists
    if target_dir.exists():
        print(f"Removing existing installation at: {target_dir}")
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"ERROR: Could not remove existing installation: {e}")
            return False
    
    # Create new directory
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {target_dir}")
    except Exception as e:
        print(f"ERROR: Could not create directory: {e}")
        return False
    
    # Files to copy
    files_to_copy = [
        "video_compare_bmo.py",
        "__init__.py"
    ]
    
    # Copy files
    for file_name in files_to_copy:
        src_file = current_dir / file_name
        dst_file = target_dir / file_name
        
        if not src_file.exists():
            print(f"WARNING: Source file not found: {src_file}")
            continue
            
        try:
            shutil.copy2(src_file, dst_file)
            print(f"Copied: {file_name}")
        except Exception as e:
            print(f"ERROR: Could not copy {file_name}: {e}")
            return False
    
    # Copy web directory
    web_src = current_dir / "web"
    web_dst = target_dir / "web"
    
    if web_src.exists():
        try:
            shutil.copytree(web_src, web_dst, dirs_exist_ok=True)
            print("Copied: web directory")
        except Exception as e:
            print(f"ERROR: Could not copy web directory: {e}")
            return False
    
    print("\n" + "=" * 40)
    print("Installation completed successfully!")
    print("Please restart ComfyUI to load the new node.")
    print("=" * 40)
    
    return True

if __name__ == "__main__":
    try:
        safe_install()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1) 