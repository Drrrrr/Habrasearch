from html.parser import HTMLParser
import urllib.request
import re
from os import listdir
import sys
import time

class Stemmer:
    # Helper regex strings.
    _vowel = "[аеиоуыэюя]"
    _non_vowel = "[^аеиоуыэюя]"

    # Word regions.
    _re_rv = re.compile(_vowel)
    _re_r1 = re.compile(_vowel + _non_vowel)

    # Endings.
    _re_perfective_gerund = re.compile(
        r"(((?P<ignore>[ая])(в|вши|вшись))|(ив|ивши|ившись|ыв|ывши|ывшись))$"
    )
    _re_adjective = re.compile(
        r"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|"
        r"ую|юю|ая|яя|ою|ею)$"
    )
    _re_participle = re.compile(
        r"(((?P<ignore>[ая])(ем|нн|вш|ющ|щ))|(ивш|ывш|ующ))$"
    )
    _re_reflexive = re.compile(
        r"(ся|сь)$"
    )
    _re_verb = re.compile(
        r"(((?P<ignore>[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|"
        r"нно))|(ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|"
        r"ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю))$"
    )
    _re_noun = re.compile(
        r"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|"
        r"ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$"
    )
    _re_superlative = re.compile(
        r"(ейш|ейше)$"
    )
    _re_derivational = re.compile(
        r"(ост|ость)$"
    )
    _re_i = re.compile(
        r"и$"
    )
    _re_nn = re.compile(
        r"((?<=н)н)$"
    )
    _re_ = re.compile(
        r"ь$"
    )

    def stem(self, word):
        """
        Gets the stem.
        """

        rv_pos, r2_pos = self._find_rv(word), self._find_r2(word)
        word = self._step_1(word, rv_pos)
        word = self._step_2(word, rv_pos)
        word = self._step_3(word, r2_pos)
        word = self._step_4(word, rv_pos)
        return word

    def _find_rv(self, word):
        """
        Searches for the RV region.
        """

        rv_match = self._re_rv.search(word)
        if not rv_match:
            return len(word)
        return rv_match.end()

    def _find_r2(self, word):
        """
        Searches for the R2 region.
        """

        r1_match = self._re_r1.search(word)
        if not r1_match:
            return len(word)
        r2_match = self._re_r1.search(word, r1_match.end())
        if not r2_match:
            return len(word)
        return r2_match.end()

    def _cut(self, word, ending, pos):
        """
        Tries to cut the specified ending after the specified position.
        """

        match = ending.search(word, pos)
        if match:
            try:
                ignore = match.group("ignore") or ""
            except IndexError:
                # No ignored characters in pattern.
                return True, word[:match.start()]
            else:
                # Do not cut ignored part.
                return True, word[:match.start() + len(ignore)]
        else:
            return False, word

    def _step_1(self, word, rv_pos):
        match, word = self._cut(word, self._re_perfective_gerund, rv_pos)
        if match:
            return word
        _, word = self._cut(word, self._re_reflexive, rv_pos)
        match, word = self._cut(word, self._re_adjective, rv_pos)
        if match:
            _, word = self._cut(word, self._re_participle, rv_pos)
            return word
        match, word = self._cut(word, self._re_verb, rv_pos)
        if match:
            return word
        _, word = self._cut(word, self._re_noun, rv_pos)
        return word

    def _step_2(self, word, rv_pos):
        _, word = self._cut(word, self._re_i, rv_pos)
        return word

    def _step_3(self, word, r2_pos):
        _, word = self._cut(word, self._re_derivational, r2_pos)
        return word

    def _step_4(self, word, rv_pos):
        _, word = self._cut(word, self._re_superlative, rv_pos)
        match, word = self._cut(word, self._re_nn, rv_pos)
        if not match:
            _, word = self._cut(word, self._re_, rv_pos)
        return word

class HabraParser(HTMLParser):
	friend  = None
	parsing = False
	skip    = False

	#filterlist = [ ["p", ("class", "for_users_only_msg")] ]
	filterlist = [ "code" ]
	filtertag  = ""

	wordRe = re.compile("\w+")

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
			s = str.lower(data)

			batch = self.wordRe.findall(s)
			self.friend.addbatch( batch )

class HabraBuilder():
	pathtofiles = "D:\\Study\\Информационный Поиск\\Курсовая\\Habrasearch\\Data\\"
	filelist    = []
	index       = {}
	docId       = 0
	docIdRe     = None

	# Other modules
	parser      = HabraParser()
	stemmer     = Stemmer()

	badfiles    = []

	def __init__( self ):
		# Initing vars
		self.parser.friend = self

		self.docIdRe = re.compile("\d+")

		# Getting list of files to parse
		self.filelist = listdir( self.pathtofiles )

	def addbatch( self, batch ):
		for t in batch:
			t = self.stemmer.stem(t)

			if self.index.get(t) == None:
				self.index[t] = [self.docId]
			else:
				ref = self.index[t]
				if self.docId not in ref:
					ref.append( self.docId )

	def buildindex( self ):
		global start

		data = ""

		size = len(self.filelist)
		i    = 0

		for fname in self.filelist:
			with open( self.pathtofiles + fname, 'r', encoding='utf-8' ) as f:
				docIdObj = self.docIdRe.search( fname )
				self.docId = int( docIdObj.group(0) )

				try:
					data = f.read()
				except UnicodeDecodeError as err:
					self.badfiles.append( self.docId )
				else:
					self.parser.feed( data )

			i += 1

			if i % 100 == 0:
				self.parser.reset()

			if i % int(size/10) == 0:
				print( (i*100)/size, "%" )
				print("Time: ", time.time() - start)


start = time.time()

index = HabraBuilder()
index.buildindex()

with open( "out.txt", "w", encoding="utf-8" ) as f:
	f.write( str(index.index) )

end = time.time()

print( "Time: ", end - start )

with open( "badfiles.txt", "w" ) as f:
	f.write( str(index.badfiles) )