import yaml

def configuration():
    with open('config.yml', 'r') as yamlfile:
        return(yaml.full_load(yamlfile))
