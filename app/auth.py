from app.models import School


class CodeBackend(object):
    def authenticate(self, code):
        try:
            return School.objects.get(code=code)
        except School.DoesNotExist:
            return None

    def get_user(self, id):
        try:
            return School.objects.get(pk=id)
        except School.DoesNotExist:
            return None
