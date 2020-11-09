from app.text_analyzer import TextAnalyzer
from app.text_filter import Filter
from app.text_sentiment import SentimentAnalyzer
import time

class Controller:
	def __init__(self, bow_path=None):
		print('Starting controller...\n- Starting analyzer')
		self.analyzer = TextAnalyzer()
		print('\tAnalyzer is ready')
		print('- Starting filter')
		if bow_path is None:
			print('\tBoW path not specified, run without initializing the data.')
			self.filter = Filter(read=True)
		else:
			print('\tBow path specified. Starting filter')
			self.filter = Filter(path=bow_path, read=True)

		print('\tFilter is ready')

	
	def analyze(self, corpus=None):

		if corpus is None:
			print('Specify corpus text.')
			return

		self.analyzer.put(corpus)

		analyzed_data = self.analyzer.analyze()

		filtered_data = self.filter.execute(analyzed_data)

		sentiment = SentimentAnalyzer(filtered_data, self.filter.get_bow())

		self.results = sentiment.get_analysis()

		print(sentiment.get_analysis())
