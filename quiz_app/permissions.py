from django.contrib.auth import mixins as django_auth_mixins
from django.shortcuts import redirect

# from quiz_app import models


class RedirectPermissionRequiredPermission(django_auth_mixins.PermissionRequiredMixin):
    def handle_no_permission(self):
        return redirect('list_of_quizzes')


# class IsThisQuizNotADraftPermission:
#     def dispatch(self, request, *args, **kwargs):
#         if (isinstance(self.get_object(), models.Quiz) and not self.get_object().is_draft) or\
#                 (isinstance(self.get_object(), models.Question) and not self.get_object().quiz.is_draft):
#             return redirect('list_of_quizzes')
#         return super().dispatch(request, *args, **kwargs)


