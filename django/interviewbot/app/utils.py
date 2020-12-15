from app.models import Question, QuestionFlow, Interview, InterviewType, KeyWords, MatchKeyword, CandidateUser
from app.text_analyzer import TextAnalyzer
from app.text_filter import Filter
import json
import time


class Stack():
    def __init__(self):
        self.elem = []

    def pop(self):
        if len(self.elem) <= 0:
            return None
        ret = self.elem[-1]
        del self.elem[-1]
        return ret

    def put(self, new_elem):
        if new_elem is None:
            return False
        try:
            self.elem.append(new_elem)
        except Exception:
            return False
        return True

    def get_last(self):
        if len(self.elem) <= 0:
            return None
        return self.elem[-1]

    def to_json(self):
        json_data = { 'elem' : self.elem }
        return json.dumps(json_data)
    
    def from_json(self, json_data):
        data = json.loads(json_data)
        self.elem = data['elem']
        return True



def get_next_question_v2(SA, id, answer, session):

    # Inizializzazione dello stack #
    stack = Stack()
    if session.get('stack', None) is None:
        session['stack'] = stack.to_json()
    else:
        stack.from_json(session['stack'])


    try:
        question = Question.objects.get(id=id)
        if question is None:
            return None

        if not question.is_technical:       #Se la domanda non è tecnica sono su un flusso di base quindi pulisco lo stack e lo inserisco
            stack = Stack()
            stack.put(question.id)
            session['stack'] = stack.to_json()

        next = calculate_next(stack, session, SA, question, answer)

        if type(next) is int and next == 0:  # Flusso terminato
            next_id = stack.pop()
            if next_id is None:     # Se lo stack è vuoto l'intervista è terminata
                return 0
            else:
                last_question = Question.objects.get(id = next_id) # recupero l'ultima domanda dallo stack
                session['stack'] = stack.to_json()
                next = calculate_next(stack, session, SA, last_question, answer, skip_analysis=True)  # skip_analysis mi permette di forzare l'algoritmo a cercare il next sullo
                return next                                               # stesso flusso senza attivare il SA
        else:
            return next
    except Question.DoesNotExist:
        return 0


def calculate_next(stack, session, SA, question, answer, skip_analysis = False):
    if question.type == 'check' or question.type == 'code' or not question.to_analyze or skip_analysis:
        flows = QuestionFlow.objects.all().filter(parent = question)
        if flows.exists():
            if flows.count() == 1:
                return flows.get(parent=question).son
            else:
                if answer == "" or answer is None:
                    return None
                for flow in flows:
                    if flow.choice == answer:
                        return flow.son
                for flow in flows:
                    if flow.choice == "":
                        return flow.son
                return 0
        else:
            return 0
    else:
        analyzer = TextAnalyzer(answer)
        analyze_results = analyzer.analyze()
        filter = Filter()
        filter_results = filter.execute(analyze_results)

        if not filter_results:  # Se il filtro non ha prodotto nessuna parola chiave, inutile attivare SentITA
            return calculate_next(stack, session, SA, question, answer, skip_analysis=True) # Ritorno il next del flusso corrente
        
        sentiment = SA.execute(filter_results)
        key_max = ""
        value_max = -999999999
        interview = Interview.objects.get(pk=int(session['interview_id']))
        for key in sentiment:
            print("########### VALUE:", key, "POL:", sentiment[key], "##############")
            try:
                old_match = MatchKeyword.objects.get(word=str(key), interview=interview)
                old_match.rating = float(old_match.rating) + float(sentiment[key])
                old_match.save()
            except MatchKeyword.DoesNotExist:
                new_match = MatchKeyword.objects.create(word=str(key), rating = float(sentiment[key]), interview=interview)
                new_match.save()
            except MatchKeyword.MultipleObjectsReturned:
                print('Cant save this keyword polarity cause multiple entry with same name and interview in database. Check the database instances.')

            if sentiment[key] > value_max:
                value_max = sentiment[key]
                key_max = key

        if value_max < -0.25:
            return calculate_next(stack, session, SA, question, answer, skip_analysis=True)
        
        if question.is_technical:
            stack.put(question.id)
        session['stack'] = stack.to_json()

        interviewtype = InterviewType.objects.get(pk = int(session.get('interview',1)))
        kw_question = KeyWords.objects.filter(word=key_max, interviewtype = interviewtype)[0]
        return kw_question.start_question



