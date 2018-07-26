import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import json

import main

f = open('event.json', 'r')
event = json.load(f)
f.close()

print("event.json")
print(event)

print()

print('result')
print(main.handle(event, {}))
