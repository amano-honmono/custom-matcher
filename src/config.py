import yaml

with open('/opt/project/config.yml') as file:
    config = yaml.safe_load(file)