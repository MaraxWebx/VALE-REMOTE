import it_core_news_md
import json
import time

class Filter:

	def __init__(self, path=None, read=False):
		if path is None:
			print('No datapath specified, default = "file.json"')
			self.datapath = 'file.json' # default directory
		else:
			self.datapath = path
		self.data_exists = False

		if read:
			try:
				with open(self.datapath , 'r') as read_file:
					self.data = json.load(read_file)
					self.data_exists = True
					print('Data load successfully')
			except:
				print("File data doesn't exists in the specified path.")
				self.data_exists = False
				self.data = None

		self.nlp = it_core_news_md.load()


	def change_path(self, path=None):
		if path is None:
			print('Specify a path.')
			return
		self.datapath = path
		print('New path:', path)


	def read_data(self):
		try:
			with open(self.datapath , 'r') as read_file:
				self.data = json.load(read_file)
				self.data_exists = True
				print('Data load successfully')
		except:
			print("File data doesn't exists in the specified path. Change it with command change_path(path).")
			self.data_exists = False


	def add_data(self, string=""):
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


	def get_data(self, print_result=False):
		if print_result:
			print('Current data:')
			for letter in self.data:
				print("\n" + letter + ":")
				for word in self.data[letter]:
					print(word)

		return self.data


	def flush(self):
		if self.data_exists:
			with open(self.datapath, 'w') as write_file:
				json.dump(self.data, write_file)

	def get_bow(self):
		return self.data

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


	def execute(self, strings=None):
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
		return self.output


	def get_benchmark(self):
		return str(self.endtime - self.starttime)

	def get_results_as_string(self):
		out = []
		for result in self.output:
			res = ""
			for word in result:
				res += word.text + ' '
			out.append(res)
		return out