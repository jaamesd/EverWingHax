#! /usr/bin/env python3
import urllib.request
import urllib.parse
import codecs
import json
import math
import pprint

debug = False

def main():
    print("""\



       ____|             \ \        /_)               |   |
       __|\ \   / _ \  __|\ \  \   /  | __ \   _` |   |   |  _` |\ \  /
       |   \ \ /  __/ |    \ \  \ /   | |   | (   |   ___ | (   | `  <
      _____|\_/ \___|_|     \_/\_/   _|_|  _|\__, |  _|  _|\__,_| _/\_\\
                                             |___/
                                                      by andromeduck
INSTRUCTIONS

  1. Open Google Chrome (desktop)
  2. In Chrome, open a messenger. Do not start the game yet.
  3. In Chrome, Open Devloper Tools via Menu > More Tools > Developer Tools.
  4. In Chrome Developer Tools, click Network and then the Filter button in
     the top left hand corner.
  5. In Chrome Developer Tools, paste the following without quotes into the
     Filter box on the upper left: \"stormcloud-146919.appspot.com/auth/\"
  6. In Chrome Developer Tools, right click the new entry under Name and select
     Copy > Copy Link Address. It begins with \"?uid=\" followed by numbers.
  7. Paste it in the prompt below.
    """)

    # For testing:
    # profile_url = "http://stormcloud-146919.appspot.com/auth/connect/?uid=1141161145996839&"

    global profile_url
    profile_url = input("Profile URL:\n")

    global query_endpoint
    query_endpoint = "http://stormcloud-146919.appspot.com/purchase/listing/?"

    print("\n\nSTARTING HAX\n")

    global world
    # need to explicity set it here for some reason
    world = update_world()
    
    aquire_characters()

    acquire_sidekicks()

    exit_tutorial()

    print("\nHAX FINISHED\n")

    print("Refresh page or play another round to see results in game.")
    return 0


def aquire_characters():
    print("\nAQUIRING CHARACTERS\n")
    characters = get_item_class("character")
    for character in characters:
        character_name = character["model"].replace("character:", "")
        if not equip_character(character):
            print("WARNING: Actions on character " + character_name + " skipped due to active quest status")
            continue

        event = {"k": get_func_key("player_key")}
        event["l"] = get_func_key("listing_level_up_character")
        event["character"] = character["key"]
        levels_to_upgrade = get_stat(character, "level", "maximum") - get_stat(character, "level", "value")
        print("Leveling up character " + character_name + " " + str(levels_to_upgrade) + " times ", end="")
        for i in range(0, levels_to_upgrade):
            submit_event(event)
            if levels_to_upgrade <= 30:
                print(".", end="", flush=True)
            elif i % 2:
                print(".", end="", flush=True)
        print(" DONE")
    print("\nCHARACTERS AQUIRED\n\n")


def equip_character(character):
    character_name = character["model"].replace("character:", "")
    if "questing" in character["state"]:
        return False

    if character["state"] == "locked":
        complete_games(2)
        print("Unlocking Character " + character_name, end=" ... ")
        event = {"k": get_func_key("player_key")}
        event["l"] = get_func_key("listing_unlock_character_" + character_name)
        event["global"] = get_func_key("item_global")
        event["character"] = character["key"]
        submit_event(event)
        characters = get_item_class("character")
        character = next(character for character in characters if character["key"] == event["character"])
        print("DONE")

    if character["state"] == "idle":
        print("Equipping Character:" + character_name, end=" ... ")
        characters = get_item_class("character")
        curr_character = next(character for character in characters if character["state"] == "equipped")
        event = {"k": get_func_key("player_key")}
        event["l"] = get_func_key("listing_equip_character")
        event["equip"] = character["key"]
        if curr_character:
            event["unequip"] = curr_character["key"]
        submit_event(event)
        print("DONE")
    return True


def acquire_sidekicks():
    print("\nAQUIRING SIDEKICKS\n")
    print("Unlocking a ton of dragons")
    for i in range(0, 20):
        complete_games(100)

        aquire_eggs("common", 9)
        aquire_dragons("common", 7)
        aquire_dragons("rare", 2)

        aquire_eggs("epic", 80)
        aquire_dragons("rare", 13)
        aquire_dragons("legendary", 8)

        level_up_sidekicks()
        evolve_sidekicks()

    for i in range(0, 3):
        level_up_sidekicks()
        evolve_sidekicks(cull_extra=True)

    print("\nSIDEKICKS AQUIRED\n\n")


