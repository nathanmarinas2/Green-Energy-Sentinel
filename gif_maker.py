
import cv2
from PIL import Image
import os

def make_gif(input_mp4, output_gif, width=480, skip_frames=2):
    print(f"🎬 Processing {input_mp4}...")
    cap = cv2.VideoCapture(input_mp4)
    if not cap.isOpened():
        print("❌ Could not open video file.")
        return

    frames = []
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Skip frames to reduce size and FPS
        if count % skip_frames == 0:
            # Resize
            h, w = frame.shape[:2]
            r = width / float(w)
            dim = (width, int(h * r))
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            
            # Convert BGR to RGB (OpenCV uses BGR, Pillow uses RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame_rgb))
            
        count += 1
        # Limit total frames to avoid huge memory/files (e.g. max 100 frames)
        if len(frames) > 100:
            break

    cap.release()
    
    if frames:
        print(f"💾 Saving GIF ({len(frames)} frames)...")
        # Save as GIF
        frames[0].save(
            output_gif,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=100, # 100ms per frame = 10fps
            loop=0
        )
        print(f"✅ Created: {output_gif}")
    else:
        print("❌ No frames extracted.")

if __name__ == "__main__":
    if os.path.exists("reports/video3D.mp4"):
        make_gif("reports/video3D.mp4", "reports/demo_3d.gif", width=480, skip_frames=5)
    
    if os.path.exists("reports/timelapse_rayos.mp4"):
        make_gif("reports/timelapse_rayos.mp4", "reports/demo_timelapse.gif", width=480, skip_frames=5)
