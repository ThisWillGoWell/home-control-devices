ONPI = True


import time

import json
import math
import random
import threading
import requests #http://docs.python-requests.org/en/master/
import grequests

if ONPI:
    from rgbmatrix import Adafruit_RGBmatrix
    import Image #http://effbot.org/imagingbook/pil-index.htm
    import ImageSequence
    import ImageDraw


else:
    from PIL import Image #http://effbot.org/imagingbook/pil-index.htm
    from PIL import ImageSequence
    from PIL import ImageDraw   



from socket import timeout



if(ONPI):
    matrix = Adafruit_RGBmatrix(32, 3)

SYSTEM ="clock"
SERVER_ADDRESS = 'http://192.168.1.84:8080'
SERVER_ENDPOINTS = ['/get?system=' + SYSTEM + "&what=imageUpdate",'/get?system=' + SYSTEM + "&what=imageStart", '/get?system=' + SYSTEM + "&what=resourceImage" ]


#Get Iamge
#http://www.effbot.org/imagingbook/pil-index.htm
resources = []


def getImage():
    r = requests.get(SERVER_ADDRESS + SERVER_ENDPOINTS[2]);
    with open("resources.gif", 'wb') as fd:
        for chunk in r.iter_content(100):
            fd.write(chunk)
    fd.close()

    
getImage()

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


queryTime = 5
nextStart = math.floor(time.time()) * 1000  
nextStop = nextStart  + queryTime * 1000
nextTimelineUpdateTime = nextStart
nextImageUpdateTime = nextStart
interval = 100
rs = []
lostConnection = True
imageTimeline   = []
imageTimeline= {'interval' :100}
reloadImage = True
blankImage = Image.new("RGBA",(96,32), (0,0,0,255))
layers = {};
masks = {};
fills = {};
successResponse = False;
processTime = 2
drawInterval = 100
im = blankImage
def exception_handler(request, exception):
    global lostConnection, reloadImage, successResponse    
    #print("fail!")
    successResponse = False
    lostConnection = True
    reloadImage = True

def processResponse():
    global lostConnection, rs, successResponse, imageTimeline, reloadImage, timerCounter
    #print("process!")
    if successResponse:
        timerCounter = timerCounter + time.time()
        imageTimeline = rs[0].response.json();
        #print(str(len(rs[0].response.text) / 1024 )+ "kB")
        lostConnection = False
        reloadImage = False




def sendRequest():
    global  queryTime, interval, reloadImage, rs, successResponse, processTime, drawInterval,timerCounter
    t = long(math.floor(time.time()*1000))
    timerCounter = time.time()
    startTime = t-t%drawInterval
    if reloadImage:     
        url = SERVER_ADDRESS + SERVER_ENDPOINTS[1] + "&t1=%d&t2=%d&interval=%d" % (startTime , startTime +  (processTime + queryTime + 1)*1000 , drawInterval)
    else:
        url = SERVER_ADDRESS + SERVER_ENDPOINTS[0] + "&t1=%d&t2=%d&interval=%d" % (startTime, startTime +  (processTime + queryTime + 1)*1000 , drawInterval)
    successResponse = True
    rs = [grequests.get(url ,timeout=processTime)]
    threading.Timer(3,processResponse).start()
    threading.Timer(queryTime, sendRequest).start()
    grequests.map(rs,exception_handler=exception_handler)
    timerCounter = time.time() - timerCounter
    

def imageToMask(image, frameNumber=-1):
    global masks
    #take in a resouce image and return a mask of that image.
    #Store that mask in a dict refrenced by source frame number 
    #so dont have to regenerate it each time.
    if frameNumber in masks:
        return masks[frameNumber]

    rows = image.size[1]
    cols = image.size[0] 

    p= 0
    emptyPixel = (0,0,0,255)
    #mask = Image.new("RGBA", image.size,(255,255,255,255))
    #pmask = Image.new("RGBA", (1,1), (0,0,0,0));
    pixels = image.getdata()

    if ONPI:
        m = []
        for p in pixels:
            if(p[0] == p[1] == p[2] == 0):
                m.append(0x00)
            else:
                m.append(0xff)
        maskData = bytearray(m)


    else:
        maskData = bytes([])
        maskOn = bytes([0xff])
        maskOff = bytes([0x00])
        
        for p in range(0, len(pixels)):
            if pixels[p][0] == pixels[p][1] == pixels[p][2] == 0:
                maskData =  maskData + maskOff
            else:
                maskData = maskData + maskOn;


    mask = Image.frombuffer("L", image.size, maskData)
    mask = mask.transpose(Image.ROTATE_180).transpose(Image.FLIP_LEFT_RIGHT)

    if frameNumber != -1:
        masks[frameNumber] = mask

    return mask

