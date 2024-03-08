import requests
import io
from PIL import Image, ImageDraw, ImageFont
import json
import os

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
    response = requests.post(url, headers=headers, json=data)
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

def display_trialsgrpleaderboard(week):
    try:
        trials_leaderboard = get_trials_leaderboard(week)
        group_leaderboard = trials_leaderboard["payload"]["world"]["group"]["entries"]
        group_leaderboard = group_leaderboard[:5]
        # Check if the request was successful (status code 200)
        if trials_leaderboard:
            # Parse the JSON content of the response into a dictionary
            leaderboard = group_leaderboard

            # Open the provided background image
            img = Image.open(get_path("Board_background.png"))
            draw = ImageDraw.Draw(img)

            font_path = "GothicA1-Regular.ttf"
            font = ImageFont.truetype(get_path(font_path), 24)

            draw.text((48, 12), f"Rank", fill="white", font=font)
            draw.text((180, 12), f"platform_name", fill="white", font=font)
            # draw.text((700, 12), f"weapon", fill="white", font=font)
            draw.text((750, 12), f"completion_time", fill="white", font=font)

            # Use a truetype font file (replace 'arial.ttf' with the path to your font file)

            font = ImageFont.truetype(get_path(font_path), 30)
            x, y = 150, 72

            # Define custom coordinates for each piece of information
            for i, trials_Group in enumerate(leaderboard):
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
                
                entry_x = x
                entry_y = y
                for i,entry in enumerate(trials_Group['entries']):
                    draw.text((entry_x, entry_y), f"{entry['platform_name']}", fill=fill, font=font)
                    entry_x += 300
                    if i == 1:
                        entry_x = x
                        entry_y += 50

                # # Draw guild_nameplate
                # draw.text((x, y + 45), f"{guild_info['weapon']}", fill=fill, font=font)

                # # Draw level
                # draw.text((700, y+20), f"{guild_info['weapon']}", fill=fill, font=font)

                # Draw remaining_time
                remaining_time = convert_to_time(trials_Group['completion_time'])
                draw.text((760, y+20), f"{remaining_time}", fill=fill, font=font)

                y += 130

            # img.save("tlb.png", format='PNG')
            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)
            return img_bytes_io

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# display_trialsleaderboard()