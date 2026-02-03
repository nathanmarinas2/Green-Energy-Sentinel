
from moviepy.editor import VideoFileClip
import os

def convert_to_gif(input_path, output_path, resize_width=600, fps=10, speed=1.5):
    print(f"🔄 Convirtiendo {input_path} a GIF...")
    try:
        # Cargar video
        clip = VideoFileClip(input_path)
        
        # Acelerar un poco para que sea más dinámico (speed factor)
        clip = clip.speedx(speed)
        
        # Redimensionar para reducir peso (GitHub recomienda < 5MB idealmente, aunque soporta más)
        clip = clip.resize(width=resize_width)
        
        # Guardar como GIF
        print("   💾 Renderizando GIF (esto puede tardar un poco)...")
        clip.write_gif(output_path, fps=fps, logger=None) # logger=None para menos ruido
        
        print(f"✅ GIF guardado: {output_path}")
        
    except Exception as e:
        print(f"❌ Error convirtiendo {input_path}: {e}")

if __name__ == "__main__":
    # 1. Video 3D
    if os.path.exists("reports/video3D.mp4"):
        convert_to_gif("reports/video3D.mp4", "reports/feature_3d_viz.gif", resize_width=500, fps=12, speed=1.0)
    
    # 2. Timelapse 2D
    if os.path.exists("reports/timelapse_rayos.mp4"):
        # Este video es largo, lo aceleramos más
        convert_to_gif("reports/timelapse_rayos.mp4", "reports/feature_timelapse.gif", resize_width=500, fps=10, speed=2.0)