def get_next_question(SA, id, answer, session):

		question = Question.objects.get(id=id)
		if question is not None:
			if question.type == 'check' or question.type == 'code' or not question.to_analyze:
				if int(session.get('last_base_quest',-1)) < 0  or not session.get('have_forked', False):
					session['last_base_quest'] = id
				flows = QuestionFlow.objects.all().filter(parent=question)
				if flows.exists() and flows.count() > 0:
					if flows.count() == 1:
						return flows.get(parent=question).son
					elif not question.is_fork:
						return None
					else:
						if answer == "" or answer is None:
							return None
						for flow in flows:
							if flow.choice == answer:
								return flow.son
						for flow in flows:
							if flow.choice == "":
								return flow.son
				else:
					if not question.is_technical:
						session['last_base_quest'] = -1
					return 0
			else:
				if not session.get('have_forked', False):
					session['last_base_quest'] = id
				session['have_forked'] = True
				
				analyzer = TextAnalyzer(answer)
				analyze_results = analyzer.analyze()
				

				filter = Filter()
				filter_results = filter.execute(analyze_results)
				
				if not filter_results:
					last_id = session.get('last_base_quest', -1)
					if int(last_id) > 0:
						question = Question.objects.get(id=id)
						flows = QuestionFlow.objects.all().filter(parent=question)
						if flows.exists() and flows.count() > 0:
							if flows.count() == 1:
								return flows.get(parent=question).son
							elif not question.is_fork:
								return None
							else:
								if answer == "" or answer is None:
									return None
								for flow in flows:
									if flow.choice == answer:
										return flow.son
					else:
						return 0

				sentiment = SA.execute(filter_results)

				key_max = ""
				value_max = -999999999
				interview = Interview.objects.get(pk=int(session['interview_id']))
				for key in sentiment:
					print("########### VALUE:", key, "POL:", sentiment[key], "##############")
					try:
						old_match = MatchKeyword.objects.get(word=str(key), interview=interview)
						old_match.rating = float(old_match.rating) + float(sentiment[key])
						old_match.save()
					except MatchKeyword.DoesNotExist:
						new_match = MatchKeyword.objects.create(word=str(key), rating = float(sentiment[key]), interview=interview)
						new_match.save()
					except MatchKeyword.MultipleObjectsReturned:
						print('Cant save this keyword polarity cause multiple entry with same name and interview in database. Check the database instances.')

					if sentiment[key] > value_max:
						value_max = sentiment[key]
						key_max = key

				if value_max < -0.25:
					last_id = session.get('last_base_quest', -1)
					if int(last_id) > 0:
						question = Question.objects.get(id=id)
						flows = QuestionFlow.objects.all().filter(parent=question)
						if flows.exists() and flows.count() > 0:
							if flows.count() == 1:
								return flows.get(parent=question).son
							elif not question.is_fork:
								return None
							else:
								if answer == "" or answer is None:
									return None
								for flow in flows:
									if flow.choice == answer:
										return flow.son
					else:
						return 0
				interviewtype = InterviewType.objects.get(pk = int(session.get('interview',1)))
				kw_question = KeyWords.objects.filter(word=key_max, interviewtype = interviewtype)[0]
				return kw_question.start_question

		else:
			return None


def log(message, user=None, session=None):

    if user is not None:
        user_name = '[' + user.fristname + ' ' + user.lastname + ']'
    elif session.get('user_id', -1) > 0:
        c_user = CandidateUser.objects.get(pk=int(session['user_id']))
        user_name = '[' + c_user.fristname + ' ' + c_user.lastname + ']'
    else:
        user_name = '[Anonymous]'

    if session is not None:
        session_info = '[INT: ' + str(session.get('interview', -1)) + ' LASTQ: ' + str(session.get('last_ans_question', -1)) + 'LASTA: ' + str(session.get('last_ans_id', -1)) + ']'
    else:
        session_info = '[No session info available]'

    timestamp = '[' + str(time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())) + ']'

    log_message = timestamp + user_name + session_info + ' => ' + message
    try:
        with open('/var/www/site/logs/django.log', 'a') as logfile:
            logfile.write(log_message)
    except Exception as e:
        print('Cannot write on the file.')
        print(str(e))


    