from html.parser import HTMLParser
import urllib.request
import re
from os import listdir
import sys

#sys.setdefaultencoding("utf-8")

class MyHTMLParser(HTMLParser):
	parsing = False
	skip    = False

	def addtokens(self, s):
		s = self.strip(s)
		s = s.lower()

		tokens = s.split()

		print (s)
		input()

	def strip(self, s):
		return re.sub('(-{2}|[\.\u00A0\t\n\r\,\:;\(\)><!"?{}])', " ", s, 0, 0)

	def handle_starttag(self, tag, attrs):
		if tag == "div":
			for k,v in attrs:
				if k == "class":
					if v == "content html_format":
						self.parsing = True
					elif v == "clear":
						self.parsing = False
		elif tag == "br":
			self.skip = False
		#else:
		#	self.skip = True

	def handle_data(self, data):
		if self.parsing and not self.skip:
			self.addtokens(data)

class Habrabuilder():
	pathtofiles = "D:\\Study\\Информационный Поиск\\Курсовая\\Habrasearch\\Data\\"
	filelist = []


	def __init__( self ):

		# Getting list of files to parse

		self.filelist = listdir( self.pathtofiles )

	def _print( self, data ):
		if sys.platform == "win32":
			print( data.encode('cp866', errors='replace') )
		else:
			print( data )

	def buildindex( self ):
		data = ""

		for fname in self.filelist:
			with open( self.pathtofiles + fname, 'r', encoding='utf-8' ) as f:
				data = f.read()

				#self._print( data )

				input()


#parser = MyHTMLParser()
#parser.feed( page_source )

index = Habrabuilder()

index.buildindex()