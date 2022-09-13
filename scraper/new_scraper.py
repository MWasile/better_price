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
        self.user_search = user_ebook
        self.email_case = {'email': user_email, 'price': user_price, 'model_id': email_case_model_id}
        self.scrap_type = self._own_type(scrap_type)
        self.scrap_model = self._pin_model()
        self.tasks = self._pin_task()

    def _own_type(self, user_scrap_type):
        # TODO: validates user input / set type
        return user_scrap_type

    def _pin_model(self):
        # TODO: create core model
        return 'model_id'

    def _pin_task(self):
        # TODO: Create list with task class object
        return '[classTaskObj]'

    def run_task(self):
        # TODO: pass all tasks to celery worker
        return '?'

    @classmethod
    def create_email_task(cls):
        # TODO: create core model, wihout instant web scrap
        return 'model_id'


class ScrapEnginge:
    # like v1
    pass
