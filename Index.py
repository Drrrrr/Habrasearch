from html.parser import HTMLParser
import urllib.request
import re
from os import listdir
import sys

class HabraParser(HTMLParser):
	parsing = False
	skip    = False

	#filterlist = [ ["p", ("class", "for_users_only_msg")] ]
	filterlist = [ "code" ]
	filtertag  = ""

	def addtokens(self, s):
		s = self.strip(s)
		s = s.lower()

		if not s.isspace() and s != "":
			self._print ("<" + s + ">")
			input()

	def strip(self, s):
		return re.sub('(-{2}|[\.\u00A0\u2014\t\n\r\,\:;\(\)><!"?{}\/])', " ", s, 0, 0)

	def _print( self, data ):
		if sys.platform == "win32":
			print( data.encode('cp866', errors='replace').decode('cp866') )
		else:
			print( data )

	def handle_starttag(self, tag, attrs):
		if tag == "div":
			for k,v in attrs:
				if k == "class":
					if v == "content html_format":
						self.parsing = True
					elif v == "clear":
						self.parsing = False
		else:
			if tag in self.filterlist and not self.skip:
				self.skip      = True
				self.filtertag = tag

	def handle_endtag(self, tag):
		if self.skip and tag == self.filtertag:
			self.skip      = False
			self.filtertag = ""

	def handle_data(self, data):
		if self.parsing and not self.skip:
			self.addtokens(data)

class HabraBuilder():
	pathtofiles = "D:\\Study\\Информационный Поиск\\Курсовая\\Habrasearch\\Data\\"
	filelist    = []
	parser      = HabraParser()

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
				self.parser.feed( data )


#parser = MyHTMLParser()
#parser.feed( page_source )

index = HabraBuilder()

index.buildindex()