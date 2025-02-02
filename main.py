from enum import Enum, auto
from typing import *
from pyray import *
import os
import json
import math
import random
import user_interface
RESOLUTION_X = 1450
RESOLUTION_Y = 800
SETTINGS = {
    "UFOV": {
        "CenterObjects": 2,
        "PeripheralObjects": 1,
        "IntermissionTime": 5,
        "RadiusOfView": 300,
    },
    "TimerDuration": 2.0,
}
PATHS = {
    "Pentominoes": ["pento_f.png", "pento_p.png", "pento_t.png", "pento_u.png", "pento_v.png", "pento_w.png", "pento_x.png", "pento_z.png"],
    "Polygons": ["diamond.png", "hemicircle.png", "hexagon.png", "octagon.png", "pentagon.png", "square.png", "star.png", "triangle.png"],
    "Faces": ["face_01.png", "face_02.png", "face_03.png", "face_04.png", "face_05.png", "face_06.png", "face_07.png", "face_08.png", "face_09.png", "face_10.png", "face_11.png", "face_12.png", "face_13.png", "face_14.png", "face_15.png", "face_16.png", "face_17.png", "face_18.png", "face_19.png", "face_20.png", "face_21.png", "face_22.png", "face_23.png", "face_24.png", "face_25.png", "face_26.png"],
}
TEXTURES = {
    "Pentominoes": {},
    "Polygons": {},
    "Faces": {},
}
init_window(RESOLUTION_X, RESOLUTION_Y, "Perceptia")
set_target_fps(get_monitor_refresh_rate(get_current_monitor()))
images_to_unload = []
for path_link, image_paths in PATHS.items():
    for image_path in image_paths:
        image_to_load = load_image(path_link + "/" + image_path)
        TEXTURES[path_link][image_path] = load_texture_from_image(image_to_load)
        images_to_unload.append(image_to_load)
COMBINED_TEXTURES = TEXTURES["Pentominoes"] | TEXTURES["Polygons"] | TEXTURES["Faces"]
for image_object in images_to_unload:
    unload_image(image_object)
settings_image = load_image("settings.jpeg")
settings_texture = load_texture_from_image(settings_image)
unload_image(settings_image)
if os.path.getsize("settings_data.json") == 0:
    with open("settings_data.json", "w") as settings_file:
        settings_file.write(json.dumps(SETTINGS, indent=4))
with open("settings_data.json", "r") as file:
    settings_data = json.load(file)
is_generating = False
is_playing = False
is_intermission = False
is_settings = False
settings_buttons = {}
settings_buttons["center_objects"] = user_interface.InputButton("Center Objects:", 25, Rectangle(50 + measure_text("Center Objects:", 25) + 10, 75, measure_text("0", 25), 25))
settings_buttons["center_objects"].text = str(settings_data["UFOV"]["CenterObjects"])
settings_buttons["peripheral_objects"] = user_interface.InputButton("Peripheral Objects:", 25, Rectangle(50 + measure_text("Peripheral Objects:", 25) + 10, 125, measure_text("0", 25), 25))
settings_buttons["peripheral_objects"].text = str(settings_data["UFOV"]["PeripheralObjects"])
settings_buttons["radius_of_view"] = user_interface.InputButton("Radius Of View:", 25, Rectangle(50 + measure_text("Radius Of View:", 25) + 10, 175, measure_text("000", 25), 25))
settings_buttons["radius_of_view"].text = str(settings_data["UFOV"]["RadiusOfView"])

