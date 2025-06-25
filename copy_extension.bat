@echo off
echo Copying Video_Compare_BMO extension to ComfyUI...

REM Create the extension directory if it doesn't exist
mkdir "D:\COMFY_INSTALLS\ComfyUI\web\extensions\Video_Compare_BMO" 2>nul

REM Copy the JavaScript file
copy "D:\CASTER_POLLUX_DEVELOPMENT\Video_Compare_BMO\web\video_compare_bmo.js" "D:\COMFY_INSTALLS\ComfyUI\web\extensions\Video_Compare_BMO\video_compare_bmo.js" /Y

REM Copy the CSS file
copy "D:\CASTER_POLLUX_DEVELOPMENT\Video_Compare_BMO\web\video_compare_bmo.css" "D:\COMFY_INSTALLS\ComfyUI\web\extensions\Video_Compare_BMO\video_compare_bmo.css" /Y

echo Extension files copied successfully!
echo Please refresh your ComfyUI browser tab.
pause 