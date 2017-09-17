from PIL import Image

import time

import requests as request
import json
import math
import threading
from ast import literal_eval

SERVER_ADDRESS = 'http://localhost:8080'
SERVER_ENDPOINTS = ['/getImageTimeline']
#Get Iamge
#http://www.effbot.org/imagingbook/pil-index.htm
resources = []

#file = cStringIO.StringIO(request.urlopen("http://192.168.1.84:8080/getImage").read());
#resourceImage = Image.open(file);

def analyseImage(path):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode 
    before processing all frames.
    '''
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def processImage(path):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(path)['mode']
    
    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')
    
    try:
        while True:
                      
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)
            
            new_frame = Image.new('RGBA', im.size)
            
            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)
            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            resources.append(new_frame);
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass



nextStart = math.floor(time.time()) * 1000  
nextStop = nextStart  + 2000
nextTimelineUpdateTime = nextStart
nextImageUpdateTime = nextStart
imageTimeline    =None  
canUpdate= True
im = None
def getImageUpdate():
    global imageTimeline, nextTimelineUpdateTime, nextStart, nextStop, canUpdate 
    if time.time() * 1000 > nextTimelineUpdateTime and canUpdate:
        url = SERVER_ADDRESS + SERVER_ENDPOINTS[0]
        response = request.get(url + "?start=%d&end=%d" % (nextStart, nextStop))
        jsonStr = str(response.text)
    
        imageTimeline = json.loads(jsonStr)
        nextTimelineUpdateTime = nextStop - imageTimeline["interval"] - 1000
        nextStart = nextTimelineUpdateTime - 2000
        nextStop = nextTimelineUpdateTime + 2000 
        canUpdate=False


    
def updateImage():
    global nextImageUpdateTime, imageTimeline, canUpdate, im 
    currentFrame = None
    if time.time() * 1000 > nextImageUpdateTime:
        currentImageTimeline = imageTimeline
        for frame in currentImageTimeline["frames"]:
            if frame["elements"][0]["t"] - (math.floor(time.time() * 1000 /currentImageTimeline["interval"]) * currentImageTimeline["interval"]) == 0:
                currentFrame = frame["elements"]
                break

    if currentFrame != None:
        if im != None:
            im.close()
        im = Image.new("RGBA", resources[0].size)
        for element in currentFrame:
            for frame in element["f"]:  
                im.paste(resources[frame["n"]].crop((0,0,frame["w"], frame["h"])), (frame["c"], frame["r"]))
        
        im.load()

        im.show();
        nextImageUpdateTime = nextImageUpdateTime + imageTimeline["interval"]
        canUpdate = True

'''
class updateThread(threading.Thread):
    def __init__(self, threadID, funciton)
        threading.Thread.__init__(self)
        self.threadID= threadID
        self.funciton = funciton
    def run(self)

    def getTimeline
'''


def updateThread():
    getImageUpdate()
    time.sleep(imageTimeline["interval"]/1000.0)


processImage("resources.gif")   
start = time.time() * 1000
t = threading.Thread(target = updateThread)
t.daemon = True  
t.start()
while canUpdate  == True:
    pass
updateImage()

