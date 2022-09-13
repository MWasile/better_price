from scraper.models import FastTaskInfo, EmailTaskInfo
from django.core.exceptions import ValidationError

class Task:
    def __init__(self, user_ebook, owner_model_id):
        self.user_ebook = user_ebook
        self.owner_model_id = owner_model_id
        self.web_data = {}  #
        self.data_auto_save = {}

    @property
    def data_auto_save(self):
        return self._data_auto_save

    @data_auto_save.setter
    def data_auto_save(self, data_from_website):
        own_save = self._db_save(data_from_website)
        if own_save:
            self._data_auto_save = data_from_website

    def _db_save(self, data_to_save):
        # TODO: save to db, reorganize models
        return True


class FastScrapMixin:
    # inh -> (Task, BookstoreClass)
    # nothing else?
    pass


class EmailScrapMixin:
    # inh -> (Task, BookstoreClass)
    # format price str -> , . zł
    # compare web price - user pirce
    # overwrite

    pass


class TaskFactory:
    # like v1
    pass


class TaskManager(TaskFactory):
    """
    ONLY!!!!:
        1. Run fast scrap
        2. Run fast scrap based on earlier set email task
        3. Set email task without instant scrap
    """

    def __init__(self, scrap_type, user_ebook, user_email=None, user_price=None, email_case_model_id=None):
        self.user_ebook = user_ebook
        self.email_case = {'email': user_email, 'price': user_price, 'model_id': email_case_model_id}
        self.scrap_type = self._own_type(scrap_type)
        self.scrap_model = self._pin_model()
        self.tasks = self._pin_task()

    def _own_type(self, user_input_type):

        if user_input_type.lower() not in ['email', 'fast']:
            raise ValueError(f'task_type must be "email" or "fast", not {user_input_type}')

        if user_input_type.lower() == 'email':
            if not self.email_case['email']:
                raise ValueError('In email task, parameter user_email is required.')
            if not self.email_case['price']:
                raise ValueError('In email task, parameter user_price is required.')
            if not self.email_case['model_id']:
                raise ValueError('In email task, parameter email_case_model_id is required.')
            return user_input_type

        return user_input_type


        return user_scrap_type

    def _pin_model(self):
        if self.email_case['model_id']:
            # Task Email already has model created before, so escape.
            return self.email_case['model_id']

        if not self.user_ebook:
            return None

        new_info_model = FastTaskInfo(
            task_type=self.scrap_type,
            user_ebook=self.user_ebook
        )

        try:
            new_info_model.full_clean()
            new_info_model.save()
        except ValidationError:
            return None

        return new_info_model.id

    def _pin_task(self):
        # TODO: Create list with task class object
        return '[classTaskObj]'

    def run_task(self):
        # TODO: pass all tasks to celery worker
        return '?'

    @classmethod
    def create_email_task(cls):
        return 'model_id'


class ScrapEnginge:
    # like v1
    pass
