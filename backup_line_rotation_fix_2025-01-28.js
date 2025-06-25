import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.log("[Video_Compare_BMO] Loading extension - Final state fix v2.2...");

// Helper function to create DOM elements
function createElement(tag, attrs = {}, ...children) {
    const el = document.createElement(tag);
    Object.assign(el, attrs);
    Object.assign(el.style, attrs.style || {});
    for (const child of children) {
        if (typeof child === 'string') {
            el.appendChild(document.createTextNode(child));
        } else if (child) {
            el.appendChild(child);
        }
    }
    return el;
}

app.registerExtension({
    name: "Video_Compare_BMO.Video_Compare_BMO",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Video_Compare_BMO") {
            console.log("[Video_Compare_BMO] Registering node - Clean implementation");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                console.log("[Video_Compare_BMO] Node created - using self-contained widget pattern");
                
                // Call original node creation if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                
                // Create the DOM container element
                const container = createElement("div", {
                    style: {
                        width: "100%",
                        height: "400px",
                        position: "relative",
                        backgroundColor: "#1a1a1a",
                        border: "2px solid #444",
                        borderRadius: "8px",
                        overflow: "hidden"
                    }
                });

                // Create the widget and get a direct reference to it
                const widget = this.addDOMWidget("video_comparer_widget", "div", container);
                
                // Set widget properties
                widget.computeSize = () => [500, 420];
                widget.serialize = false;
                
                // Initialize widget state (using custom property to avoid ComfyUI conflicts)
                widget.state = {
                    urlA: null,
                    urlB: null,
                    splitPosition: 0.5,
                    comparisonMode: 'slider',
                    sliderDirection: 'horizontal'
                };
                
                // Setup the video comparer UI
                this.setupVideoComparer(widget, container);
                
                // ATTACH THE UPDATE FUNCTION DIRECTLY TO THE WIDGET OBJECT
                widget.updateVideos = function(urlA, urlB, comparisonMode = 'slider', sliderDirection = 'horizontal') {
                    console.log("[Video_Compare_BMO] updateVideos correctly called on widget with:", urlA, urlB, "mode:", comparisonMode, "direction:", sliderDirection);
                    
                    // Store the URLs and mode
                    this.state.urlA = urlA;
                    this.state.urlB = urlB;
                    this.state.comparisonMode = comparisonMode;
                    this.state.sliderDirection = sliderDirection;
                    
                    // 'this' inside this function refers to the widget object itself
                    if (this.videoA && this.videoB) {
                        console.log("[Video_Compare_BMO] Setting video sources");
                        this.statusText.textContent = "Loading videos...";
                        
                        // Reset video sources
                        this.videoA.src = "";
                        this.videoB.src = "";
                        
                        // Apply layout based on comparison mode
                        this.applyComparisonMode(comparisonMode, sliderDirection);
                        
                        if (comparisonMode === 'side_by_side') {
                            // For side-by-side mode, show the combined video in videoA only
                            this.videoA.src = urlA;
                            this.videoA.load();
                            console.log("[Video_Compare_BMO] Loading combined side-by-side video");
                        } else {
                            // For slider mode, load both videos
                            this.videoA.src = urlA;
                            this.videoB.src = urlB;
                            this.videoA.load();
                            this.videoB.load();
                            console.log("[Video_Compare_BMO] Loading separate videos for slider mode");
                        }
                        
                        console.log("[Video_Compare_BMO] Video sources updated successfully");
                    } else {
                        console.error("[Video_Compare_BMO] updateVideos was called, but video elements were not found on the widget!");
                        console.log("[Video_Compare_BMO] Widget videoA:", this.videoA, "videoB:", this.videoB);
                    }
                };

                // Add layout switching function to widget
                widget.applyComparisonMode = function(mode, direction = 'horizontal') {
                    console.log("[Video_Compare_BMO] Applying comparison mode:", mode, "direction:", direction);
                    console.log("[Video_Compare_BMO] Current widget state:", this.state);
                    
                    if (mode === 'side_by_side') {
                        // Side-by-side mode: show only the combined video in videoA
                        this.videoA.style.position = "absolute";
                        this.videoA.style.top = "0";
                        this.videoA.style.left = "0";
                        this.videoA.style.width = "100%";
                        this.videoA.style.height = "100%";
                        this.videoA.style.clipPath = "none";
                        this.videoA.style.display = "block";
                        
                        // Hide videoB completely for side-by-side mode
                        this.videoB.style.display = "none";
                        
                        // Hide slider handle completely for side-by-side mode
                        this.sliderHandle.style.display = "none";
                        this.videoContainer.style.cursor = "default";
                        
                        // Update split indicator to show mode info
                        this.splitIndicator.style.display = "block";
                        this.splitIndicator.textContent = "Side-by-side mode";
                        
                        console.log("[Video_Compare_BMO] Side-by-side layout applied - showing combined video");
                    } else {
                        // Slider mode: overlapped videos with clip-path based on direction
                        this.videoA.style.position = "absolute";
                        this.videoA.style.top = "0";
                        this.videoA.style.left = "0";
                        this.videoA.style.width = "100%";
                        this.videoA.style.height = "100%";
                        this.videoA.style.clipPath = "none";
                        this.videoA.style.display = "block";
                        
                        this.videoB.style.position = "absolute";
                        this.videoB.style.top = "0";
                        this.videoB.style.left = "0";
                        this.videoB.style.width = "100%";
                        this.videoB.style.height = "100%";
                        this.videoB.style.display = "block";
                        
                        // Reset split position to 50% when changing directions
                        this.state.splitPosition = 0.5;
                        console.log("[Video_Compare_BMO] Reset split position to 50% for direction:", direction);
                        
                        // Reset slider handle appearance for interactive mode
                        this.sliderHandle.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
                        this.sliderHandle.style.pointerEvents = "none";
                        
                        // Apply initial clip-path and cursor based on direction
                        console.log("[Video_Compare_BMO] About to call updateSliderForDirection with:", direction, this.state.splitPosition);
                        this.updateSliderForDirection(direction, this.state.splitPosition);
                        
                        // Show slider elements
                        this.sliderHandle.style.display = "block";
                        this.splitIndicator.style.display = "block";
                        
                        console.log("[Video_Compare_BMO] Slider layout applied with direction:", direction);
                    }
                };

                // Add direction-specific slider update function
                widget.updateSliderForDirection = function(direction, splitPos) {
                    console.log(`[Video_Compare_BMO] updateSliderForDirection called with direction: ${direction}, splitPos: ${splitPos}`);
                    const clipPercent = splitPos * 100;
                    
                    // Reset all handle styles first
                    this.sliderHandle.style.borderRadius = "0";
                    this.sliderHandle.style.transform = "translateX(-50%)";
                    
                    console.log(`[Video_Compare_BMO] Applying ${direction} direction with ${clipPercent}% split`);
                    
                    switch(direction) {
                        case 'horizontal':
                            this.videoB.style.clipPath = `inset(0 0 0 ${clipPercent}%)`;
                            this.sliderHandle.style.left = `${clipPercent}%`;
                            this.sliderHandle.style.top = "0";
                            this.sliderHandle.style.width = "4px";
                            this.sliderHandle.style.height = "100%";
                            this.sliderHandle.style.transform = "translateX(-50%)";
                            this.videoContainer.style.cursor = "ew-resize";
                            console.log("[Video_Compare_BMO] Applied horizontal slider");
                            break;
                            
                        case 'vertical':
                            this.videoB.style.clipPath = `inset(${clipPercent}% 0 0 0)`;
                            this.sliderHandle.style.top = `${clipPercent}%`;
                            this.sliderHandle.style.left = "0";
                            this.sliderHandle.style.width = "100%";
                            this.sliderHandle.style.height = "4px";
                            this.sliderHandle.style.transform = "translateY(-50%)";
                            this.sliderHandle.style.borderRadius = "0";
                            this.sliderHandle.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
                            this.videoContainer.style.cursor = "ns-resize";
                            console.log("[Video_Compare_BMO] Applied vertical slider");
                            break;
                            
                        case 'diagonal':
                            // Diagonal clip-path using polygon for a line from top-left to bottom-right
                            // For splitPos 0: line at top-left corner (show all of videoB)
                            // For splitPos 1: line at bottom-right corner (hide all of videoB)
                            // The diagonal line equation is: x + y = splitPos * 200 (in percentage terms)
                            const linePosition = clipPercent * 2; // Convert 0-100% to 0-200% for diagonal
                            
                            let points;
                            if (linePosition <= 100) {
                                // Line is in upper-left triangle
                                points = [
                                    [0, linePosition],
                                    [linePosition, 0],
                                    [100, 0],
                                    [100, 100],
                                    [0, 100]
                                ];
                            } else {
                                // Line is in lower-right triangle
                                const adjustedPos = linePosition - 100;
                                points = [
                                    [adjustedPos, 100],
                                    [100, adjustedPos],
                                    [100, 100]
                                ];
                            }
                            
                            const polygonPath = points.map(p => `${p[0]}% ${p[1]}%`).join(', ');
                            this.videoB.style.clipPath = `polygon(${polygonPath})`;
                            
                            // Position handle on the diagonal line itself
                            // The diagonal line goes from top-left (0,0) to bottom-right (100,100)  
                            // At any split position, the line is at equation: x + y = clipPercent * 2
                            // The handle should be positioned at the midpoint of this diagonal line
                            let handleX, handleY;
                            
                            // Simple diagonal positioning: handle moves along the diagonal from (0,0) to (100,100)
                            handleX = clipPercent;
                            handleY = clipPercent;
                            
                            this.sliderHandle.style.left = `${handleX}%`;
                            this.sliderHandle.style.top = `${handleY}%`;
                            this.sliderHandle.style.width = "80px";
                            this.sliderHandle.style.height = "6px";
                            this.sliderHandle.style.borderRadius = "0";
                            this.sliderHandle.style.backgroundColor = "rgba(255, 255, 255, 1.0)";
                            this.sliderHandle.style.border = "2px solid rgba(0, 0, 0, 0.8)";
                            this.sliderHandle.style.boxShadow = "0 0 8px rgba(255, 255, 255, 0.8), 0 0 4px rgba(0, 0, 0, 0.8)";
                            this.sliderHandle.style.zIndex = "30";
                            this.sliderHandle.style.display = "block";
                            this.sliderHandle.style.visibility = "visible";
                            this.sliderHandle.style.opacity = "1";
                            this.sliderHandle.style.transform = "translate(-50%, -50%) rotate(45deg)";
                            this.videoContainer.style.cursor = "nwse-resize";
                            console.log(`[Video_Compare_BMO] Applied diagonal slider - linePos: ${linePosition}, handleX: ${handleX}%, handleY: ${handleY}%`);
                            break;
                            
                        default:
                            console.warn(`[Video_Compare_BMO] Unknown direction: ${direction}, defaulting to horizontal`);
                            this.videoB.style.clipPath = `inset(0 0 0 ${clipPercent}%)`;
                            this.sliderHandle.style.left = `${clipPercent}%`;
                            this.sliderHandle.style.top = "0";
                            this.sliderHandle.style.width = "4px";
                            this.sliderHandle.style.height = "100%";
                            this.sliderHandle.style.transform = "translateX(-50%)";
                            this.videoContainer.style.cursor = "ew-resize";
                    }
                    
                    this.splitIndicator.textContent = `Split: ${Math.round(clipPercent)}% (${direction})`;
                    console.log(`[Video_Compare_BMO] Updated split indicator: Split: ${Math.round(clipPercent)}% (${direction})`);
                };

                // --- The Isolated onExecuted Handler ---
                this.onExecuted = function(message) {
                    console.log("[Video_Compare_BMO] Node executed. Received data:", message);
                    if (widget && message && message.video_a_url && message.video_b_url) {
                        const urlA = message.video_a_url[0];
                        const urlB = message.video_b_url[0];
                        const comparisonMode = message.comparison_mode ? message.comparison_mode[0] : 'slider';
                        const sliderDirection = message.slider_direction ? message.slider_direction[0] : 'horizontal';
                        console.log("[Video_Compare_BMO] Calling widget.updateVideos with:", urlA, urlB, "mode:", comparisonMode, "direction:", sliderDirection);
                        widget.updateVideos(urlA, urlB, comparisonMode, sliderDirection);
                    } else {
                        console.log("[Video_Compare_BMO] Missing data - widget:", !!widget, "message:", !!message);
                    }
                };
                
                console.log("[Video_Compare_BMO] Self-contained widget setup complete");
            };
            
            // Setup video comparer function
            nodeType.prototype.setupVideoComparer = function(widget, container) {
                console.log("[Video_Compare_BMO] Setting up video comparer");
                
                // Create video container
                const videoContainer = createElement("div", {
                    style: {
                        position: "relative",
                        width: "100%",
                        height: "320px",
                        backgroundColor: "#000",
                        overflow: "hidden",
                        cursor: "ew-resize"
                    }
                });

                // Create video elements
                const videoA = createElement("video", {
                    muted: true,
                    loop: true,
                    style: {
                        position: "absolute",
                        top: "0",
                        left: "0",
                        width: "100%",
                        height: "100%",
                        objectFit: "contain"
                    }
                });

                const videoB = createElement("video", {
                    muted: true,
                    loop: true,
                    style: {
                        position: "absolute",
                        top: "0",
                        left: "0",
                        width: "100%",
                        height: "100%",
                        objectFit: "contain",
                        clipPath: "inset(0 0 0 50%)" // Start with 50% split
                    }
                });

                // Create slider handle
                const sliderHandle = createElement("div", {
                    style: {
                        position: "absolute",
                        top: "0",
                        left: "50%",
                        width: "4px",
                        height: "100%",
                        backgroundColor: "rgba(255, 255, 255, 0.8)",
                        transform: "translateX(-50%)",
                        pointerEvents: "none",
                        zIndex: "10"
                    }
                });

                // Create control panel
                const controlPanel = createElement("div", {
                    style: {
                        position: "absolute",
                        bottom: "0",
                        left: "0",
                        right: "0",
                        height: "80px",
                        backgroundColor: "rgba(0,0,0,0.8)",
                        padding: "10px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap"
                    }
                });

                // Create play/pause button
                const playButton = createElement("button", {
                    textContent: "▶ Play",
                    style: {
                        padding: "8px 16px",
                        backgroundColor: "#4CAF50",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "14px"
                    }
                });

                // Create status text
                const statusText = createElement("div", {
                    style: {
                        color: "#fff",
                        fontSize: "12px",
                        flex: "1",
                        textAlign: "center"
                    }
                }, "Load videos to begin comparison");

                // Create split indicator
                const splitIndicator = createElement("div", {
                    style: {
                        color: "#4CAF50",
                        fontSize: "11px",
                        fontWeight: "bold"
                    }
                }, "Split: 50%");

                // ATTACH ELEMENTS DIRECTLY TO THE WIDGET OBJECT
                widget.videoA = videoA;
                widget.videoB = videoB;
                widget.sliderHandle = sliderHandle;
                widget.playButton = playButton;
                widget.statusText = statusText;
                widget.splitIndicator = splitIndicator;
                widget.videoContainer = videoContainer;

                // Setup interactions
                this.setupVideoInteraction(widget, videoContainer);

                // Build DOM structure
                videoContainer.appendChild(videoA);
                videoContainer.appendChild(videoB);
                videoContainer.appendChild(sliderHandle);
                
                controlPanel.appendChild(playButton);
                controlPanel.appendChild(statusText);
                controlPanel.appendChild(splitIndicator);
                
                container.appendChild(videoContainer);
                container.appendChild(controlPanel);
                
                console.log("[Video_Compare_BMO] Video comparer setup complete");
            };

            // Setup video interactions
            nodeType.prototype.setupVideoInteraction = function(widget, videoContainer) {
                console.log("[Video_Compare_BMO] Setting up video interactions");
                
                const { videoA, videoB, sliderHandle, playButton, statusText, splitIndicator } = widget;
                let isDragging = false;

                // Play/pause functionality
                playButton.addEventListener('click', () => {
                    const isPaused = videoA.paused;
                    if (isPaused) {
                        if (widget.state.comparisonMode === 'side_by_side') {
                            // Side-by-side mode: only play videoA
                            videoA.play().then(() => {
                                playButton.textContent = "⏸ Pause";
                                statusText.textContent = "Playing side-by-side video";
                            }).catch(e => {
                                console.error("[Video_Compare_BMO] Error playing video:", e);
                                statusText.textContent = "Error playing video";
                            });
                        } else {
                            // Slider mode: play both videos synchronized
                            Promise.all([videoA.play(), videoB.play()]).then(() => {
                                playButton.textContent = "⏸ Pause";
                                statusText.textContent = "Playing synchronized videos";
                            }).catch(e => {
                                console.error("[Video_Compare_BMO] Error playing videos:", e);
                                statusText.textContent = "Error playing videos";
                            });
                        }
                    } else {
                        videoA.pause();
                        if (widget.state.comparisonMode !== 'side_by_side') {
                            videoB.pause();
                        }
                        playButton.textContent = "▶ Play";
                        statusText.textContent = "Videos paused";
                    }
                });

                // Video synchronization (only for slider mode)
                videoA.addEventListener('timeupdate', () => {
                    if (widget.state.comparisonMode === 'slider' && Math.abs(videoA.currentTime - videoB.currentTime) > 0.1) {
                        videoB.currentTime = videoA.currentTime;
                    }
                });

                // Mouse interaction for slider
                const updateSlider = (e) => {
                    // Only allow slider interaction in slider mode
                    if (widget.state.comparisonMode !== 'slider') {
                        return;
                    }
                    
                    const rect = videoContainer.getBoundingClientRect();
                    const direction = widget.state.sliderDirection;
                    let splitPos;
                    
                    switch(direction) {
                        case 'horizontal':
                            const x = e.clientX - rect.left;
                            splitPos = Math.max(0, Math.min(1, x / rect.width));
                            break;
                            
                        case 'vertical':
                            const y = e.clientY - rect.top;
                            splitPos = Math.max(0, Math.min(1, y / rect.height));
                            break;
                            
                        case 'diagonal':
                            // For diagonal, we need the position along the diagonal line from top-left to bottom-right
                            const dx = e.clientX - rect.left;
                            const dy = e.clientY - rect.top;
                            const normalizedX = dx / rect.width;
                            const normalizedY = dy / rect.height;
                            
                            // For a diagonal line from top-left to bottom-right:
                            // The line equation is: x + y = constant
                            // At any point on the line, x + y gives us the position along the diagonal
                            // When x + y = 0, we're at top-left corner (0% split)
                            // When x + y = 2, we're at bottom-right corner (100% split)
                            splitPos = Math.max(0, Math.min(1, (normalizedX + normalizedY) / 2));
                            
                            console.log(`[Video_Compare_BMO] Diagonal calculation: x=${normalizedX.toFixed(3)}, y=${normalizedY.toFixed(3)}, sum=${(normalizedX + normalizedY).toFixed(3)}, splitPos=${splitPos.toFixed(3)}`);
                            break;
                            
                        default:
                            splitPos = 0.5;
                    }
                    
                    widget.state.splitPosition = splitPos;
                    widget.updateSliderForDirection(direction, splitPos);
                };

                videoContainer.addEventListener('mousedown', (e) => {
                    // Only allow dragging in slider mode
                    if (widget.state.comparisonMode !== 'slider') {
                        return;
                    }
                    
                    isDragging = true;
                    videoContainer.style.cursor = 'grabbing';
                    updateSlider(e);
                });

                document.addEventListener('mousemove', (e) => {
                    if (isDragging && widget.state.comparisonMode === 'slider') {
                        updateSlider(e);
                    }
                });

                document.addEventListener('mouseup', () => {
                    if (isDragging) {
                        isDragging = false;
                        // Restore cursor based on mode and direction
                        if (widget.state.comparisonMode === 'slider') {
                            widget.updateSliderForDirection(widget.state.sliderDirection, widget.state.splitPosition);
                        } else {
                            videoContainer.style.cursor = 'default';
                        }
                    }
                });

                // Video loading events
                let videoALoaded = false;
                let videoBLoaded = false;
                
                const checkVideosLoaded = () => {
                    if (widget.state.comparisonMode === 'side_by_side') {
                        // Side-by-side mode: only need videoA to be loaded
                        if (videoALoaded) {
                            statusText.textContent = "Side-by-side video loaded - Click play to start";
                            console.log("[Video_Compare_BMO] Side-by-side video loaded successfully");
                        }
                    } else {
                        // Slider mode: need both videos to be loaded
                        if (videoALoaded && videoBLoaded) {
                            statusText.textContent = "Videos loaded - Click play to start";
                            console.log("[Video_Compare_BMO] Both videos loaded successfully");
                        }
                    }
                };
                
                videoA.addEventListener('loadeddata', () => {
                    console.log("[Video_Compare_BMO] Video A loaded");
                    videoALoaded = true;
                    checkVideosLoaded();
                });
                
                videoB.addEventListener('loadeddata', () => {
                    console.log("[Video_Compare_BMO] Video B loaded");
                    videoBLoaded = true;
                    checkVideosLoaded();
                });
                
                videoA.addEventListener('loadstart', () => {
                    console.log("[Video_Compare_BMO] Video A loading started");
                    videoALoaded = false;
                });
                
                videoB.addEventListener('loadstart', () => {
                    console.log("[Video_Compare_BMO] Video B loading started");
                    videoBLoaded = false;
                });

                // Handle errors
                videoA.addEventListener('error', (e) => {
                    console.error("[Video_Compare_BMO] Video A error:", e);
                    if (widget.state.comparisonMode === 'side_by_side') {
                        statusText.textContent = "Error loading side-by-side video";
                    } else {
                        statusText.textContent = "Error loading Video A";
                    }
                });

                videoB.addEventListener('error', (e) => {
                    console.error("[Video_Compare_BMO] Video B error:", e);
                    if (widget.state.comparisonMode !== 'side_by_side') {
                        statusText.textContent = "Error loading Video B";
                    }
                });
            };
        }
    }
});

// Global execution listener
api.addEventListener("execution_start", ({ detail }) => {
    console.log("[Video_Compare_BMO] Execution started for node:", detail);
});

api.addEventListener("executed", ({ detail }) => {
    console.log("[Video_Compare_BMO] Execution completed for node:", detail.node, "data:", detail.output);
    
    // The onExecuted handler in the node prototype should handle this
    // This global listener is for debugging purposes
});

console.log("[Video_Compare_BMO] Extension loaded successfully - Final state fix v2.2"); 