settings_buttons["intermission_time"] = user_interface.InputButton("Intermission Time:", 25, Rectangle(50 + measure_text("Intermission Time:", 25) + 10, 225, measure_text("00", 25), 25))
settings_buttons["intermission_time"].text = str(settings_data["UFOV"]["IntermissionTime"])
settings_buttons["timer_duration"] = user_interface.InputButton("Timer Duration:", 25, Rectangle(50 + measure_text("Timer Duration:", 25) + 10, 275, measure_text("000", 25), 25))
settings_buttons["timer_duration"].text = str(settings_data["TimerDuration"])
center_textures_to_load = {
    "Pentominoes": [],
    "Polygons": [],
    "Faces": [],
}
peripheral_textures_to_load = {
    "Pentominoes": [],
    "Polygons": [],
    "Faces": []
}
center_match = []
center_match_color = WHITE
center_trial_textures = []
peripheral_match = []
peripheral_match_color = WHITE
peripheral_trial_textures = []
peripheral_positions = []
available_center_keys = []
available_peripheral_keys = []
trial_clock = 0
current_trial = 1
def reset_game():
    global is_playing
    global center_textures_to_load
    global peripheral_textures_to_load
    global center_match
    global peripheral_match
    global center_trial_textures
    global peripheral_trial_textures
    global peripheral_positions
    global available_center_keys
    global available_peripheral_keys
    global current_trial
    is_playing = False
    center_textures_to_load = {
        "Pentominoes": [],
        "Polygons": [],
        "Faces": [],
    }
    peripheral_textures_to_load = {
        "Pentominoes": [],
        "Polygons": [],
        "Faces": [],
    }
    center_trial_textures = []
    peripheral_trial_textures = []
    peripheral_positions = []
    center_match = []
    peripheral_match = []
    available_center_keys = []
    available_peripheral_keys = []
    current_trial = 1
