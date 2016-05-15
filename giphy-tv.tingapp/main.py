import tingbot
from tingbot import *
from urlparse import urlparse
import sys, os
import json
import urllib2
import string
import hashlib
import threading

# Debug sys to stdout
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# Set Debug on/off
debug = 1

state = {}
channels = ['cats', 'dogs']

# Set current channel
currentchannel = 0

# Define imageloader counter
imageloaded = 0

# Define threading list
threads = []

def get_channel(i):
    return 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=' + channels[i]

def filename_for_url(url):
    m = hashlib.md5()
    m.update(os.path.dirname(urlparse(url).path))
    thishash = m.hexdigest()
    return '/tmp/giphy-' + thishash + '_' + os.path.basename(urlparse(url).path)

def loading_screen(cur): 
    screen.fill(color='black')
    screen.text('Loading image ' + str(cur))
    screen.update()
    return

def update_screen():
    while 1 == 1:
        screen.update()

@button.press('left')
def on_left():

    global threads

    # Show static GIF
    image_url = 'static.gif'
    state['image'] = Image.load(image_url)
    
    image = state['image']
    
    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]
    
    sf = max(width_sf, height_sf)
    
    screen.image(state['image'], scale=sf)
    screen.update()

    # Change channel!
    global giphy_tv_url, currentchannel
    if currentchannel + 1 >= len(channels): 
        currentchannel = 0
    else:
        currentchannel = currentchannel + 1

    screen.text('Tuning to ' + channels[currentchannel])
        
    giphy_tv_url = get_channel(currentchannel)
    
    print giphy_tv_url
    
    t = threading.Thread(target=refresh_feed, args=(1, ))
    threads.append(t)
    t.start()
    print (len(threads))

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
    
    image = state['image']
    
    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]
    
    sf = max(width_sf, height_sf)
    
    screen.image(state['image'], scale=sf)
    screen.update()    


def refresh_feed(user_refreshed = 0):
    screen.update()
    global imageloaded, state
    
    image_urls = []
    
    for x in range(1, 11): 
        response = urllib2.urlopen(giphy_tv_url)
        data = json.loads(response.read())
    
        for key, value in data.iteritems():
            if key != 'data': 
                continue
            else:
                image_urls.append(str(value['fixed_height_downsampled_url']))
                if debug:
                    print('image_urls_append: ' + str(x))
            
    # Reset imageloaded counter
    imageloaded = 0
    
    # Load all images in the image_urls list to files
    for image_url in image_urls:
        if not user_refreshed:
            loading_screen(imageloaded + 1)
        
        filename = filename_for_url(image_url)

        # Get file from URL if it's not already downloaded
        if not os.path.exists(filename):
            gif = urllib2.urlopen(image_url)
            with open(filename,'wb') as output:
                  output.write(gif.read())

            if debug:
                print('urlretrieve: ' + str(image_url))


        imageloaded = imageloaded + 1

    # Update state list
    state['image_urls'] = image_urls
    state['index'] = 0
    
    return 1
    
def loop():
    global threads
    if 'image' not in state:
        screen.fill(color='black')
        screen.text('Loading...')
        refresh_feed()
        return

    image = state['image']

    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]
    
    sf = max(width_sf, height_sf)
    
    screen.image(state['image'], scale=sf)
    screen.update()
    
# run the app

# Define first channel
giphy_tv_url = get_channel(0)

# Start loop
tingbot.run(loop)
