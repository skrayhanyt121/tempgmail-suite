import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

def create_realistic_telegram_proof(
    output_path="/sdcard/Download/realistic_telegram_proof.png",
    channel_title="PR.social Update",
    subs_text="42.8K subscribers",
    avatar_path="/root/scripted/temp_avatar.jpg",
    post_text="PR Worker Telegram - Android Update\n\nDear users,\nwe've released a major update to PR Worker Telegram.\nNew earning tasks are now live! Check the dashboard.",
    post_views="4.8K",
    post_time="13:45"
):
    # Dimensions matching standard Android 9:20 ratio: 720 x 1600
    W, H = 720, 1600
    
    # Fonts
    roboto_bold = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 26)
    roboto_med = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf", 22)
    roboto_reg = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 20)
    roboto_small = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 16)
    roboto_time = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf", 20)
    
    # Telegram Dark Theme Palette
    bg_color = (14, 22, 33)        # #0e1621 - Chat background
    header_color = (33, 45, 59)    # #212d3b - Header
    bubble_color = (24, 37, 51)    # #182533 - Post bubble
    bottom_color = (23, 33, 43)    # #17212b - Bottom bar
    accent_blue = (93, 165, 232)   # #5da5e8 - Telegram blue
    text_white = (255, 255, 255)
    text_gray = (130, 147, 161)    # #8293a1
    
    img = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Android Status Bar (0 to 60px)
    draw.rectangle([0, 0, W, 60], fill=header_color)
    # Clock on left
    draw.text((36, 18), "2:11", fill=text_white, font=roboto_time)
    # Status icons on right (WiFi, Signal, Battery 85%)
    # Signal bars
    for i in range(4):
        bx = W - 180 + i * 8
        by = 38 - (i + 1) * 4
        draw.rectangle([bx, by, bx + 5, 38], fill=text_white)
    # Wifi icon (simple clean arch)
    wx = W - 125
    draw.arc([wx - 10, 20, wx + 10, 40], start=200, end=340, fill=text_white, width=2)
    draw.arc([wx - 6, 25, wx + 6, 37], start=200, end=340, fill=text_white, width=2)
    draw.ellipse([wx - 2, 34, wx + 2, 38], fill=text_white)
    # Battery icon with percentage
    draw.rectangle([W - 75, 22, W - 35, 38], outline=text_white, width=2)
    draw.rectangle([W - 35, 26, W - 32, 34], fill=text_white)
    draw.rectangle([W - 71, 25, W - 45, 35], fill=text_white) # ~70% full
    draw.text((W - 105, 20), "78%", fill=text_white, font=roboto_small)

    # 2. Telegram Header Bar (60 to 180px)
    draw.rectangle([0, 60, W, 180], fill=header_color)
    
    # Back Arrow '<-'
    arrow_pts = [(40, 120), (60, 105), (60, 115), (75, 115), (75, 125), (60, 125), (60, 135)]
    # Draw clean back arrow
    draw.polygon([(42, 120), (58, 106), (58, 116), (82, 116), (82, 124), (58, 124), (58, 134)], fill=text_white)

    # Circular Avatar
    avatar_box = (100, 85, 175, 160)
    avatar_size = (75, 75)
    if os.path.exists(avatar_path):
        try:
            av_raw = Image.open(avatar_path).convert("RGBA").resize(avatar_size, Image.Resampling.LANCZOS)
            # Circular mask
            mask = Image.new("L", avatar_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, avatar_size[0], avatar_size[1]], fill=255)
            av_circ = ImageOps.fit(av_raw, mask.size, centering=(0.5, 0.5))
            av_circ.putalpha(mask)
            img.paste(av_circ, (100, 85), av_circ)
        except Exception as e:
            draw.ellipse([100, 85, 175, 160], fill=(43, 82, 120))
            draw.text((128, 105), channel_title[0].upper(), fill=text_white, font=roboto_bold)
    else:
        draw.ellipse([100, 85, 175, 160], fill=(43, 82, 120))
        draw.text((128, 105), channel_title[0].upper(), fill=text_white, font=roboto_bold)

    # Channel Title & Subscribers
    draw.text((195, 95), channel_title, fill=text_white, font=roboto_bold)
    draw.text((195, 130), subs_text, fill=text_gray, font=roboto_reg)

    # Right icons: Search & 3-dots
    # Search icon (circle + handle)
    draw.ellipse([W - 110, 110, W - 92, 128], outline=text_white, width=2)
    draw.line([W - 96, 124, W - 88, 132], fill=text_white, width=3)
    # 3 dots
    draw.ellipse([W - 50, 108, W - 44, 114], fill=text_white)
    draw.ellipse([W - 50, 118, W - 44, 124], fill=text_white)
    draw.ellipse([W - 50, 128, W - 44, 134], fill=text_white)

    # Subtle separator shadow
    draw.line([0, 180, W, 180], fill=(20, 28, 38), width=2)

    # 3. Chat Area Background with subtle Telegram style date pill
    date_pill_box = [W//2 - 70, 220, W//2 + 70, 255]
    draw.rounded_rectangle(date_pill_box, radius=16, fill=(28, 42, 56))
    draw.text((W//2 - 40, 227), "Today", fill=(145, 162, 178), font=roboto_med)

    # 4. Message Bubble
    bubble_x1, bubble_y1 = 30, 280
    bubble_x2, bubble_y2 = W - 30, 680
    draw.rounded_rectangle([bubble_x1, bubble_y1, bubble_x2, bubble_y2], radius=20, fill=bubble_color)

    # Channel name in post
    draw.text((bubble_x1 + 25, bubble_y1 + 20), channel_title, fill=accent_blue, font=roboto_bold)

    # Post content lines
    lines = [
        "PR Worker Telegram - Android Update",
        "",
        "Dear users,",
        "We have released a major update to PR Worker Telegram.",
        "New high-paying verification tasks are now live!",
        "Complete subscriptions, view posts and withdraw instantly.",
        "Stay subscribed for daily exclusive tasks."
    ]
    cur_y = bubble_y1 + 65
    for l in lines:
        draw.text((bubble_x1 + 25, cur_y), l, fill=text_white, font=roboto_reg)
        cur_y += 32

    # Bubble footer: View count + Eye + Timestamp
    # Eye icon
    eye_x = bubble_x2 - 170
    draw.ellipse([eye_x, bubble_y2 - 38, eye_x + 18, bubble_y2 - 24], outline=text_gray, width=2)
    draw.ellipse([eye_x + 6, bubble_y2 - 33, eye_x + 12, bubble_y2 - 29], fill=text_gray)
    draw.text((eye_x + 24, bubble_y2 - 42), post_views, fill=text_gray, font=roboto_small)
    draw.text((bubble_x2 - 75, bubble_y2 - 42), post_time, fill=text_gray, font=roboto_small)

    # Reaction Badge below post (Telegram reaction pill: 👍 142  🔥 89)
    react_box = [bubble_x1 + 10, bubble_y2 + 15, bubble_x1 + 160, bubble_y2 + 65]
    draw.rounded_rectangle(react_box, radius=20, fill=(24, 37, 51))
    draw.text((bubble_x1 + 30, bubble_y2 + 25), "👍 142", fill=text_white, font=roboto_med)

    # 5. Bottom Action Bar: "MUTE" (Proof of subscription!)
    bottom_y = H - 120
    draw.rectangle([0, bottom_y, W, H - 40], fill=bottom_color)
    draw.line([0, bottom_y, W, bottom_y], fill=(30, 42, 54), width=1)
    
    # Centered "MUTE" text
    mute_text = "MUTE"
    draw.text((W//2 - 35, bottom_y + 22), mute_text, fill=accent_blue, font=roboto_bold)

    # 6. Android Bottom Navigation Pill Bar (H - 40 to H)
    draw.rectangle([0, H - 40, W, H], fill=(0, 0, 0))
    # Navigation gesture pill in center
    draw.rounded_rectangle([W//2 - 90, H - 24, W//2 + 90, H - 16], radius=4, fill=(180, 180, 180))

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    print(f"Generated realistic proof saved to: {output_path}")

if __name__ == "__main__":
    create_realistic_telegram_proof()
