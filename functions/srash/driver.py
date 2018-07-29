import json

import lambda_function

f = open('event.json', 'r')
event = json.load(f)
f.close()

print("event.json")
print(event)

print()

print('result')
print(lambda_function.lambda_handler(event, {}))
