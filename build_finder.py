from ast import mod
import os
from itertools import product
import copy
from PIL import Image, ImageDraw, ImageFont
import json
from collections import Counter
import io

def get_path(filename):
   # Get the current directory
    current_directory = os.getcwd()
    # Recursively search for the file in the current directory and its subdirectories
    for root, dirs, files in os.walk(current_directory):
        if filename in files:
            file_path = os.path.join(root, filename)
            return file_path

 
input_folder = "src/Icons"
output_path = 'build_img.png'
insight = ['Aetherborne','Aetheric Attunement','Aetheric Evasion','Cascade','Catalyst','Conduit','Drop','Molten','Medic',
           'Energized','Engineer','Lucent','Mender','Omnisurge','Packcaller','Reuse','Zeal']

brutality = ['Aetherhunter','Berserker','Bladestorm','Deconstruction','Earth','KnockoutKing','Overpower','Pacifier','PactHunter',
             'Rage','Ragehunter','Reduce','Sharpened','Stop','Tenacious','WeightedStrikes']

alacrity = ['Adrenaline', 'Agility', "Assassin's Frenzy", 'Conditioning', 'Endurance',
            'Evasion', 'EvasiveFury', 'FleetFooted', 'Grace', 'Inertia',
            'Invigorated', 'Nimble', 'PackWalker', 'Roll', 'Sprinter', 'Swift']

finese = ['Acidic', 'Barbed', 'Cunning', 'Fire', 'Galvanized',
          'Impulse', 'Merciless', 'Predator', 'Pulse', 'Recycle',
          'Relentless', 'Rushdown', 'Savagery', 'Tactician']

fortitude = ['Aegis', 'AssassinsVigour', 'Bloodless', 'Conservation', 'Fireproof',
             'Fortress', 'Guardian', 'Insulated', 'NineLives', 'Parasitic',
             'ShellshockResist', 'Strategist', 'StunningVigour', 'Sturdy', 'Tough',
             'Vampiric', 'Warmth', 'Water']

Builds = ["Assassin's Frenzy",'FleetFooted',"Invigorated",'Fire','Savagery',
          'Tactician','Tough','Energized','Engineer','Aetherhunter',
          'Bladestorm','WeightedStrikes','Guardian','Acidic','Aegis',]

prismatic = insight + brutality + alacrity + finese + fortitude

def load_json(file_name):
    # Get the current directory
    current_directory = os.getcwd()
    # Recursively search for the file in the current directory and its subdirectories
    for root, dirs, files in os.walk(current_directory):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Load and return the JSON data
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
    # If the file is not found, return None or handle the error as needed
    return None

def list_gen(perk_list):
  new_list = []
  for i in perk_list:
    if perk_list.count(i) ==2:
      if f"+6 {i}" not in new_list:
        new_list.append(f"+6 {i}")
    elif perk_list.count(i) == 1:
      if f"+3 {i}" not in new_list:
        new_list.append(f"+3 {i}")
  return new_list

def categorize_cells(cells):
    categories = {
        'Insight': insight,
        'Brutality': brutality,
        'Alacrity': alacrity,
        'Finesse': finese,
        'Fortitude': fortitude,
        'Prismatic' : prismatic
    }

    slot_names = []

    for cell in cells:
        for slot_name, slot_cells in categories.items():
            if cell in slot_cells:
                slot_names.append(slot_name)
                break  # Exit the inner loop once a match is found

    return slot_names

def generate_item_combinations(wp, hd, torso, arm, leg):
    item_lists = [wp, hd, torso, arm, leg]
    combinations = list(product(*item_lists))

    perk_summary = []

    for combination in combinations:
        combined_cells = []
        combined_perks = []

        for item in combination:
            combined_cells.extend(item['cells'])
            combined_perks.extend(item['perks'])

        perk_summary.append({'cells': combined_cells, 'perks': combined_perks})

    return combinations, perk_summary

def load_combinations_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data

def translate_to_english(perks_list,language,to_language= "english"):
  data = load_json('Text_data.json')
  # Create a dictionary to map Spanish to English for each category
  translation_dict = {"Cells_1": {language: to_language},"Cells_2": {language: to_language}}
  # Translate each item in the perks_list
  translated_list = [data[category][translation_dict[category][language]][data[category][language].index(item)] for 
                     item in perks_list for category in translation_dict if item in data[category][language]]
  return translated_list

def custom_sort(item):
    # Split the item into two parts: the numeric part and the rest of the string
    parts = item.split(' ', 1)
    
    # Extract the numeric part
    num_part = parts[0]
    
    # Extract the non-numeric part
    non_num_part = parts[1]
    
    # Assign higher priority to +6, then +3, and sort alphabetically within each group
    if num_part == '+6':
        return (0, non_num_part)
    elif num_part == '+3':
        return (1, non_num_part)
    else:
        # For other cases, return a high priority so that they come after +3 items
        return (2, non_num_part)
    
