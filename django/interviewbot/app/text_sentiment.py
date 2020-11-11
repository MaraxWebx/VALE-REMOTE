import keras.models
from keras import backend as K
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import spacy
import os
import pickle
from pathlib import Path

class SentimentAnalyzer:

    def __init__(self):
        self.model_load_path = str(Path(__file__).resolve().parent.parent) + '/keras/'
        self.model = keras.models.load_model(self.model_load_path + 'saved_model.h5')
        self.MAX_SEQUENCE_LENGTH = 35
        self.EMBEDDING_DIM = 300
        self.MAX_N_WEMBS = 200000
        self.NB_WEMBS = self.MAX_N_WEMBS
        self.nlp = spacy.load('it_core_news_sm')
        with open(self.model_load_path + 'wemb_ind.pkl', 'rb') as f:    
            self.wemb_ind = pickle.load(f)
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

    def create_features(self, text, maxlen):
        doc = self.nlp(text)
        wemb_idxs = []
        for tok in doc:
            text_lower = tok.text.lower()
            wemb_idx = self.wemb_ind.get(text_lower, self.wemb_ind['unknown'])
            wemb_idxs.append(wemb_idx)
        wemb_idxs = pad_sequences([wemb_idxs], maxlen=maxlen, value=self.NB_WEMBS)
        return [wemb_idxs]


    def lexicon_match(self,word, lexicon):
        match = word in lexicon
        return match  


    def tok_process(self,doc):
        doc_toks = list(map(lambda x: x.text.lower(),doc))
        return doc_toks


    def create_word_list(self,texts):
        docs = list(map(lambda x:self.nlp(x), texts))
        wlist = list(map(lambda x: self.tok_process(x), docs))
        word_list = [w for sublist in wlist for w in sublist]
        return list(set(word_list))


    def process_texts(self,texts, maxlen):
        texts_feats = map(lambda x: self.create_features(x, maxlen), texts)
        return texts_feats  


    def calculate_polarity(self, sentences):
        results = []
        sentences = list(map(lambda x: x.lower(), sentences))
        #sentences = list(map(lambda x: re.sub('[^a-zA-z0-9\s]','',x), sentences))
        X_ctest = list(self.process_texts(sentences, self.MAX_SEQUENCE_LENGTH))
        n_ctest_sents = len(X_ctest)

        test_wemb_idxs = np.reshape(np.array([e[0] for e in X_ctest]), [n_ctest_sents, self.MAX_SEQUENCE_LENGTH])

        sent_model = self.model
        preds = sent_model.predict([test_wemb_idxs])
        K.clear_session()
        for i in range(n_ctest_sents):
            results.append(sentences[i] + ' - ' + 'opos: ' + str(preds[i][0]) + ' - oneg: ' + str(preds[i][1]))
            print(sentences[i],' - opos: ', preds[i][0], ' - oneg: ', preds[i][1])
        return results, preds


    def __checkwords(self, string):
        results=[]
        for word in string:
            iniziale = list(word.lemma_)[0].upper()
            if iniziale in self.data:
                for keyword in self.data[iniziale]:
                    if word.lemma_.lower() == keyword.lower():
                        results.append(word.text.lower())
        return results

    
    def execute(self, strings):
    out = []
    for string in self.strings:
        res = ""
        for word in string:
            res += word.text + ' '
        out.append(res)

    results, polarity = self.calculate_polarity(out)
    self.polarity = polarity
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
        for subj in keyword:
            if subj in self.output:
                self.output[subj] += (pos-neg)
            else:
                self.output[subj] = (pos-neg)

    return self.output

