from django.core.management.base import BaseCommand, CommandError
from app.models import CandidateUser, Answer
import os

class Command(BaseCommand):
    help = 'Delete all existing file in media directory that are not present anymore in the database.'

    def handle(self, *args, **options):
        dir = '/var/www/media'
        user_folder = '/user_cvs'
        video_folder = '/videos'
        ### Get all present information from the database ###

        answers = Answer.objects.all().filter(choice_vid__isnull=False)
        users = CandidateUser.objects.all().filter(cv__isnull=False)

        ## Save only the file name to a list for avoid making a query for each file ##
        vids = []
        for answer in answers:
            vids.append(str(answer.choice_vid))
        
        cvs = []
        for user in users:
            cvs.append(str(user.cv))


        for filename in os.listdir(dir + user_folder):
            flag = False
            for cv in cvs:
                if cv.endswith(filename):
                    flag = True
                    break
            if not flag:
                # os.remove(dir + user_folder + '/' + filename)
                self.stdout.write(self.style.SUCCESS('This cv will be deleted: %s' % filename))

        for filename in os.listdir(dir + video_folder):
            flag = False
            for vid in vids:
                if vid.endswith(filename):
                    flag = True
                    break
            if not flag:
                # os.remove(dir + video_folder + '/' + filename)
                self.stdout.write(self.style.SUCCESS('This video will be deleted: %s' % filename))
        