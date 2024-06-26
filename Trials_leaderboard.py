import aiohttp
import asyncio
import os
import io
import json
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()

weapon_id = {
    "1":"NameIcon_Hammer.png",
    "2":"NameIcon_Axe.png",
    "3":"NameIcon_Blade.png",
    "4":"NameIcon_cb.png",
    "5":"NameIcon_WarPike.png",
    "6":"NameIcon_DP.png",
    "7":"NameIcon_AetherCaster.png",
}

role_id ={
    "PR_TEMPEST": "icon_omnicell_tempest.png",
    "PR_DARKNESS": "icon_omnicell_darkness.png",
    "PR_DISCIPLINE": "icon_omnicell_discipline.png",
    "PR_BASTION": "icon_omnicell_bastion.png",
    "PR_FRANK": "icon_omnicell_frank.png",
    "PR_ICEBORNE": "icon_omnicell_iceborne.png",
}

platform = {
    "WIN": "ico_platform_pc_default.png",
    "PSN": "ico_platform_ps_default.png",
    "XBL": "ico_platform_xbox_default.png",
    "SWT": "ico_platform_switch_default.png",
}

fonts = {
    "title_font": "INFECTED.ttf",
    "items_font": "GothicA1-Medium.ttf",
}


async def fetch_trials_leaderboard(week,session_token):
    url = "https://leaderboards-prod.steelyard.ca/trials/leaderboards/all"
    headers = {
        "Authorization": f"BEARER {session_token}",
    }
    data = {
        "difficulty": 1,
        "page": 0,
        "page_size": 100,
        "trial_id": f"Arena_MatchmakerHunt_Elite_New_00{week}",
        "target_platforms": []
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, timeout=5) as response:
            return await response.json()

def convert_to_time(value):
    if value >= 60000:  # If the value is greater than or equal to 1 minute (60000 milliseconds), convert to minutes
        seconds = value // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes} min {seconds} sec"
    else:  # Otherwise, treat it as seconds
        seconds = value // 1000
        return f"{seconds}.{str(value)[-3:]} sec"

def get_path(filename):
   # Get the current directory
    current_directory = os.getcwd()
    # Recursively search for the file in the current directory and its subdirectories
    for root, dirs, files in os.walk(current_directory):
        if filename in files:
            file_path = os.path.join(root, filename)
            return file_path

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def prep_paste_img(img_filename,size):
    image_to_paste = Image.open(get_path(img_filename))
    resized_image = image_to_paste.resize(size)
    return resized_image

async def getImage_group_leaderboard(leaderboard_data,current_behemoth,current_rotation_time):
    Title_font = ImageFont.truetype(get_path("INFECTED.ttf"), size=106)
    # item_font = ImageFont.truetype(get_path("NotoSansJP-Regular.ttf"), size=40)
    item_font = ImageFont.truetype(get_path("Customfont.ttf"), size=40)
    
    img = Image.new('RGB', (1600, 1100), color='#313338')
    draw = ImageDraw.Draw(img)

    draw.text((300, 30), f"Trials Champions Group", fill="white", font=Title_font)
    draw.text((660, 145), current_rotation_time, fill="#49be25", font=item_font)

    behemoth_icon = Image.open(get_path(f"{current_behemoth}.png")).resize((290,250))
    img.paste(behemoth_icon, (0, -20), mask=behemoth_icon.split()[3])
    x, y = 100, 220

    # Pre-resize weapon and role icons
    icon_size = (75, 75)
    resized_weapon_icons = {weapon_id: prep_paste_img(weapon_path, icon_size) for weapon_id, weapon_path in weapon_id.items()}
    resized_role_icons = {role_id: prep_paste_img(role_path, icon_size) for role_id, role_path in role_id.items()}

    # Define custom coordinates for each piece of information
    for i, trials_Group in enumerate(leaderboard_data):
        if i == 0:
            fill = "#FFD700"  # Gold
        elif i == 1:
            fill = "#E0E0E0"  # Brighter Silver
        elif i == 2:
            fill = "#CD853F"  # Brighter Bronze
        else:
            fill = "white"

        draw.text((x-60, y+50), f"{i+1}", fill=fill, font=item_font)
        
        entry_x = x
        entry_y = y
        for i, entry in enumerate(trials_Group['entries']):
            weapon_icon = resized_weapon_icons[str(entry['weapon'])]
            role_icon = resized_role_icons[str(entry['player_role_id'])]
            player_name = entry['platform_name']

            img.paste(weapon_icon, (entry_x, entry_y+5), mask=weapon_icon.split()[3])
            img.paste(role_icon, (entry_x+50+20, entry_y+5), mask=role_icon.split()[3])
            draw.text((entry_x+150, entry_y+5), player_name, fill=fill, font=item_font)
            entry_x += 520
            if i == 1:
                entry_x = x
                entry_y += 65

        # Draw remaining_time
        remaining_time = convert_to_time(trials_Group['completion_time'])
        draw.text((1270, y+35), f"{remaining_time}", fill=fill, font=item_font)

        y += 170
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    return img_bytes_io
    # img.save('tlb.png', format='PNG')

