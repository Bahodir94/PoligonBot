import yaml, os


text = {
	'langs' : [],
	'lang_codes' : []
}

root = os.path.dirname(os.path.abspath(__file__))	+ '/'

for m in os.listdir(path=root+'langs'):
	if m[-4:] == '.yml':
		with open(root+'langs/'+m) as f:
			text[m[:2]] = yaml.safe_load(f)
			text['langs'].append([text[m[:2]]['config']['name'], m[:2]])
			text['lang_codes'].append(m[:2])
