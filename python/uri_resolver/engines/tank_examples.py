import tank


# get tank instance from project path:
tk = tank.tank_from_path("/mnt/ala/jobs/s171")

# get a template instance



# find published file
layout_cam = '/mnt/ala/jobs/s171/sequences/tqn/tqn_040/lay/publish/maya/camera/tqn040.v060.abc'
tank.util.find_publish(tk, [layout_cam])




# how to find the template for a published file?

# get all published paths for template:
tk.paths_from_template(tk.templates.get('maya_shot_env_json'), {})

# constrain results by sequence code:
tk.paths_from_template(tk.templates.get('maya_shot_env_json'), {"Sequence":"tqn"})

# constrain results by shot code:
tk.paths_from_template(tk.templates.get('maya_shot_env_json'), {"Shot":"tqn_040"})

# constrain results by shot code and step code:
tk.paths_from_template(tk.templates.get('maya_shot_env_json'), {"Shot":"tqn_040", "Step": "lay"})


# template: sequences/{Sequence}/{Shot}/{Step}/publish/environment/{name}.v{version}.json

#

tank_uri = "tank://s171/sequence:tqn/shot:tqn_040/step:lay/product:environment/tqn040?version=latest"

# tank_uri = "tank://s171/sequence:tqn/shot:tqn_040/step:lay/publish/environment/tqn040.v041.json"


# how to get tokens or fields from a publshed file path?
ctx = tk.context_from_path('/mnt/ala/jobs/s171/sequences/tqn/tqn_040/lay/publish/environment/tqn040.v041.json')

'''
<Sgtk Context:   Project: {'type': 'Project', 'id': 124, 'name': 'Studio One 2017'}
  Entity: {'type': 'Shot', 'id': 1185, 'name': 'tqn_040'}
  Step: {'type': 'Step', 'id': 35, 'name': 'Layout'}
  Task: None
  User: None
  Shotgun URL: https://utsala.shotgunstudio.com/detail/Shot/1185
  Additional Entities: []>
'''

# that is not quite the same as tokens, i.e. how do we get version etc?


templ = tk.templates['maya_shot_env_json']
ctx.as_template_fields(templ)
# {'Step': 'lay', 'Shot': 'tqn_040', 'Sequence': 'tqn'}

templ_path = tk.templates['maya_shot_env_json']
print templ_path.keys
# {'Step': <Sgtk StringKey Step>, 'version': <Sgtk IntegerKey version>, 'Shot': <Sgtk StringKey Shot>, 'name': <Sgtk StringKey name>, 'Sequence': <Sgtk StringKey Sequence>}



tk = tank.tank_from_path("/mnt/ala/jobs/s171")
templ_path = tk.templates['maya_shot_env_json']
fields = {"Sequence": "tqn", "Shot": "tqn_040", "Step": "lay", "name": "tqn040"}
publishes = tk.paths_from_template(templ_path, fields)
versions = [templ_path.get_fields(x).get('version') for x in publishes]
versions.sort()
latest = versions[-1]
fields["version"] = latest
latest_publish = tk.paths_from_template(templ_path, fields)

tank_uri = "tank://s171/sequence:tqn/shot:tqn_040/step:lay/template:maya_shot_env_json/tqn040?version=latest"

"tank://s171/template:maya_shot_env_json?sequence=tqn&shot=tqn_040&step=lay&name=tqn040"
"tank://s171/tqn/tqn_040"







