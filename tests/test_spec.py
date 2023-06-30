import requests
import yaml

def test_invalid_spec():
    url = 'https://github.com/jetpack-io/typeid/blob/main/spec/invalid.yml'
    r = requests.get(url, allow_redirects=True)
    invalid_yaml=r.content
    documents = yaml.full_load(invalid_yaml)
def test_valid_spec():
    url = 'https://github.com/jetpack-io/typeid/blob/main/spec/valid.yml'
    r = requests.get(url, allow_redirects=True)
    valid_yaml=r.content
    documents = yaml.full_load(valid_yaml)
    
    
    