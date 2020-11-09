
class SentimentAnalyzer:

	def __init__(self, strings, polarity, bow):
		self.strings = strings
		self.polarity = polarity
		self.bow = bow
		self.analysis = self.__analyze()


	def __analyze(self):
		self.output = {}

		i=-1
		for doc in self.strings:
			i+=1

			keyword = self.__checkwords(doc)
			if not keyword:
				continue

			sent = self.polarity[i]

			pos = sent[0]
			neg = sent[1]
			"""
			while pos < 1 and neg < 1:
				pos *= 10
				neg *= 10
			"""
			for subj in keyword:

				if subj in self.output:
					self.output[subj] += (pos-neg)
				else:
					self.output[subj] = (pos-neg)
				
				"""
				if neg - pos > 0.5:
					if subj in self.output:
						self.output[subj] -=1
					else:
						self.output[subj] = -1
				elif pos - neg > 0.5:
					if subj in self.output:
						self.output[subj] +=1
					else:
						self.output[subj] = +1
				else:
					if subj in self.output:
						self.output[subj] +=0
					else:
						self.output[subj] = 0
				"""
		return self.output

	def get_analysis(self):
		return self.analysis

	def __checkwords(self, string):
		results=[]
		for word in string:
			iniziale = list(word.lemma_)[0].upper()
			if iniziale in self.bow:
				for keyword in self.bow[iniziale]:
					if word.lemma_.lower() == keyword.lower():
						results.append(word.text)
		return results


	def __find_subj(self, string):
		result = ""
		for word in string:
			if word.pos_ == 'PROPN' or word.pos_ == 'NOUN':
				result += word.text + ' '
		return result