trials = 20
intermission_clock = 0.0
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    if is_generating:
        is_generating = False
        is_intermission = True
        intermission_clock = get_time()
        center_key_copies = [
            ("Pentominoes", list(TEXTURES["Pentominoes"].keys())),
            ("Polygons", list(TEXTURES["Polygons"].keys())), 
            ("Faces", list(TEXTURES["Faces"].keys())), 
        ]
        peripheral_key_copies = [
            ("Pentominoes", list(TEXTURES["Pentominoes"].keys())),
            ("Polygons", list(TEXTURES["Polygons"].keys())), 
            ("Faces", list(TEXTURES["Faces"].keys())), 
        ]
        order = list(range(3))
        random.shuffle(order)
        for i in range(settings_data["UFOV"]["CenterObjects"]):
            index = order[i % len(center_key_copies)]
            to_remove = random.choice(center_key_copies[index][1])
            center_textures_to_load[center_key_copies[index][0]].append(to_remove)
            center_key_copies[index][1].remove(to_remove)
        order = list(range(3))
        random.shuffle(order)
        for i in range(settings_data["UFOV"]["PeripheralObjects"]):
            index = order[i % len(peripheral_key_copies)]
            to_remove = random.choice(peripheral_key_copies[index][1])
            peripheral_textures_to_load[peripheral_key_copies[index][0]].append(to_remove)
            peripheral_key_copies[index][1].remove(to_remove)
        for x in center_key_copies:
            if len(center_textures_to_load[x[0]]) != 0:
                available_center_keys.append(x[0])
        for x in peripheral_key_copies:
            if len(peripheral_textures_to_load[x[0]]) != 0:
                available_peripheral_keys.append(x[0])
        for i in range(trials):
            if random.random() < 0.33:
                center_trial_textures.append(random.choice(center_textures_to_load[random.choice(available_center_keys)]))
                center_match.append(True)
            else:
                chosen_one = random.choice(center_key_copies)
                center_trial_textures.append(random.choice(chosen_one[1]))
                center_match.append(False)
            theta = random.random() * (2 * math.pi)
            match_flag = False
            for j in range(2):
                if random.random() < 0.166:
                    match_flag = True
                    peripheral_trial_textures.append(random.choice(peripheral_textures_to_load[random.choice(available_peripheral_keys)]))
                    peripheral_match.append(True)
                else:
                    chosen_one = random.choice(peripheral_key_copies)
                    peripheral_trial_textures.append(random.choice(chosen_one[1]))
                    if not match_flag and j == 1:
                        peripheral_match.append(False)
                theta += (j * (random.uniform(math.pi / 2, (3 * math.pi) / 2)))
                peripheral_positions.append((int(math.cos(theta) * settings_data["UFOV"]["RadiusOfView"]), int(math.sin(theta) * settings_data["UFOV"]["RadiusOfView"])))
    else:
        if is_intermission:
            draw_text("Center Images:", 50, int(RESOLUTION_Y / 2) - 12, 25, WHITE)
            draw_text("Peripheral Images:", 50, int(RESOLUTION_Y / 2) + 137, 25, WHITE)
            current_i = 0
            for category, images in center_textures_to_load.items():
                if category in available_center_keys:
                    for image_key in images:
                        draw_texture(COMBINED_TEXTURES[image_key], 50 + measure_text("Center Images:", 25) + ((current_i + 1) * 150), int(RESOLUTION_Y / 2) - 12, WHITE)
                        current_i += 1
            current_i = 0
            for category, images in peripheral_textures_to_load.items():
                if category in available_peripheral_keys:
                    for image_key in images:
                        draw_texture(COMBINED_TEXTURES[image_key], 50 + measure_text("Center Images:", 25) + ((current_i + 1) * 150), int(RESOLUTION_Y / 2) + 137, WHITE)
                        current_i += 1
            if get_time() - intermission_clock > settings_data["UFOV"]["IntermissionTime"]:
                is_intermission = False
                trial_clock = get_time() + settings_data["TimerDuration"]
        elif is_playing:
            draw_texture(COMBINED_TEXTURES[center_trial_textures[current_trial - 1]], int(RESOLUTION_X / 2) - 50, int(RESOLUTION_Y / 2) - 50, WHITE)
            draw_texture(COMBINED_TEXTURES[peripheral_trial_textures[(current_trial - 1) * 2]], int(RESOLUTION_X / 2) + peripheral_positions[(current_trial - 1) * 2][0], int(RESOLUTION_Y / 2) - peripheral_positions[(current_trial - 1) * 2][1], WHITE)
            draw_texture(COMBINED_TEXTURES[peripheral_trial_textures[((current_trial - 1) * 2) + 1]], int(RESOLUTION_X / 2) + peripheral_positions[((current_trial - 1) * 2) + 1][0], int(RESOLUTION_Y / 2) - peripheral_positions[((current_trial - 1) * 2) + 1][1], WHITE)
            draw_text("[A] Match Center", 50, int(RESOLUTION_Y / 2) - 12, 25, center_match_color)
            draw_text("[L] Match Peripheral", 50, int(RESOLUTION_Y / 2) + 37, 25, peripheral_match_color)
            if is_key_pressed(KeyboardKey.KEY_A):
                if center_match[current_trial - 1]:
                    center_match_color = GREEN
                else:
                    center_match_color = RED
            elif is_key_pressed(KeyboardKey.KEY_L):
                if peripheral_match[current_trial - 1]:
                    peripheral_match_color = GREEN
                else:
                    peripheral_match_color = RED                    
            if get_time() > trial_clock:
                trial_clock += settings_data["TimerDuration"]
                current_trial += 1
                center_match_color = WHITE
                peripheral_match_color = WHITE
                if current_trial == trials:
                    reset_game()
        else:
            if is_settings:
                draw_texture(settings_texture, 0, 0, GRAY)
            else:
                draw_text("[Space] Start/Stop", int(RESOLUTION_X / 2) - int(measure_text("[Space] Start/Stop", 50) / 2), int(0.85 * RESOLUTION_Y), 50, WHITE)
                draw_text("[S] Settings", 50, 30, 25, WHITE)
            if is_key_pressed(KeyboardKey.KEY_S):
                is_settings = not is_settings
                for settings_object in settings_buttons.values():
                    settings_object.toggle()
                if not is_settings:
                    settings_data["UFOV"]["CenterObjects"] = max(int(settings_buttons["center_objects"].text), 1)
                    settings_data["UFOV"]["PeripheralObjects"] = max(int(settings_buttons["peripheral_objects"].text), 1)
                    settings_data["UFOV"]["RadiusOfView"] = min(int(settings_buttons["radius_of_view"].text), 300)
                    settings_data["UFOV"]["IntermissionTime"] = max(int(settings_buttons["intermission_time"].text), 1)
                    settings_data["TimerDuration"] = max(float(settings_buttons["timer_duration"].text), 0.25)
                    with open("settings_data.json", "w") as file:
                        json.dump(settings_data, file)
        if not is_intermission and is_key_pressed(KeyboardKey.KEY_SPACE):
            if not is_playing:
                is_generating = True
                reset_game()
            is_playing = not is_playing
    for settings_object in settings_buttons.values():
        settings_object.update()
    end_drawing()
close_window()