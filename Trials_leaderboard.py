import requests
import io
from PIL import Image, ImageDraw, ImageFont
import json
import os
from dotenv import load_dotenv
load_dotenv()

def get_trials_leaderboard(week):
    url = "https://leaderboards-prod.steelyard.ca/trials/leaderboards/all"
    headers = {
        "Authorization": f"BEARER {os.environ.get('SESSION_TOKEN')}",
    }
    data = {
            "difficulty": 1,
            "page": 0,
            "page_size": 100,
            "trial_id": f"Arena_MatchmakerHunt_Elite_New_00{week}",
            "target_platforms": []
        } 
    response = requests.post(url, headers=headers, json=data,timeout=5)
    data = json.loads(response.content)
    return data

def convert_to_time(value):
    if len(str(value)) == 6:  # If the value is 6 digits, convert to minutes
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

def seconds_to_minutes(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def prep_paste_img(img_filename,size):
    image_to_paste = Image.open(get_path(img_filename))
    resized_image = image_to_paste.resize(size)
    return resized_image

weapon_id = {
    "1":"NameIcon_Hammer.png",
    "2":"NameIcon_Axe.png",
    "3":"NameIcon_cb.png",
    "4":"NameIcon_Blade.png",
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

def getImage_group_leaderboard(leaderboard_data):
    Title_font = ImageFont.truetype(get_path(fonts["title_font"]), size=106)
    item_font = ImageFont.truetype(get_path(fonts["items_font"]), size=40)
    
    img = Image.new('RGB', (1600, 1100), color='#313338')
    draw = ImageDraw.Draw(img)

    draw.text((300, 30), f"Trials Champions Group", fill="white", font=Title_font)

    behemoth_icon = prep_paste_img("ico_gnasher_ragetail_512x512.png",(280,280))
    img.paste(behemoth_icon, (0, -40), mask=behemoth_icon.split()[3])
    x, y = 100, 200

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

        # Draw guild_name
        draw.text((x-60, y+60), f"{i+1}", fill=fill, font=item_font)
        
        entry_x = x
        entry_y = y
        for i,entry in enumerate(trials_Group['entries']):
            weapon_icon = f"{weapon_id[str(entry['weapon'])]}"
            role_icon = f"{role_id[str(entry['player_role_id'])]}"
            player_name = f"{entry['platform_name']}"

            icon_size = (75,75)
            weapon_icon = prep_paste_img(weapon_icon,icon_size)
            img.paste(weapon_icon, (entry_x, entry_y+5), mask=weapon_icon.split()[3])

            role_icon = prep_paste_img(role_icon,icon_size)
            img.paste(role_icon, (entry_x+50+20, entry_y+5), mask=role_icon.split()[3])

            draw.text((entry_x+150, entry_y+25),player_name, fill=fill, font=item_font)
            entry_x += 520
            if i == 1:
                entry_x = x
                entry_y += 65

        # Draw remaining_time
        remaining_time = convert_to_time(trials_Group['completion_time'])
        draw.text((1270, y+55), f"{remaining_time}", fill=fill, font=item_font)

        y += 170
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    return img_bytes_io
    # img.save("tlb.png", format='PNG')

def getImage_solo_leaderboard(leaderboard_data):
    Title_font = ImageFont.truetype(get_path(fonts["title_font"]), size=70)
    item_font = ImageFont.truetype(get_path(fonts["items_font"]), size=30)
    # Open the provided background image
    img = Image.new('RGB', (1024, 700), color='#313338')
    draw = ImageDraw.Draw(img)

    draw.text((220, 50), f"Trials Champions Solo", fill="white", font=Title_font)

    behemoth_icon = prep_paste_img("ico_gnasher_ragetail_512x512.png",(250,250))
    img.paste(behemoth_icon, (-20, -30), mask=behemoth_icon.split()[3])

    x, y = 70, 180

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

        weapon_icon = f"{weapon_id[str(entry['weapon'])]}"
        role_icon = f"{role_id[str(entry['player_role_id'])]}"
        platform_icon = f"{platform[str(entry['platform'])]}"
        player_name = f"{entry['platform_name']}"
        completion_time = entry['completion_time']

        draw.text((x-30, y+28), f"{i+1}", fill=fill, font=item_font)
        
        weapon_icon = prep_paste_img(weapon_icon,(70,70))
        img.paste(weapon_icon, (x, y+5), mask=weapon_icon.split()[3])

        role_icon = prep_paste_img(role_icon,(70,70))
        img.paste(role_icon, (x+50+20, y+5), mask=role_icon.split()[3])

        draw.text((x+150, y+28), player_name, fill=fill,font=item_font)
        width,_ = get_text_dimensions(player_name,item_font)
        
        platform_icon = prep_paste_img(platform_icon,(50,50))
        img.paste(platform_icon, (x+160+width, y+20), mask=platform_icon.split()[3])

        # Draw remaining_time
        completion_time = convert_to_time(completion_time)
        draw.text((800, y+28), f"{completion_time}", fill=fill, font=item_font)

        y += 100

    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    return img_bytes_io
    # img.save('lb.png', format='PNG')

def getImage_Trials_leaderboard(week):
    try:
        trials_leaderboard = get_trials_leaderboard(week)
        group_leaderboard_data = trials_leaderboard["payload"]["world"]["group"]["entries"][:5]
        solo_leaderboard_data = trials_leaderboard["payload"]["world"]["solo"]["all"]["entries"][:5]
        # Check if the request was successful (status code 200)
        if trials_leaderboard:
            solo_leaderboard_img = getImage_solo_leaderboard(solo_leaderboard_data)
            group_leaderboard_img = getImage_group_leaderboard(group_leaderboard_data)
            return solo_leaderboard_img,group_leaderboard_img
            
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# display_trialsgrpleaderboard(58)