def aquire_eggs(rarity, num_eggs):
    print("unlocking " + str(num_eggs) + " " + rarity + " eggs ", end="")
    event = {"k": get_func_key("player_key")}
    event["l"] = get_func_key("listing_" + rarity + "_dragon_egg")
    for i in range(0, num_eggs):
        submit_event(event, update_world=False)
        if num_eggs <= 40:
            print(".", end="", flush=True)
        elif i % 2:
            print(":", end="", flush=True)
    update_world()
    print(" DONE")


def aquire_dragons(rarity, num_dragons):
    print("acquiring " + str(num_dragons) + " " + rarity + " dragons", end="")
    event = {"k": get_func_key("player_key")}
    event["l"] = get_func_key(rarity + "_dragon")
    for j in range(0, num_dragons):
        submit_event(event, update_world=False)
        print(".", end="", flush=True)
    update_world()
    print(" DONE")


def level_up_sidekicks():
    sidekicks = get_item_class("sidekick")
    print("Leveling up " + str(len(sidekicks)) + " sidekicks")
    sidekicks = [sidekick for sidekick in sidekicks if get_stat(sidekick, "xp", "value") != get_stat(sidekick, "xp", "maximum")]
    for i in range(0, math.ceil(len(sidekicks) / 2)):
        equip_sidekicks(sidekicks[i], sidekicks[len(sidekicks) - 1 - i])
        complete_games(1)


def evolve_sidekicks(cull_extra=False):
    sidekicks = get_item_class("sidekick")
    evolution_candidates = [sidekick for sidekick in sidekicks
        if get_stat(sidekick, "xp", "value") == get_stat(sidekick, "xp", "maximum")
        and get_stat(sidekick, "maturity", "value") != get_stat(sidekick, "maturity", "maximum")]
    print("Attempting to Evolve " + str(len(evolution_candidates)) + " of " + str(len(sidekicks)) + " sidekicks")
    while (len(evolution_candidates)):
        event = {"k": get_func_key("player_key")}
        match_target = evolution_candidates[0]
        evolution_candidates.remove(match_target)

        ideal_match = next((sidekick for sidekick in evolution_candidates
            if sidekick["model"] == match_target["model"]
            and get_stat(sidekick, "maturity", "value") == get_stat(match_target, "maturity", "value")
            and get_stat(sidekick, "zodiac", "value") == get_stat(match_target, "zodiac", "value")), None)

        if ideal_match:
            evolution_candidates.remove(ideal_match)
            print("Match found, Combining")
            event["l"] = get_func_key("listing_fuse_dragon_zodiac_bonus")
            event["sidekick1"] = match_target["key"]
            event["sidekick2"] = ideal_match["key"]
        elif cull_extra:
            print("No match, Deleting")
            event["l"] = get_func_key("listing_sell_dragon")
            event["sidekick"] = match_target["key"]
        else:
            print("No match, Skipping")
            continue
        submit_event(event, update_world=False)

    if cull_extra:
        deletion_candidates =[sidekick for sidekick in sidekicks
        if get_stat(sidekick, "xp", "value") == get_stat(sidekick, "xp", "maximum")
        and get_stat(sidekick, "zodiac_bonus", "value") != get_stat(sidekick, "zodiac_bonus", "maximum")]
        num_deletion_candidates = len(deletion_candidates)
        print("Attempting to Cull " + str(num_deletion_candidates) + " of " + str(len(sidekicks)) + " subpar sidekicks")
        event = {"k": get_func_key("player_key")}
        event["l"] = get_func_key("listing_sell_dragon")
        for i in range(0, num_deletion_candidates):
            event["sidekick"] = deletion_candidates[i]["key"]
            submit_event(event, update_world=False)
            if len(num_deletion_candidates) <= 40:
                print(".", end="", flush=True)
            elif i % 2:
                print(":", end="", flush=True)


