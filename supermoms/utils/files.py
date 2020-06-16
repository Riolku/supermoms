from flask import json

def load_json(filename):
  return json.load(open(filename))

def load_file(filename):
  with open(filename) as f:
    return f.read()