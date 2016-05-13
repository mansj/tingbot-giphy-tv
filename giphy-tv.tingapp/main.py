import tingbot
from tingbot import *
from urlparse import urlparse
import os
import json
import urllib
import string
import hashlib
import random


giphy_tv_url = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=cats'

state = {}
channels = {'cats', 'dogs'}

imageloaded = 99

def filename_for_url(url):
    m = hashlib.md5()
    m.update(os.path.dirname(urlparse(url).path))
    thishash = m.hexdigest()
    return '/tmp/giphy-' + thishash + '_' + os.path.basename(urlparse(url).path)

@every(minutes=10)
def refresh_feed():
    global imageloaded
    image_urls = []
    
    for x in range(0, 3): 
        response = urllib.urlopen(giphy_tv_url)
        data = json.loads(response.read())
    
        for key, value in data.iteritems():
            if key != 'data': 
                continue
            else:
                image_urls.append(str(value['fixed_height_downsampled_url']))
            
    imageloaded = 0
    for image_url in image_urls:
        filename = filename_for_url(image_url)
        
        if not os.path.exists(filename):
            urllib.urlretrieve(image_url, filename)

        imageloaded = imageloaded + 1
        
        screen.fill(color='red')
        screen.text('Loading image ' + str(random.randint(0,199)) + str(imageloaded))


    state['image_urls'] = image_urls
    state['index'] = 0

@every(seconds=5)
def next_image():
    if 'image_urls' not in state:
        return
    
    image_urls = state['image_urls']
    state['index'] += 1
    
    if state['index'] >= len(image_urls):
        state['index'] = 0
    
    image_url = state['image_urls'][state['index']]
    state['image'] = Image.load(filename_for_url(image_url))

def loop():
    if 'image' not in state:
        screen.fill(color='black')
        screen.text('Loading...')
        return
    else:
        screen.fill(color='black')
        screen.text('Done!')
    
    image = state['image']
    
    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]
    
    sf = max(width_sf, height_sf)
    
    screen.image(state['image'], scale=sf)

# run the app
tingbot.run(loop)
