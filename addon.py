import sys
import os
import xbmc
import xbmcaddon
import json
import xbmcgui
import random
import xbmcplugin
from PIL import ImageFont, Image, ImageDraw

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'images')

def getHeight(rating, h, rad):
    return h-(float(rating)/10.0*(h-2*rad)+rad)

def get_episodes(show_id):
        postdata = json.dumps({"jsonrpc": "2.0",
                               "id": 1,
                               'method': 'VideoLibrary.GetEpisodes',
                               "params": {
                                   'tvshowid': show_id,
                                   "properties": ["season", "episode", "rating", "playcount"]
                               }})
        json_query = xbmc.executeJSONRPC(postdata)
        json_query = json.loads(json_query)
        if 'error' in json_query:
            xbmc.log('%s: ERROR: %s' % (ADDONID, json_query['error']['stack']['message']))
            return None
        json_query = json_query['result']['episodes']
        return json_query 

query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetTVShows",
            "params": {
                "properties": ["title", "genre", "rating", "art"],
                "sort": { "order": "ascending", "method": "label" }
            },
            "id": "libTvShows"
        }
rpc_result = xbmc.executeJSONRPC(jsonrpccommand=json.dumps(query, encoding='utf-8'))
xbmc.log(str(type(rpc_result))+" "+str(rpc_result),level=xbmc.LOGWARNING)

w = 500
h = 500
cc = [ (242, 0, 86, 2555), (255, 186, 210, 2555), (92, 96, 77, 2555)  ]
rad = w/40

 
pluginPath = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('profile') ).decode("utf-8")
addonPath = xbmcaddon.Addon().getAddonInfo('path')
xbmc.log(pluginPath + addonPath)
#create working path
xbmc.log("Create working path: "+pluginPath,level=xbmc.LOGWARNING)
try:
    os.mkdir(pluginPath)
except:
    xbmc.log("Failed to create path: "+pluginPath,level=xbmc.LOGWARNING)

#delete old files
xbmc.log("Remove all files in "+pluginPath,level=xbmc.LOGWARNING)
files = os.listdir(pluginPath)
for file in files:
    if file.endswith(".png"):
        os.remove(os.path.join(pluginPath,file))

json_result = json.loads(rpc_result)
json_result = json_result["result"]["tvshows"]

for item in json_result:        
    filename = pluginPath+'graphytv_id'+str(item["tvshowid"])+'_rand'+str(random.randint(1,10001))+'.png'
    xbmc.log("Create File: "+str(filename),level=xbmc.LOGWARNING)
    img = Image.new('RGB', (w, h), color = (200, 174, 126))
    draw = ImageDraw.Draw(img)
    
    #xbmc.log("Thumbnail "+str(item["art"]),level=xbmc.LOGWARNING)
    #background = Image.open(item["art"], 'r')
    #img_w, img_h = img.size    
    #offset = ((w - img_w) // 2, (h - img_h) // 2)
    #img.paste(background, offset)    
    
    #mean rating
    y = getHeight(item["rating"], h, rad)
    draw.line([0, y, w, y])
    
    fontFilename = os.path.join(addonPath,"FreeMono.ttf")
    try:                
        font = ImageFont.truetype(fontFilename, 15)        
    except:        
        xbmc.log("Failed to find font in "+fontFilename,level=xbmc.LOGWARNING)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
            xbmc.log("Using font arial.ttf",level=xbmc.LOGWARNING)
        except:
            xbmc.log("Using fallback font",level=xbmc.LOGWARNING)
            font = None
    
    #draw horizontal lines
    for ii in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        y = getHeight(ii, h, rad)
        draw.line([0, y, w, y], (0,0,0))
        draw.text([0,y], str(ii), font=font, fill = (0,0,0)) 
    
    #get all episodes
    try:    
        lst = get_episodes(item["tvshowid"])
    except Exception as e:
        xbmc.log("GraphyTVError: Did not get episodes: "+str(e),level=xbmc.LOGWARNING)
        lst = []
    
    #create image
    lastSeason = 0
    if len(lst)>1:
        for idx,episode in enumerate(lst):
            season = episode["season"]
            episodenumber = episode["episode"]
            rating = episode["rating"]        
            #xbmc.log("-->"+str(season)+"."+str(episodenumber)+": "+str(rating),level=xbmc.LOGWARNING)
            x = rad+idx*(float(w)-2*rad)/(len(lst)-1)   
            y = getHeight(rating, h, rad)
            draw.ellipse((x-rad, y-rad, x+rad, y+rad), fill=cc[int(season) % len(cc)]) #image.setPenColor( cc[season % len(cc)] )
            if lastSeason != season and idx != 0:
                draw.line([x-rad, 0, x-rad, h], (200-50, 174-50, 126-50))
            
            lastSeason = season
                        
    img.save(filename)

    
    try:            
        title = str(item["title"].encode('utf-8'))
    except: 
        try:
            title = str(item["title"])
        except:
            title = "Unknown Title" 

    try:        
        li = xbmcgui.ListItem(label = str(title)+" ("+str(round(item["rating"], 1))+")", iconImage=filename, thumbnailImage=filename)
        li.setArt({ 'thumb': filename, 'poster' : filename, 'banner': filename, 'fanart' : filename, 'clearart': filename, 'landscape' : filename, 'icon' : filename })
        #li = xbmcgui.Listitem.setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })    
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=filename, listitem=li)
    except Exception as e:
        xbmc.log("GraphyTVError: "+str(e))

xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False, updateListing=True)
