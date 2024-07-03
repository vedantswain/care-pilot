# Importing Libaries
import requests
import os
import random

no_of_images_to_pull = int(input('How many avatars you need? '))
size = tuple(input('Enter the image size(eg. 400x400): ').split('x'))
base_url = 'https://dummyimage.com/'
colors = (
    ('fff', '000'),
    ('000', 'fff'),
    ('cf38cf', 'fff'),
)
formats = (
    'png',
    'jpg',
    'gif',
)
folder_name = 'avatar_images'
try:
    os.mkdir(folder_name)
except:
    pass


for i in range(no_of_images_to_pull):
    img_format = formats[int(random.randint(0, 2))]
    color = colors[int(random.randint(0, 2))]
    response = requests.get(
        f'{base_url}{size[0]}x{size[1]}.{img_format}/{color[0]}/{color[1]}&text=Avatar+{i}'
    )
    with open(f'{folder_name}/Avatar{i}.{img_format}', 'wb') as file:
        file.write(response.content)