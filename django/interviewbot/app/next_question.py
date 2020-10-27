from app.models import Question

class QuestionServer():
    dictlist_questions = []
    is_init = False

    def __init__(self):
        qs_question = Question.objects.all().order_by('id')

        for question in qs_question:
            self.dictlist_questions.append({
                'type'      :   question.type,
                'action'    :   question.action,
                'length'    :   question.length,
                'choices'   :   question.choices
            })
        
        self.is_init = True

    def get(self, question_id):
        if not self.is_init:
            return 'Not initialized'
        if question_id >=0 and question_id < len(self.dictlist_questions):
            return self.dictlist_questions[question_id]
        return 'Invalid index input'

def get_next_question():
    return 4

if __name__ == '__main__':
    get_next_question()