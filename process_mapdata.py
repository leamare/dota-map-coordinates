import json
import matplotlib.path as mplPath
import numpy as np

true_sight = {
    'npc_dota_fort': 900,
    'npc_dota_tower': 700,
    'ent_dota_fountain': 1200
}

with open('data/mapdata.json', 'r') as f:
    neutrals = []
    landmark_auras = []
    data = json.loads(f.read())['data']
    if (data.get('trigger_multiple')):
        for k in data['trigger_multiple']:
            if ('neutralcamp' in k['name']):
                neutrals.append(k)
            else:
                landmark_auras.append(k)
        data['trigger_multiple'] = neutrals
        data['landmark_aura'] = landmark_auras
    ##        print k['name']

    neutral_data = {}
    with open('data/dota_pvp_prefab.vmap.txt', 'r') as f:
        dump_on_next_brace = False
        for line in f.readlines():
            if 'VolumeName' in line:
                VolumeName = line.strip('\n').split(" ")[-1].replace('"', '')
            if 'PullType' in line:
                PullType = line.strip('\n').split(" ")[-1].replace('"', '')
            if 'NeutralType' in line:
                NeutralType = line.strip('\n').split(" ")[-1].replace('"', '')
            if 'npc_dota_neutral_spawner' in line:
                dump_on_next_brace = True
            if '}' in line and dump_on_next_brace:
                dump_on_next_brace = False
                neutral_data[VolumeName] = {
                    'PullType': PullType,
                    'NeutralType': NeutralType
                }

    landmarks = []
    with open('data/dota_custom_default_000.vmap.txt', 'r') as f:
        dump_on_next_brace = False
        ent_type_found = False

        for line in f.readlines():
            if '"CMapEntity"' in line:
                origin = [0,0]
            if '"origin"' in line:
                origin = [x.replace('"', '') for x in line.strip('\n').split(" ")[-3:]]
            if '"model"' in line:
                ent_type_found = True

                if 'dark_statue_base' in line:
                    classname = 'statue'
                elif 'old_well' in line:
                    classname = 'well'
                elif 'cathedral' in line:
                    classname = 'mines'
                elif 'ancient_giant_skeleton' in line:
                    classname = 'graveyard'
                else:
                    ent_type_found = False

            if ent_type_found and origin[0] and origin[1]:
                dump_on_next_brace = True
            if '}' in line and dump_on_next_brace:
                dump_on_next_brace = False
                landmarks.append({
                    'x': round(float(origin[0]), 2), 
                    'y': round(float(origin[1]), 2),
                    'name': classname
                })
                origin = [0,0]
                ent_type_found = False
    data['landmarks'] = landmarks

    with open('data/dota_pvp_prefab.vmap.txt', 'r') as f:
        dump_on_next_brace = False
        ent_type_found = False
        class_infoplayer = False

        for line in f.readlines():
            if 'CMapEntity' in line:
                ent_type_found = False
                class_infoplayer = False
                origin = [0,0]
            if 'info_player_start_dota' in line:
                class_infoplayer = True
            if 'roshan_location_2' in line and class_infoplayer:
                ent_type_found = True
            if '"origin"' in line:
                origin = [x.replace('"', '') for x in line.strip('\n').split(" ")[-3:]]
            if ent_type_found and origin[0] and origin[1]:
                dump_on_next_brace = True
            if '}' in line and dump_on_next_brace:
                data['npc_dota_roshan_spawner'].append({
                    'x': int(origin[0]),
                    'y': int(origin[1]),
                    'bounds': [
                        int(origin[0]),
                        int(origin[1])
                    ],
                    'team': 0
                })
                break

    for pt in data['npc_dota_neutral_spawner']:
        point = [pt['x'], pt['y']]
        if (data.get('trigger_multiple')):
            for trigger in data['trigger_multiple']:
                if ('neutralcamp' not in trigger['name']):
                    continue
                points = []
                for i in range(1, 5):
                    points.append([trigger[str(i)]['x'], trigger[str(i)]['y']])
                bbPath = mplPath.Path(np.array(points))
                if bbPath.contains_point(point):
                    pt['triggerName'] = trigger['name']
                    pt['pullType'] = neutral_data[trigger['name']]['PullType']
                    pt['neutralType'] = neutral_data[trigger['name']]['NeutralType']
                    break
        
    meta = {}
    coorddata = {}
    for key in data:
        print (key)
        if key == 'trigger_multiple' or key == 'landmark_aura':
            coorddata[key] = []
            for obj in data[key]:
                entity = {
                    'points': [],
                    'name': obj['name']
                }
                for i in range(1, 5):
                    entity['points'].append(obj[str(i)])
                coorddata[key].append(entity)
        elif key == 'landmarks':
            coorddata[key] = data[key]
            continue
        else:
            coorddata[key] = []
            for obj in data[key]:
                new_obj = {}
                coords = {}
                if type(obj) is str:
                    continue
                for k in obj:
                    if k == 'team' or k == 'name' or k == 'z':
                        continue
                    elif k != 'x' and k != 'y' and k != 'pullType' and k != 'neutralType' and k != 'triggerName':
                        if obj[k] == 0:
                            continue
                        elif k == 'bat':
                            obj[k] = round(obj[k], 2)
                        new_obj[k] = obj[k]
                    else:
                        coords[k] = obj[k]
                
                # if key == 'ent_dota_tree':
                #     # workaround for 7.33, whatever problem it had
                #     coords['x'] -= 32
                #     coords['y'] -= 32

                if 'spawner' in key:
                    new_obj = {
                        'bounds': [ 0, 0 ]
                    }

                if key == 'npc_dota_tower' or key == 'npc_dota_barracks':
                    subkey = obj['name'].split('_')[2]
                    coords['subType'] = subkey
                    meta[key + '_' + subkey] = new_obj
                    if key == 'npc_dota_tower':
                        meta[key + '_' + subkey]['trueSight'] = true_sight[key]
                else:
                    meta[key] = new_obj
                    if key == 'npc_dota_fort' or key == 'ent_dota_fountain':
                        meta[key]['trueSight'] = true_sight[key]

                coorddata[key].append(coords)
    result = {
        'data': coorddata,
        'stats': meta
    }
    with open('mapdata.json', 'w') as g:
        g.write(json.dumps(result))
