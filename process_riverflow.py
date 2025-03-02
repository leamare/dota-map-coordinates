import json
import math

#targetname goes to target

map_paths = []
with open('data/dota_pvp_prefab.vmap.txt', 'r') as f:
    dump_on_next_brace = False
    found_cmap_path = False
    found_node = False
    can_be_saved = False

    last_map_path = []
    origin = []
    radius_scale = ''
    angles = []

    for line in f.readlines():
        if '"CMapPath"' in line:
            found_cmap_path = True
        if '"CMapPathNode"' in line and found_cmap_path:
            found_node = True
        # if found_node:
            # print(line)
        if ('"origin"' in line) and found_node:
            origin = [x.replace('"', '') for x in line.strip('\n').split(" ")[-3:]]
            dump_on_next_brace = True
        if '"radius_scale"' in line and found_node:
            radius_scale = [x.replace('"', '') for x in line.strip('\n').split(" ")[-1:]]
        if '"angles"' in line and found_node:
            angles = [x.replace('"', '') for x in line.strip('\n').split(" ")[-3:]]
            dump_on_next_brace = True
        if '}' in line and dump_on_next_brace and found_node:
            dump_on_next_brace = False
            last_map_path.append({
                'origin': origin,
                'radius_scale': radius_scale,
                'angles': angles
            })
            found_node = False
        if '"dota_movespeed_modifier_path"' in line:
            can_be_saved = True
            dump_on_next_brace = True
        if '}' in line and dump_on_next_brace and found_cmap_path:
            dump_on_next_brace = False
            found_cmap_path = False
            if can_be_saved:
                map_paths.append(last_map_path)
            last_map_path = []

geo_json = {
    'type': 'FeatureCollection',
    'features': []
}

for path_index, path in enumerate(map_paths):
    coordinates = []
    for node in path:
        coordinates.append([float(node['origin'][0]), float(node['origin'][1])])
    
    polygon = []
    polygon_left = []
    polygon_right = []
        
    for i in range(len(coordinates)-1):
        p1 = coordinates[i]
        p2 = coordinates[i+1]
        
        dx = p2[0] - p1[0] 
        dy = p2[1] - p1[1]
        
        # Calculate perpendicular vector
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            continue
            
        # Normalize and scale by radius
        radius = float(path[i]['radius_scale'][0])
        perpx = (-dy/length) * radius
        perpy = (dx/length) * radius
        
        if i == 0:
            polygon_left.append([p1[0] + perpx, p1[1] + perpy])
            polygon_right.append([p1[0] - perpx, p1[1] - perpy])
            
        polygon_left.append([p2[0] + perpx, p2[1] + perpy])
        polygon_right.append([p2[0] - perpx, p2[1] - perpy])
        
    polygon.append(polygon_left + polygon_right[::-1])

    geo_json['features'].append({
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates
        },
        'properties': {
            'name': 'dota_movespeed_modifier_path_' + str(path_index)
        }
    })

    geo_json['features'].append({
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': polygon
        },
        'properties': {
            'name': 'dota_movespeed_modifier_path_' + str(path_index) + '_polygon'
        }
    })

with open('data/riverflow.json', 'w') as f:
    f.write(json.dumps(geo_json))