def putImage():
    global im
    threading.Timer(0.1,putImage).start()
    im.load()
    matrix.SetImage(im.im.id,0,0)
    threading.Thread(target=updateImage).start()


lastDrawTime = 0
def updateImage():
    global layers, blankImage, fills, nextImageUpdateTime, imageTimeline, lostConnection, masks,drawInterval, lastDrawTime, last,im
    currentFrame = None
    start = time.time()
    #print("starting Draw")
    if lostConnection == True:
        im = random.choice(resources)       
    else:
        currentImageTimeline    = imageTimeline 
        for frame in currentImageTimeline["frames"]:  
            if len(frame["elements"])!=0:
                t = math.floor(time.time() * 1000)
                currentTime = t - t%drawInterval
                #print(time.time(), (math.floor(time.time() * 1000 /currentImageTimeline["interval"]) * currentImageTimeline["interval"]), frame["time"] - (math.floor(time.time() * 1000 /currentImageTimeline["interval"]) * currentImageTimeline["interval"]),currentImageTimeline["interval"] )
                if frame["time"] - currentTime == 0:
                    currentFrame = frame["elements"]                 
                    break
                
        if currentFrame != None:
            #im = Image.new("RGBA", resources[0].size)
            for element in currentFrame:
                currentLayer = Image.new("RGBA", (96,32))
                if element["fill"]["fill"]:
                    key = "%d%d%d%d" % (element["fill"]["r"],element["fill"]["g"],element["fill"]["b"],element["fill"]["a"])
                    if key not in fills:
                        fills[key] = Image.new("RGBA", (96,32),(element["fill"]["r"],element["fill"]["g"],element["fill"]["b"],element["fill"]["a"]))

                    fillImage = fills[key]
                    for frame in element["f"]:
                        sr = 0 
                        sc = 0 
                        if("sr" in frame):
                            sr = frame["sr"]
                        if("sc" in frame):
                            sc = frame["sc"]
                        currentLayer.paste(fillImage.crop((sc,sr, sc + frame["w"], sr + frame["h"])), (frame["c"], frame["r"]),imageToMask(resources[frame["n"]].crop((sc,sr,sc + frame["w"], sr + frame["h"]))))
                else:
                    for frame in element["f"]:
                        sr = 0 
                        sc = 0 
                        if("sr" in frame):
                            sr = frame["sr"]
                        if("sc" in frame):
                            sc = frame["sc"]

                        drawImage = resources[frame["n"]].crop((sc,sr,sc + frame["w"], sr + frame["h"]))
                        currentLayer.paste(drawImage, (frame["c"], frame["r"]), imageToMask(drawImage))
                layers[element["l"]] = currentLayer
                masks["layer-"+str(element["l"])] = imageToMask(currentLayer)
            
            im = Image.new("RGBA", (96,32))
          
            for i in range(len(layers)):
                im.paste(layers[i],(0,0),imageToMask(layers[i],"layer-" + str(i)))
        
            #im = Image.blend(im, blankImage, currentImageTimeline["alpha"])
            """
            if ONPI:
                #im.load()
                matrix.SetImage(im.im.id,0,0);
                print(time.time() - start, time.time() - lastDrawTime,  currentTime)
                lastDrawTime = time.time()
            else:
                pass
                #showImage(image)
            """



 

processImage("resources.gif")
imageToMask(resources[0], 0)
start = time.time() * 1000
im = Image.new("RGBA", resources[0].size)
for i in range(10):
    layers[i] = blankImage
t1 = threading.Timer(0,sendRequest)
t2 = threading.Timer(3,putImage)

t1.start()
t2.start()