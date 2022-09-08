from django.contrib import admin

from quiz_app import models

admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.UserAnswer)
admin.site.register(models.UserQuiz)