def equip_sidekicks(new_left, new_right):
    sidekicks = get_item_class("sidekick")
    curr_left = next((sidekick for sidekick in sidekicks if sidekick["state"] == "equippedLeft"), None)
    event = {"k": get_func_key("player_key")}
    if curr_left:
        event["l"] = get_func_key("listing_equip_dragon_left_swap")
        event["sidekick1"] = new_left["key"]
        event["sidekick2"] = curr_left["key"]
        if new_left["key"] != curr_left["key"]:
            submit_event(event)
    else:
        event["l"] = get_func_key("listing_equip_dragon_left")
        event["sidekick1"] = new_left["key"]
        submit_event(event)

    sidekicks = get_item_class("sidekick")
    curr_right = next((sidekick for sidekick in sidekicks if sidekick["state"] == "equippedRight"), None)
    event = {"k": get_func_key("player_key")}
    if curr_right:
        event["l"] = get_func_key("listing_equip_dragon_right_swap")
        event["sidekick1"] = new_right["key"]
        event["sidekick2"] = curr_right["key"]
        if new_right["key"] != curr_right["key"]:
            submit_event(event)
    else:
        event["l"] = get_func_key("listing_equip_dragon_right")
        event["sidekick1"] = new_right["key"]
        submit_event(event)
    print("Equipped 2 new pets")


def complete_games(num_games):
    print("Farming " + str(num_games) + " Rounds ", end="")
    sidekicks = get_item_class("sidekick")
    curr_left = next((sidekick for sidekick in sidekicks if sidekick["state"] == "equippedLeft"), None)
    curr_right = next((sidekick for sidekick in sidekicks if sidekick["state"] == "equippedRight"), None)

    event = {"k": get_func_key("player_key")}
    event["l"] = get_func_key("game_complete")
    event["global"] = get_func_key("item_global")
    event["coin"] = 99999
    event["xpPlayer"] = 99999
    if curr_left:
        event["sidekick1"] = curr_left["key"]
        event["xpSidekick1"] = 99999
    if curr_right:
        event["sidekick2"] = curr_right["key"]
        event["xpSidekick2"] = 99999

    for i in range(0, num_games):
        submit_event(event, update_world=False)
        if num_games <= 40:
            print(".", end="", flush=True)
        elif i % 2:
            print(":", end="", flush=True)
    update_world()
    print(" DONE")


def get_func_key(key_name):
    if key_name == "player_key":
        return world["player"]["key"]
    elif key_name == "item_global":
        return next(item["key"] for item in world["player"]["inventory"] if item["model"] == "item_global")
    else:
        return next(item["key"] for item in world["schema"]["listings"] if item["name"] == key_name)


def get_item_class(type_name):
    return[item for item in world["player"]["inventory"] if type_name in item["model"]]


def get_stat(item, name, field):
    return int(next(stat[field] for stat in item["stats"] if stat["name"] == name))


def update_world():
    try:
        world = json.loads(urllib.request.urlopen(profile_url).read().decode('utf-8'))
        return world
    except Exception as error:
        print("Invalid Profile URL: ", profile_url)
        print(str(error))
        exit(1)


def submit_event(query_data, update_world=True):
    try:
        query_url = query_endpoint + urllib.parse.urlencode(query_data)
        response = urllib.request.urlopen(query_url).read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(str(e))
        response = e.read().decode("utf-8")

    if "error" in response:
        print("ERROR on query: ", query_url)
        print(response["message"])
    elif update_world:
        response = json.loads(response)
        if "wallet" in response:
            world["player"]["wallet"] = response["wallet"]
        if "inventory" in response:
            world["player"]["inventory"] = response["inventory"]
    return response


def exit_tutorial():
    if (get_item_class("token:tutorialComplete")):
        return
    print("\nEXITING TUTORIAL\n")
    characters = get_item_class("character")
    curr_character = next(character for character in characters if character["state"] == "equipped")
    event = {"k": get_func_key("player_key")}
    event["l"] = get_func_key("listing_tutorial_lvl5")
    event["character"] = curr_character["key"]
    submit_event(event)
    print("\nTUTORIAL EXITED\n")


def default_inventory():
    event = {"k": get_func_key("player_key")}
    event["l"] = get_func_key("listing_default_inventory")
    submit_event(event)

if __name__ == "__main__":
    main()
