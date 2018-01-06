# -*- coding: utf-8 -*-  
import sys
import web
import urllib2
import os
import sys
import json
import cv2
import numpy
import re
sys.path.append("..")
from itemindex.queryguesser import *
from itemindex.gamesearcher import *
from webfetch.picture_query.ImageSet import *

reload(sys)
sys.setdefaultencoding('utf-8')

#load guesser
Guesser = QueryGuesser()

urls = (
	'/', 'home',
	'/guesser', 'guesser',
	'/gamesearch','gamesearch',
	'/imgsearch','imgsearch',
	'/rank','gamerank'
)

render = web.template.render('html')

def gamesearcher(command,rankmod=0):
	vm_env.attachCurrentThread()
	lresult = searcher.keywordsearch(command,rankmod)
	res = []
	for game in lresult:
		res.append({'name':game.get('name'),
					'id':game.get('id'),
					'producer':game.get('producer'),
					'tags':game.get('tags').split(' ')[:min(12,len(game.get('tags').split(' ')))]
			})
	return res

def getID(store_url):
    m = re.search("apps+/(\d+)/*", store_url)
    return str(m.group(1))

def getnamebyid(id):
	vm_env.attachCurrentThread()
	return searcher.idget(id).get('name')

def imgsearcher(filename):
	targetimg = cv2.imread(filename, cv2.IMREAD_COLOR)
	#targetimg = numpy.array(filename)
	similars = imageSet.getSimilar(targetimg)
	res = []
	if similars != None:
		for imgurl in similars:
			res.append({'imgurl':imgurl,
						'name':getnamebyid(int(getID(imgurl)))
				})
	return res

class home:
	def GET(self):
		return render.home2()

class guesser:
	def GET(self):
		user_data = web.input()
		guessed = user_data.word
		resultlist = Guesser.guess(guessed.decode("utf8"))
		l = min(6,len(resultlist))
		return json.dumps(resultlist[:l])

class gamesearch:
	def GET(self):
		user_data = web.input()
		keywords = user_data.keyword
		res = gamesearcher(keywords)
		return render.resultGame(keywords,res)

class imgsearch:
    def POST(self):
        user_data = web.input(img={})
        filename = user_data.img.filename
        name,ext = os.path.splitext(filename)
        ext = ext.lower()
        safeImageExts =('.png','.jpeg','.jpg','.gif')
        if not ext in safeImageExts:
            return 'file type error'
        #保存文件到服务器
        fout = open(filename,'wb')
        fout.write(user_data.img.file.read())
        fout.close()
        res = imgsearcher(filename)
        #从服务器删除文件
        os.remove(filename)
        return render.resultImg(res)
        
class gamerank:
	def GET(self):
		user_data = web.input()
		keywords = user_data.keyword
		rankmod = int(user_data.rankmod)
		res = gamesearcher(keywords,rankmod)
		return json.dumps(res)

if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()