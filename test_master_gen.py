from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

def generate_from_master(
    output_path="/sdcard/Download/realistic_master_proof.png",
    channel_title="Россия на максималках",
    subs_text="128.5K subscribers",
    avatar_path=None,
    post_title="Главные новости дня",
    post_body="Оперативная сводка и эксклюзивные материалы уже на канале.\nПодписывайтесь и оставайтесь в курсе всех событий!",
    post_time="14:15",
    post_views="15.2K"
):
    base = Image.open('/root/scripted/master_telegram_real.jpg').convert('RGB')
    W, H = base.size # 459, 1024
    
    draw = ImageDraw.Draw(base)
    
    # Fonts
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 15)
    font_subs = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 11)
    font_post_title = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 14)
    font_post_text = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 13)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 10)

    # 1. Overlay the Header Pill
    # Pill box: (55, 52, 395, 100)
    pill_box = [55, 52, 395, 100]
    draw.rounded_rectangle(pill_box, radius=24, fill=(255, 255, 255))
    
    # Avatar inside pill: circle at (62, 57, 95, 95) -> 38x38
    av_size = (38, 38)
    if avatar_path and os.path.exists(avatar_path):
        av_img = Image.open(avatar_path).convert("RGBA").resize(av_size, Image.Resampling.LANCZOS)
        mask = Image.new("L", av_size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, av_size[0], av_size[1]], fill=255)
        av_circ = ImageOps.fit(av_img, mask.size, centering=(0.5, 0.5))
        av_circ.putalpha(mask)
        base.paste(av_circ, (62, 57), av_circ)
    else:
        draw.ellipse([62, 57, 100, 95], fill=(40, 120, 200))
        draw.text((75, 66), channel_title[0].upper(), fill=(255, 255, 255), font=font_title)
        
    # Title & Subtitle inside pill
    draw.text((108, 60), channel_title[:24], fill=(0, 0, 0), font=font_title)
    draw.text((108, 78), subs_text, fill=(110, 115, 120), font=font_subs)

    # 2. Re-create the Post Bubble (from y=170 to y=520)
    # Clear old bubble area and draw clean Telegram bubble
    bubble_box = [12, 165, W - 12, 500]
    draw.rounded_rectangle(bubble_box, radius=16, fill=(255, 255, 255))
    
    # Post author / channel header inside bubble
    draw.text((28, 180), channel_title, fill=(42, 130, 218), font=font_post_title)
    
    # Post body
    lines = [
        post_title,
        "",
        post_body[:100],
        post_body[100:200] if len(post_body) > 100 else "",
        "",
        "Следите за обновлениями на нашем канале!"
    ]
    lines = [l for l in lines if l != ""]
    cy = 210
    for l in lines:
        draw.text((28, cy), l, fill=(20, 20, 20), font=font_post_text)
        cy += 20
        
    # Bubble footer: View count + Time
    draw.text((W - 130, 475), f"👁 {post_views}", fill=(130, 135, 140), font=font_small)
    draw.text((W - 65, 475), post_time, fill=(130, 135, 140), font=font_small)

    # Save realistic proof
    base.save(output_path, "JPEG", quality=95)
    print("Master-based realistic proof generated:", output_path)

generate_from_master()
