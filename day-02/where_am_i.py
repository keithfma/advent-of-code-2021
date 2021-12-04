from collections import namedtuple

INPUT_FILE = 'input.txt'


Direction = namedtuple('Direction', ['action', 'distance'])


# unpack input file into Direction objects
directions = [] 
with open(INPUT_FILE, 'r') as fp:
    for line in fp:
        parts = line.strip().split(' ')
        directions.append(
            Direction(parts[0], int(parts[1]))
        )

# puzzle #1 ----------

# iterate through the directions to find out the final location
x = 0
y = 0
for direction in directions:
    if direction.action == 'forward':
        x += direction.distance
    elif direction.action == 'up':
        y -= direction.distance
    elif direction.action == 'down': 
        y += direction.distance
    else:
        raise ValueError(f'Bad direction: {direction}')

print('puzzle #1 ----------')
print(f'x = {x}, y = {y}, x*y = {x*y}') 

   
# puzzle #1 ----------

# iterate through the directions to find out the final location (this time, with aim)
x = 0
y = 0
aim = 0

for direction in directions:
    if direction.action == 'forward':
        x += direction.distance
        y += aim*direction.distance
    elif direction.action == 'up':
        aim -= direction.distance
    elif direction.action == 'down': 
        aim += direction.distance
    else:
        raise ValueError(f'Bad direction: {direction}')

print('puzzle #2 ----------')
print(f'x = {x}, y = {y}, x*y = {x*y}') 
