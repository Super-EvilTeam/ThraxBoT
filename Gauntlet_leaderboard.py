import time
import requests,json
import io
from PIL import Image, ImageDraw, ImageFont
from build_finder import get_path

def seconds_to_minutes(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def getImage_gauntlet_leaderboard(season_title,season_timeline):
    try:
        with open("gauntlet.json", 'r',encoding='utf-8') as file:
            leaderboard = json.load(file)

        # Open the provided background image
        img = Image.open(get_path("Board_background.png"))
        draw = ImageDraw.Draw(img)

        font_path = "Roboto-Regular.ttf"
        font = ImageFont.truetype(get_path(font_path), 24)
        Title_font = ImageFont.truetype(get_path(font_path), 35)

        Title_width,_ = get_text_dimensions(season_title,Title_font)
        Timeline_width,_ = get_text_dimensions(season_timeline,Title_font)
        Title_x = (1164 - Title_width) // 2
        Timeline_x = (1164 - Timeline_width) // 2

        draw.text((Title_x, 0), season_title, fill="white", font=Title_font)
        draw.text((Timeline_x, 50), season_timeline, fill="#49be25", font=Title_font)
        

        draw.text((48, 112), f"Rank", fill="white", font=font)
        draw.text((180, 112), f"Guild", fill="white", font=font)
        draw.text((800, 112), f"Level", fill="white", font=font)
        draw.text((950, 112), f"Time Left", fill="white", font=font)

        # Use a truetype font file (replace 'arial.ttf' with the path to your font file)

        font = ImageFont.truetype(get_path(font_path), 30)
        x, y = 150, 172

        # Define custom coordinates for each piece of information
        for i, guild_info in enumerate(leaderboard):
            if i == 0:
                fill = "#FFD700"  # Gold
            elif i == 1:
                fill = "#E0E0E0"  # Brighter Silver
            elif i == 2:
                fill = "#CD853F"  # Brighter Bronze
            else:
                fill = "white"

            # Draw guild_name
            draw.text((66, y+28), f"{i+1}", fill=fill, font=font)

            draw.text((x, y+5), f"{guild_info['guild_name']}", fill=fill, font=font)

            # Draw guild_nameplate
            draw.text((x, y + 45), f"{guild_info['guild_nameplate']}", fill=fill, font=font)

            # Draw level
            draw.text((800, y+20), f"{guild_info['level']}", fill=fill, font=font)

            # Draw remaining_time
            remaining_time = seconds_to_minutes(guild_info['remaining_sec'])
            draw.text((960, y+20), f"{remaining_time}", fill=fill, font=font)

            y += 130

        img_bytes_io = io.BytesIO()
        img.save(img_bytes_io, format='PNG')
        img_bytes_io.seek(0)
        return img_bytes_io

    except requests.RequestException as e:
        print(f"An error occurred: {e}")