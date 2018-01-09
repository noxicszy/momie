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
from itemindex.querycorrection import *
from related.guess import *

reload(sys)
sys.setdefaultencoding('utf-8')

#load guesser
Guesser = QueryGuesser()

urls = (
	'/', 'home',
	'/guesser', 'guesser',
	'/gamesearch','gamesearch',
	'/imgsearch','imgsearch',
	'/rank','gamerank',
	'/companysearch','companysearch',
	'/item','item'
)

render = web.template.render('html')

def gamesearcher(command,rankmod=0):
	vm_env.attachCurrentThread()
	lresult = searcher.keywordsearch(command,rankmod)
	res = []
	for game in lresult:
		tags = ''
		try:
			if len(game.get('tags')) >= 40:
				tags = game.get('tags')[:40].split(' ')[:-1]
			else:
				tags = game.get('tags').split(' ')
		except:pass
		res.append({'name':game.get('name'),
					'id':game.get('id'),
					'producer':game.get('producer'),
					'tags':tags,
					'price':game.get('price'),
					'cover':game.get('cover')
			})
	return res

def companysearcher(command):
	vm_env.attachCurrentThread()
	lresult = searcher.producersearch(command)
	res = []
	for game in lresult:
		tags = ''
		try:
			if len(game.get('tags')) >= 40:
				tags = game.get('tags')[:40].split(' ')[:-1]
			else:
				tags = game.get('tags').split(' ')
		except:pass
		res.append({'name':game.get('name'),
					'id':game.get('id'),
					'producer':game.get('producer'),
					'tags':tags,
					'price':game.get('price'),
					'cover':game.get('cover')
			})
	return res


#get id by imgurl
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
			imgid = getID(imgurl)
			res.append({'imgurl':imgurl,
						'name':getnamebyid(int(imgid)),
						'id':imgid
				})
	return res

def gamegetter(id):
	vm_env.attachCurrentThread()
	lres = searcher.idget(id)
	lres['description'] = ''.join(lres['description'].split(' '))
	for i in range(len(lres['vector'])):
		lres['vector'][i] = int((lres['vector'][i]+0.3)*180)
	try:
		lres['tags'] = lres['tags'].split(' ')
	except:pass
	lres['rev'] = []
	for review in lres['review']:
		lres['rev'].append({'authorid':review['author']['steamid'],
							'playtime':review['author']['playtime_forever'],
							'review-content':review['review']
			})
	del lres['review']
	lres['rel'] = []
	for relatedid in lres['related']:
		vm_env.attachCurrentThread()
		lrres = searcher.idget(int(relatedid))
		tags = []
		try:
			tags = lrres['tags'][:40].split(' ')
		except:pass
		lres['rel'].append({'name':lrres['name'],'tags':tags,'id':relatedid})
	del lres['related']
	del lres['names']
	return lres

def minigamegetter(id):
	vm_env.attachCurrentThread()
	lres = searcher.idget(id)
	try:
		if len(lres['tags']) >= 40:
			lres['tags'] = lres['tags'][:40].split(' ')[:-1]
		else:
			lres['tags'] = lres['tags'].split(' ')
	except:pass
	del lres['description'],lres['vector'],lres['review'],lres['related'],lres['names'],lres['urls']
	return lres

class home:
	def GET(self):
		user_data = web.input()
		visited = web.cookies(visit="").visit.strip()
		print 'v',visited
		visited = visited.split('|')[:-1]
		print visited
		items = []
		for id in guess(visited):
			items.append(minigamegetter(int(id)))
		try:
			ifC = user_data.ifC
			return render.home2(1,items)
		except:
			return render.home2(0,items)

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
		try:
			ifcorrect = user_data.ifcorrect
		except:
			ifcorrect = 'true'

		if ifcorrect == 'true':
			corrected = correcter.correct(keywords)
			if corrected == None or corrected == keywords:
				res = gamesearcher(keywords)
				return render.resultGame(keywords,res,0)
			else:
				res = gamesearcher(corrected)
				if res == []:
					res = gamesearcher(keywords)
					return render.resultGame(keywords,res,0)
				else:
					return render.resultGame(corrected,res,keywords)
		else:
			res = gamesearcher(keywords)
			return render.resultGame(keywords,res,0)
		
		

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

class companysearch:
	def GET(self):
		user_data = web.input()
		keywords = user_data.keyword
		try:
			ifcorrect = user_data.ifcorrect
		except:
			ifcorrect = 'true'

		if ifcorrect == 'true':
			corrected = correcter.correct(keywords)
			if corrected == None or corrected == keywords:
				res = companysearcher(keywords)
				return render.resultCompany(keywords,res,0)
			else:
				res = companysearcher(corrected)
				if res == []:
					res = companysearcher(keywords)
					return render.resultCompany(keywords,res,0)
				else:
					return render.resultCompany(corrected,res,keywords)
		else:
			res = companysearcher(keywords)
			return render.resultCompany(keywords,res,0)

class item:
	def GET(self):
		user_data = web.input()
		id = user_data.id
		visited = web.cookies(visit="").visit
		print 1,visited
		web.setcookie('visit', visited+id+'|')
		item = gamegetter(int(id))
		return render.itemGame(item)


if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()