def img_generator(build_icon_names, Perks_list, Build, counter, mod_img=None, wspecial_img=None, consumable_images=None):
    perk_counts = Counter(Perks_list)
    render_perks = sorted([f"+6 {perk}" if count == 2 and f"+6 {perk}" not in Perks_list else f"+3 {perk}" for perk, count in perk_counts.items()], key=lambda x: len(x))
    render_perks = sorted(render_perks, key=custom_sort)
    image_files = {"Omnicell": build_icon_names[counter][0], "Armors": build_icon_names[counter][1:7]}
    total_width, max_height = 828, 286
    Rep = True if wspecial_img and len(wspecial_img) == 2 else False
    combined_image = Image.new('RGBA', (total_width, max_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(combined_image)

    def paste_image(img, x, y):
        combined_image.paste(img.convert("RGBA"), (x, y))

    def render_images(image_list, x_offset, y_offset):
        for img in image_list:
            paste_image(img, x_offset, y_offset)
            x_offset += img.width + 10
        return x_offset

    def render_text(text, x, y, font, fill=(255, 255, 255, 255)):
        draw.text((x + 5, y), text, font=font, fill=fill)
        bbox = draw.textbbox((x, y), text, font=font)
        return x + (bbox[2] - bbox[0]) + 20

    x_offset = render_images([Image.open(os.path.join(input_folder, image_files["Omnicell"]))], 202 if mod_img or wspecial_img else (total_width//2) - 64, 0)
    x_offset = render_images([Image.open(os.path.join(input_folder, img)) for img in image_files['Armors']], 10, 138)

    temp = None  
    if wspecial_img and not Rep:
        paste_image(Image.open(os.path.join(input_folder, wspecial_img)), 350, 0)
    elif wspecial_img and len(wspecial_img) == 2:
        paste_image(Image.open(os.path.join(input_folder, wspecial_img[0])), 350, 0)
        paste_image(Image.open(os.path.join(input_folder, wspecial_img[1])), 498, 0)

    if mod_img and not Rep:
        paste_image(Image.open(os.path.join(input_folder, mod_img)), 498, 0)
    elif mod_img and len(wspecial_img) == 2:
        paste_image(Image.open(os.path.join(input_folder, mod_img)), 646, 0)

    font_size, font = 20, ImageFont.truetype(get_path("Roboto-Bold.ttf"), 20)
    x_off, y_off, x_off1, y_off1 = 10, (128 * 2) + 20, 10, (128 * 2) + 30

    for i in render_perks:
        if x_off > 650:
            temp = combined_image.copy()  # Assign combined_image to temp
            combined_image = Image.new('RGBA', (total_width, max_height + 60), (0, 0, 0, 0))
            combined_image.paste(temp)
            draw = ImageDraw.Draw(combined_image)
            x_off1 = render_text(i, x_off1, y_off1+20, font)
            x_off += x_off1 - 10
        else:
            x_off = render_text(i, x_off, y_off, font)
    
    if consumable_images:
        temp = combined_image.copy()  # Assign combined_image to temp
        combined_image = Image.new('RGBA', (total_width, max_height + 188), (0, 0, 0, 0))
        combined_image.paste(temp)
        render_images([Image.open(os.path.join(input_folder, img)) for img in consumable_images], 202, 336)

    img_bytes_io = io.BytesIO()
    combined_image.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    return img_bytes_io

def Build_finder(Perks_list,language,weapon_type,weapon_filter,lantern,omnicell,counter):
  weapons= load_json('weapons.json')
  armors = load_json('armors.json')
  total_combination = 0
  Build = []
  Perks_list = translate_to_english(Perks_list,language)
  Cells_list = categorize_cells(Perks_list)


  wp = [weapon for weapon in weapons 
    if (all(item in Cells_list for item in weapon['cells']) and any(item in Perks_list for item in weapon['perks']))
    or (any(item in Perks_list for item in weapon['perks']) and weapon['cells']==['Prismatic', 'Prismatic'])]
  hd = [head for head in armors if head['type'] == 'Head' and all(item in Cells_list for item in head['cells']) and 
        any(item in Perks_list for item in head['perks'])]
  tors = [torso for torso in armors if torso['type'] == 'Torso' and all(item in Cells_list for item in torso['cells']) 
          and any(item in Perks_list for item in torso['perks'])]
  arm = [arms for arms in armors if arms['type'] == 'Arms' and all(item in Cells_list for item in arms['cells']) 
         and any(item in Perks_list for item in arms['perks'])]
  leg = [leg for leg in armors if leg['type'] == 'Legs' and all(item in Cells_list for item in leg['cells']) 
         and any(item in Perks_list for item in leg['perks'])]

  combinations, perk_summary = generate_item_combinations(wp, hd, tors, arm, leg)

  for i in range(len(combinations)):
      if combinations[i][0]['type'] == weapon_type and combinations[i][0]['behemoth'] == weapon_filter:
          perks_armor = perk_summary[i]['perks']
          req_perk = copy.copy(Perks_list)  # Create a copy of Perks_list
          cells_armor = perk_summary[i]['cells']

          for a in perks_armor:
              if a in req_perk:
                  req_perk.remove(a)
          remain_cells = categorize_cells(req_perk)
          perk_summary[i]['cells'].append('Insight')
          for a in cells_armor:
              if a in remain_cells:
                  remain_cells.remove(a)
          nm = []
          if len(remain_cells) == 2 and cells_armor.count('Prismatic') == 2 or remain_cells == []:
              for j in combinations[i]:
                 nm.append(j['name'])
                 nm.append(j['behemoth'])
              Build.append(nm)
              total_combination += 1
          req_perk = copy.copy(Perks_list)  # Reset to the original state

  build_icon_names = []
  for i in Build:
      temp = []
      temp.insert(0, f"{omnicell}.png")
      temp.append(i[0].replace(' ', '').replace("'", '') + '.png')
      temp.append(i[2].replace(' ', '').replace("'", '')+ '.png')
      temp.append(i[4].replace(' ', '').replace("'", '')+ '.png')
      temp.append(i[6].replace(' ', '').replace("'", '')+ '.png')
      temp.append(i[8].replace(' ', '').replace("'", '')+ '.png')
      temp.insert(7,f"{lantern}.png".replace(' ', '').replace("'", '') )
      build_icon_names.append(temp)
      temp = []
  if build_icon_names == []:
    return build_icon_names

  return build_icon_names,Build,total_combination