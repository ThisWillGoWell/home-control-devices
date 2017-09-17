import time
import threading
from rgbmatrix import Adafruit_RGBmatrix
import math
import requests
import Image #http://effbot.org/imagingbook/pil-index.htm
import ImageSequence
import ImageDraw


"""
Global Varibles

"""

SYSTEM ="clock"
SERVER_ADDRESS = 'http://192.168.1.10:8080'
SERVER_ENDPOINTS = ['/get?system=' + SYSTEM + "&what=imageUpdate",'/get?system=' + SYSTEM + "&what=imageStart", '/get?system=' + SYSTEM + "&what=resourceImage" ]
im = Image.new("RGBA", (96,32))
imageTimeline = {}


def t():
    return math.floor(time.time() * 1000)

def getImage():
    r = requests.get(SERVER_ADDRESS + SERVER_ENDPOINTS[2]);
    with open("resources.gif", 'wb') as fd:
        for chunk in r.iter_content(100):
            fd.write(chunk)
    fd.close()

    


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


class ImageDraw(threading.Thread):
    drawInterval = 100

    """docstring for ImageDraw"""
    def __init__(self, arg, drawInterval, event):
        super(ImageDraw, self).__init__()
        this.drawInterval = 100
        self.event = event

    def run(self):
        while True:
            matrix.SetImage(im.im.id,0,0)
            event.clear()
            time.sleep(self.drawInterval - t()%self.drawInterval)
    

class ImageUpdate(threading.Thread):
    """docstring for ImageUpdate"""
    masks = {}
    layers = {}
    imageQueue = []
    jsonQueue = []
    fills={}
    event = None;
    def __init__(self, arg, event):
        super(ImageUpdate, self).__init__()
        self.event = event


    def run(self):
        while True:
            event.wait()
            event.set()
            currentFrame = None
            start = time.time()
            #print("starting Draw")
            if lostConnection == True:
                im = random.choice(resources)       
            else:
                currentImageTimeline    = imageTimeline 
                for frame in currentImageTimeline["frames"]:  
                    if len(frame["elements"])!=0:
                        T = t()
                        currentTime = T - T%drawInterval
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

    def imageToMask(image, frameNumber=-1):
        #take in a resouce image and return a mask of that image.
        #Store that mask in a dict refrenced by source frame number 
        #so dont have to regenerate it each time.
        if frameNumber in self.masks:
            return masks[frameNumber]

        rows = image.size[1]
        cols = image.size[0] 

        p= 0
        emptyPixel = (0,0,0,255)
        #mask = Image.new("RGBA", image.size,(255,255,255,255))
        #pmask = Image.new("RGBA", (1,1), (0,0,0,0));
        pixels = image.getdata()

        m = []
        for p in pixels:
            if(p[0] == p[1] == p[2] == 0):
                m.append(0x00)
            else:
                m.append(0xff)
        maskData = bytearray(m)


        mask = Image.frombuffer("L", image.size, maskData)
        self.mask = mask.transpose(Image.ROTATE_180).transpose(Image.FLIP_LEFT_RIGHT)

        if frameNumber != -1:
            masks[frameNumber] = self.mask

        return mask

        


        

class ServerTalk(threading.Thread):
    queryTime = 5000
    processTime = 4000

    """docstring for ServerTalk"""
    def __init__(self):
        super(ServerTalk, self).__init__()

    def run():
        while True:
            T = t()
            startTime = T-T%drawInterval
            if reloadImage:     
                url = SERVER_ADDRESS + SERVER_ENDPOINTS[1] + "&t1=%d&t2=%d&interval=%d" % (startTime , startTime +  (queryTime + 1)*1000 , drawInterval)
            else:
                url = SERVER_ADDRESS + SERVER_ENDPOINTS[0] + "&t1=%d&t2=%d&interval=%d" % (startTime, startTime +  (queryTime + 1)*1000 , drawInterval)

            try:
                imageTimeline = requests.get(url, timeout=processTime).json()
                lostConnection = False
                reloadImage = False
            except requests.exceptions.Timeout:
                lostConnection = True
                reloadImage = True

            time.sleep(queryTime -t()%queryTime )



def Manager():

    getImage()
    processImage()
    e = threading.event()
    e.clear()
    client = ServerTalk()

