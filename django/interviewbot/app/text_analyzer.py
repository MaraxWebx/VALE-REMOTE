import it_core_news_md as it_core
import time
import pandas

class TextAnalyzer:

	def __init__(self, corpus=None):
		self.doc = None
		self.nlp = it_core.load()
		if corpus is not None:
			self.doc = self.nlp(corpus)
			self.LENGTH = len(self.doc)

		self.results = []
		self.temp_data = []
		# State variables
		self.verb_found = False
		self.conj_join = False
		self.propn_list = False
		self.start = 0
		self.end = 0


	def __reset_variables(self):
		self.verb_found = False
		self.conj_join = False
		self.propn_list = False
		if self.temp_data:
			self.temp_data.sort()
			self.data.append(self.temp_data)
		self.temp_data = []


	def put(self, corpus=None):
		if corpus is None:
			return None
		self.doc = self.nlp(corpus)
		self.LENGTH = len(self.doc)


	def print_formatted_text(self):
		if self.doc is None:
			raise Exception("No text input given. Init this class with corpus as parameter or use put(corpus) method.")
		else:
			data = {
				'text': [],
				'pos': [],
				'tag': []
			}

			for token in self.doc:
				data['text'].append(token.text)
				data['pos'].append(token.pos_)
				data['tag'].append(token.tag_)

			df = pandas.DataFrame(data)
			pandas.set_option('display.max_colwidth', 400)
			pandas.set_option('display.max_rows', 9999)
			print(df[['text','pos','tag']])
				

	def __check_doc(self):
		if self.doc is None:
			raise Exception("No text input given. Init this class with corpus as parameter or use put(corpus) method.")


	def get_benchmark(self):
		return str(self.end - self.start)
        

	def analyze(self):
		self.__check_doc()

		index = 0
		self.data = []
		self.start = time.time_ns() // 1000000 
		while index < self.LENGTH:
			self.__analyze_token(self.doc[index])
			if self.__check_if_complete() or self.doc[index].text == '.':
				self.__reset_variables()
			index += 1

		self.__reset_variables()
		self.end = time.time_ns() // 1000000 
		return self.data


	def __check_if_complete(self):
		flagVerb = False
		flagNounOrPropn = False
		for i in self.temp_data:
			if i.pos_ == 'VERB' or i.pos_ == 'AUX':
				flagVerb = True
			if i.pos_ == 'NOUN' or i.pos_ == 'PROPN':
				flagNounOrPropn = True
			m = i.i
		if flagVerb and flagNounOrPropn:
			c = m + 1
			while c < m + 3 and c < self.LENGTH:
				if self.doc[c].pos_ == 'SCONJ':
					temp = self.conj_join
					self.__analyze_conj(self.doc[c])
					if self.conj_join:
						self.conj_join = temp
						return False
					self.conj_join = temp
				if self.doc[c].pos_ == 'NUM' or self.doc[c].pos_ == 'PROPN' or self.doc[c].pos_ == 'NOUN':
					return False
				if self.doc[c].pos_ == 'VERB' or self.doc[c].pos_ == 'AUX':
					if c == m + 1:
						z = c
						while z < self.LENGTH and z < c+3:
							if self.doc[z].pos_ == 'ADJ' or self.doc[z].pos_ == 'NOUN' or self.doc[z].pos_ == 'PROPN':
								return False
							z += 1
					return True
				c += 1
		return False

	"""
	## Old function for the translation of the index
	def __transform(self):
		transformed_data = []

		if not self.data:
			raise Exception('No data to transform')
		else:
			for i_list in self.data:
				tmp = []
				for i in i_list:
					tmp.append(self.doc[i].text)
				transformed_data.append(tmp)
			return transformed_data

	"""

	def __analyze_token(self, token):

		# TODO: Aggiungere il controllo per il BoW
		if token.pos_ == 'VERB':
			self.__analyze_verb(token)

		elif token.pos_ == 'AUX':  # Bisogna controllare i "falsi ausiliari".
			if token.i + 1 < self.LENGTH and self.doc[token.i + 1].pos_ == 'VERB':
				return token.i
			else:
				# Gli ausiliari sono seguiti da un verbo, se non è così c'è un errore e quindi l'ausiliaro
				# deve essere visto come un verbo a tutti gli effetti.
				self.__analyze_verb(token)

		elif token.pos_ == 'SCONJ':
			self.__analyze_conj(token)
			return token.i + 1

		elif token.pos_ == 'NOUN':
			self.__analyze_noun(token)
			return token.i + 1

		elif token.pos_ == 'NUM':
			self.temp_data.append(token)

		elif token.pos_ == 'ADV':
			self.temp_data.append(token)

		elif token.pos_ == 'PROPN':
			self.__analyze_propn(token)
			return token.i + 1

		elif token.pos_ == 'ADJ':
			self.temp_data.append(token)

		elif token.pos_ == 'PRON':
			self.temp_data.append(token)

		elif token.pos_ == 'X':
			# Controllare se il lemma della parola è nel BoW, per ora li aggiunge, nel dubbio.
			self.temp_data.append(token)
			return token.i + 1

		else:
			return token.i + 1

		return token.i + 1


	def extract_tag(self, tag):
		token_dict = {}
		tag_split = tag.split('|')
		for single_tag in tag_split:
			val = single_tag.split('=')
			token_dict[val[0]] = val[1]
		return token_dict


	def __analyze_verb(self, token):
		tags = self.extract_tag(token.tag_)

		# if token.lemma_ != 'essere' and token.lemma_ != 'avere':
		# 		self.__reset_variables() 

		self.temp_data.append(token)

		if 'VerbForm' in tags and tags['VerbForm'] == 'Part':
			# il verbo non è completo e deve essere preceduto da un ausiliario
				if token.i - 1 > 0 and self.doc[token.i - 1].pos_ == 'AUX':
					self.temp_data.append(self.doc[token.i - 1])

		self.verb_found = True
		

	def __analyze_conj(self, token):
		if token.i + 1 < self.LENGTH and self.doc[token.i+1].pos_ == 'NOUN' or self.doc[token.i+1].pos_ == 'PROPN':
			self.conj_join = True
		elif token.i + 2 < self.LENGTH and self.doc[token.i+2].pos_ == 'NOUN' or self.doc[token.i+2].pos_ == 'PROPN':
			self.conj_join = True
		else:
			self.__reset_variables()
		

	def __analyze_noun(self, token):
		if self.verb_found or not self.temp_data or self.conj_join:
			self.temp_data.append(token)


	def __analyze_propn(self, token):

		if self.propn_list or self.verb_found or self.conj_join:
			self.temp_data.append(token)

		if token.i + 1 < self.LENGTH and self.doc[token.i + 1].pos_ == 'PROPN':
			self.propn_list = True
		else:
			self.propn_list = False