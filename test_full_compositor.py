import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageOps

def create_rich_telegram_proof(
    output_path="/sdcard/Download/latest_automated_proof.jpg",
    channel_title="PR.social Update",
    subs_text="31.3K subscribers",
    avatar_path="/root/scripted/temp_avatar.jpg",
    post_text="PR Worker Telegram - Android Update\n\nDear users,\nWe have released a major update to PR Worker Telegram for Android.\nNew task types and automated checks are now live!\nStay subscribed to receive instant notifications.",
    views_str="10.3K",
    time_str="14:08",
    reactions_list=None,
    comments_count=38
):
    if reactions_list is None:
        reactions_list = ["❤️ 340", "👍 114", "🔥 33", "🤣 16"]

    base = Image.open('/root/scripted/master_telegram_real.jpg').convert('RGB')
    W, H = base.size # 459, 1024
    draw = ImageDraw.Draw(base)

    # Fonts
    font_bold_title = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 15)
    font_subs = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 11)
    font_author = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 13)
    font_post = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 12)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 10)
    font_react = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf", 11)
    font_mute = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 16)

    # 1. Overlay Header Pill (55, 52, 395, 100)
    pill_box = [55, 52, 395, 100]
    draw.rounded_rectangle(pill_box, radius=24, fill=(255, 255, 255))
    
    # Avatar (62, 57, 100, 95)
    av_size = (38, 38)
    if avatar_path and os.path.exists(avatar_path):
        try:
            av_img = Image.open(avatar_path).convert("RGBA").resize(av_size, Image.Resampling.LANCZOS)
            mask = Image.new("L", av_size, 0)
            ImageDraw.Draw(mask).ellipse([0, 0, av_size[0], av_size[1]], fill=255)
            av_circ = ImageOps.fit(av_img, mask.size, centering=(0.5, 0.5))
            av_circ.putalpha(mask)
            base.paste(av_circ, (62, 57), av_circ)
        except Exception:
            draw.ellipse([62, 57, 100, 95], fill=(30, 100, 180))
            draw.text((75, 66), channel_title[0].upper(), fill=(255, 255, 255), font=font_bold_title)
    else:
        draw.ellipse([62, 57, 100, 95], fill=(30, 100, 180))
        draw.text((75, 66), channel_title[0].upper(), fill=(255, 255, 255), font=font_bold_title)

    draw.text((108, 60), channel_title[:24], fill=(0, 0, 0), font=font_bold_title)
    draw.text((108, 78), subs_text, fill=(110, 115, 120), font=font_subs)

    # 2. Re-create White Post Bubble (12, 165, W - 12, 680)
    bubble_box = [12, 165, W - 12, 680]
    draw.rounded_rectangle(bubble_box, radius=16, fill=(255, 255, 255))

    # Author
    draw.text((28, 180), channel_title, fill=(36, 129, 204), font=font_author)

    # Post lines
    # Split text into clean wrapped chunks
    raw_lines = post_text.replace("**", "").split("\n")
    clean_lines = []
    for l in raw_lines:
        words = l.split(" ")
        cur_line = ""
        for w in words:
            if len(cur_line + " " + w) < 42:
                cur_line = (cur_line + " " + w).strip()
            else:
                clean_lines.append(cur_line)
                cur_line = w
        if cur_line:
            clean_lines.append(cur_line)

    cy = 205
    for l in clean_lines[:16]:
        draw.text((28, cy), l, fill=(20, 20, 20), font=font_post)
        cy += 18

    # Bottom of bubble: Views + Time
    draw.text((W - 130, 650), f"👁 {views_str}", fill=(130, 135, 140), font=font_small)
    draw.text((W - 65, 650), time_str, fill=(130, 135, 140), font=font_small)

    # 3. Reactions Bar below bubble (12, 695 to W - 12, 735)
    react_x = 24
    for r_item in reactions_list[:4]:
        # draw small reaction pill
        pill_w = 65
        draw.rounded_rectangle([react_x, 695, react_x + pill_w, 725], radius=14, fill=(235, 245, 255), outline=(210, 230, 250))
        draw.text((react_x + 8, 702), r_item, fill=(30, 50, 70), font=font_react)
        react_x += pill_w + 10

    # 4. Comments Bar (12, 745, W - 12, 785)
    if comments_count > 0:
        draw.rounded_rectangle([12, 745, W - 12, 785], radius=14, fill=(245, 248, 250))
        draw.text((30, 755), f"💬 {comments_count} comments", fill=(36, 129, 204), font=font_react)
        draw.text((W - 35, 755), "›", fill=(150, 155, 160), font=font_bold_title)

    # 5. Prominent MUTE Button at Bottom (65, 936, 395, 982)
    mute_pill = [65, 936, 395, 982]
    draw.rounded_rectangle(mute_pill, radius=24, fill=(255, 255, 255), outline=(225, 230, 235), width=1)
    cx = (65 + 395) // 2
    cy = (936 + 982) // 2
    draw.text((cx - 18, cy - 10), "Mute", fill=(36, 129, 204), font=font_mute)

    # Save
    base.save(output_path, "JPEG", quality=95)
    print("Full rich proof successfully created at:", output_path)

create_rich_telegram_proof()
