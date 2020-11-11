import it_core_news_md
import json
import time
from app.model import KeyWords

class Filter:

	def __init__(self):
		self.nlp = it_core_news_md.load()
		keyword = KeyWords.object.all()
		self.data = {}
		for word in keyword:
			self.__add_data(word.word)

	def __add_data(self, string=""):
		if string == "":
			print("Can't add empty string.")
			return
		doc = self.nlp(string)
		string = doc[0].lemma_
		iniziale = list(string)[0].upper()
		if iniziale in self.data:
			self.data[iniziale].append(string)
		else:
			self.data[iniziale] = [string]

	def __check_string(self, string):
		iniziale = list(string.lemma_)[0].upper()
		if iniziale in self.data:
			for word in self.data[iniziale]:
				if string.lemma_ == word:
					return True
		return False

	def __tokenize(self, strings):
		lemmatized_strings = []
		for string in strings:
			doc = self.nlp(' '.join(string))
			lemmatized_strings.append(doc)
		return lemmatized_strings


	def execute(self, strings=None, as_string=False):
		if strings is None:
			print('No strings for input. Insert a list of string as paramenter')
			return
		self.starttime = time.time_ns() // 1000000
		self.output = []
		#tokenized_strings = self.__tokenize(strings)
		for string in strings:
			is_rilevant = False
			contain_verb = False
			contain_noun = False
			contain_propn = False
			contain_num = False


			for word in string:
				if word.pos_== 'VERB' or word.pos_== 'AUX':
					contain_verb 	= True

				if word.pos_== 'NOUN':
					contain_noun 	= True

				if word.pos_== 'PROPN':
					contain_propn 	= True

				if word.pos_ == 'NUM':
					contain_num 	= True

				if self.__check_string(word):
					is_rilevant = True
					break

			if len(string) > 2 and not is_rilevant:		# non contiene parole chiave, vediamo se ha senso
				if contain_verb:
					if contain_noun or contain_propn or contain_num:
						is_rilevant = True

			if is_rilevant:
				self.output.append(string)
		self.endtime = time.time_ns() // 1000000
		if as_string:
			return self.get_results_as_string(self.output)
		return self.output


	def get_benchmark(self):
		return str(self.endtime - self.starttime)

	def get_results_as_string(self, data):
		data = []
		for result in data:
			res = ""
			for word in result:
				res += word.text + ' '
			data.append(res)
		return data