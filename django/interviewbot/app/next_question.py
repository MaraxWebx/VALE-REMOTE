from app.models import Question

class QuestionServer():
    dictlist_questions = []
    is_init = False

    def __init__():
        qs_question = Question.objects.all().order_by('id')

        for question in qs_question:
            dictlist_questions.append({
                'type'      :   question.type
                'action'    :   question.action
                'length'    :   question.length
                'choices'   :   question.choices
            })
        
        is_init = True

    def get(question_id):
        if not is_init:
            return 'Not initialized'
        if question_id >=0 and question_id < len(dictlist_questions):
            return dictlist_questions[question_id]
        return 'Invalid index input'

def get_next_question():
    return 4

if __name__ == '__main__':
    get_next_question()