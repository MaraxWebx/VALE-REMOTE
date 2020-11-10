from sentita import calculate_polarity

class SentimentAnalyzer:

	def __init__(self, bow):
		self.bow = bow

	def analyze(self, strings):
		out = []
		for string in strings:
			res = ""
			for word in string:
				res += word.text + ' '
			out.append(res)
			
		result2, polarity = calculate_polarity(out)
		self.polarity = polarity
		self.analysis = self.__analyze(strings)



	def __analyze(self, strings):
		output = {}

		i=-1
		for doc in strings:
			i+=1

			keyword = self.__checkwords(doc)
			if not keyword:
				continue

			sent = self.polarity[i]

			pos = sent[0]
			neg = sent[1]

			for subj in keyword:

				if subj in output:
					output[subj] += (pos-neg)
				else:
					output[subj] = (pos-neg)
				
		return output

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
