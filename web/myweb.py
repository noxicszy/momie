# -*- coding: utf-8 -*-  
import sys
import web
import urllib2
import os
import sys
import json
sys.path.append("..")
from itemindex.queryguesser import *
from itemindex.gamesearcher import *

reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
	'/', 'home',
	'/gs', 'guesser',
	'/gamesearch','gamesearch'
)

render = web.template.render('html')

def gamesearcher(command):
	vm_env.attachCurrentThread()
	lresult = searcher.keywordsearch(command)
	res = []
	for game in lresult:
		res.append({'name':game.get('name'),
					'id':game.get('id'),
					'producer':game.get('producer'),
					'tags':game.get('tags').split(' ')[:min(12,len(game.get('tags').split(' ')))]
			})
	return res

class home:
	def GET(self):
		return render.home2()

class guesser:
	def GET(self):
		user_data = web.input()
		guessed = user_data.word
		resultlist = QueryGuesser().guess(guessed.decode("utf8"))
		l = min(6,len(resultlist))
		print json.dumps(resultlist[:l])
		return json.dumps(resultlist[:l])

class gamesearch:
	def GET(self):
		user_data = web.input()
		keywords = user_data.keyword
		res = gamesearcher(keywords)
		return render.resultGame(keywords,res)


if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()