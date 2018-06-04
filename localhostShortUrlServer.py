import http.server
import requests
import urllib
import os
import threading
import re
from socketserver import ThreadingMixIn

myDict={}

def urlify(s):

     # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"[^\w\s]", '', s)

     # Replace all runs of whitespace with a single dash
     s = re.sub(r"\s+", '-', s)

     return s
class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class handler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		form='''<!DOCTYPE html><title>Shorten your URL</title><form method="POST" action="http://localhost:8000/"><textarea name="longURI"></textarea><br><textarea name="shortTxt"></textarea><br><button type="submit">Cut it!</button></form>'''
		if self.path=="/emptyValues":
			self.send_response(400)
			self.send_header("Content-type","text/html; charset:utf-8")
			self.end_headers()
			for key in myDict.keys():
				form+='''<a href="'''+key+'''">http://localhost:8000/'''+myDict[key]+'''</a><br>'''
			form+="\n Please enter all values."
			self.wfile.write(form.encode())
		elif self.path=="/invalidURI":
			self.send_response(404)
			self.send_header("Content-type","text/html; charset:utf-8")
			self.end_headers()
			for key in myDict.keys():
				form+='''<a href="'''+key+'''">http://localhost:8000/'''+myDict[key]+'''</a><br>'''
			form+="\n The URL you added is invalid."
			self.wfile.write(form.encode())
		elif self.path=="/withLink":
			self.send_response(200,'OK')
			self.send_header("Content-type","text/html; charset:utf-8")
			self.end_headers()
			for key in myDict.keys():
				form+='''<a href="'''+key+'''">http://localhost:8000/'''+myDict[key]+'''</a><br>'''
			self.wfile.write(form.encode())
		elif self.path=="/":
			self.send_response(200,'OK')
			self.send_header("Content-type","text/html; charset:utf-8")
			self.end_headers()
			for key in myDict.keys():
				form+='''<a href="'''+key+'''">http://localhost:8000/'''+myDict[key]+'''</a><br>'''
			self.wfile.write(form.encode())
		else:
			req=self.path[1:]
			if req in myDict.values():
				self.send_response(303)
				key = list(myDict.keys())[list(myDict.values()).index(req)]
				self.send_header('Location', key)
				self.end_headers()
			else:
				self.send_response(200,'OK')
				self.send_header("Content-type","text/html; charset:utf-8")
				self.end_headers()
				for key in myDict.keys():
					form+='''<a href="'''+key+'''">http://localhost:8000/'''+myDict[key]+'''</a><br>'''
				self.wfile.write(form.encode())
	def do_POST(self):
		data=self.rfile.read(int(self.headers.get('Content-length', 0))).decode()
		querries=urllib.parse.parse_qs(data)
		if ('longURI' in querries) and ('shortTxt' in querries):
			try:
				r = requests.get(querries['longURI'][0])
				if r.status_code==200:
					querries['shortTxt'][0]=urlify(querries['shortTxt'][0])
					re=urllib.parse.urlparse(querries['longURI'][0])
					myDict[querries['longURI'][0]]=querries['shortTxt'][0]
					self.send_response(303)
					self.send_header('Location', '/withLink')
					self.end_headers()
				elif r.status_code==404:
					self.send_response(303)
					self.send_header('Location', '/invalidURI')
					self.end_headers()
			except requests.exceptions.RequestException as e:  
   				print(e)
   				self.send_response(303)
   				self.send_header('Location', '/invalidURI')
   				self.end_headers()
		else:
   			self.send_response(303)
   			self.send_header('Location', '/emptyValues')
   			self.end_headers()
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	serv=ThreadHTTPServer(('', port),handler)
	serv.serve_forever()