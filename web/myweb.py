# -*- coding: utf-8 -*-  
import sys
import web
import urllib2
import os
import sys
import json
sys.path.append("..")
from itemindex.queryguesser import *

reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
	'/', 'home',
	'/gs', 'guesser',
)

render = web.template.render('html')

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

if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()