async def getImage_solo_leaderboard(leaderboard_data,current_behemoth,current_rotation_time):
    Title_font = ImageFont.truetype(get_path("INFECTED.ttf"), size=75)
    # item_font = ImageFont.truetype(get_path("NotoSansJP-Regular.ttf"), size=30)
    item_font = ImageFont.truetype(get_path("Customfont.ttf"), size=30)

    # Open the provided background image
    img = Image.new('RGB', (1024, 700), color='#313338')
    draw = ImageDraw.Draw(img)

    draw.text((220, 40), f"Trials Champions Solo", fill="white", font=Title_font)
    draw.text((420, 135), current_rotation_time, fill="#49be25", font=item_font)
    
    behemoth_icon = Image.open(get_path(f"{current_behemoth}.png")).resize((250,240))
    img.paste(behemoth_icon, (-20, -30), mask=behemoth_icon.split()[3])

    x, y = 70, 200

    # Pre-resize weapon, role, and platform icons
    icon_size = (70, 70)
    resized_weapon_icons = {weapon_id: prep_paste_img(weapon_path, icon_size) for weapon_id, weapon_path in weapon_id.items()}
    resized_role_icons = {role_id: prep_paste_img(role_path, icon_size) for role_id, role_path in role_id.items()}
    resized_platform_icons = {platform_id: prep_paste_img(platform_path, (50, 50)) for platform_id, platform_path in platform.items()}

    # Define custom coordinates for each piece of information
    for i, entry in enumerate(leaderboard_data):
        if i == 0:
            fill = "#FFD700"  # Gold
        elif i == 1:
            fill = "#E0E0E0"  # Brighter Silver
        elif i == 2:
            fill = "#CD853F"  # Brighter Bronze
        else:
            fill = "white"

        draw.text((x-30, y+18), f"{i+1}", fill=fill, font=item_font)
        
        weapon_icon = resized_weapon_icons[str(entry['weapon'])]
        role_icon = resized_role_icons[str(entry['player_role_id'])]
        platform_icon = resized_platform_icons[str(entry['platform'])]
        
        img.paste(weapon_icon, (x, y+5), mask=weapon_icon.split()[3])
        img.paste(role_icon, (x+50+20, y+5), mask=role_icon.split()[3])
        
        draw.text((x+150, y+18), entry['platform_name'], fill=fill, font=item_font)
        width,_ = get_text_dimensions(entry['platform_name'], item_font)
        
        img.paste(platform_icon, (x+160+width, y+15), mask=platform_icon.split()[3])

        completion_time = convert_to_time(entry['completion_time'])
        draw.text((800, y+18), f"{completion_time}", fill=fill, font=item_font)

        y += 100
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    return img_bytes_io
    # img.save("lb.png", format="PNG")


# async def main():
#     print("called main")
#     await getImage_Trials_leaderboard(58)

# # Run the asyncio event loop
# if __name__ == "__main__":
#     print("called name")
#     asyncio.run(main())