import random
import pandas as pd

career_data = pd.read_excel(open('career_info.xlsx', 'rb'))

class BaseCareer:
    def __init__(self):
        self.path = str()
        self.jobs = dict()
        self.first_job = None

    def update(self):
        pass

    def set_jobs(self):
        columns = list(career_data)

        def check_path():
            if career_data['Path'][ind] == self.path:
                job = dict()

                for column in columns:
                    job.update({column: career_data[column][ind]})

                self.jobs.update({f'{self.path}_{job["Name"]}': job})

        for ind in career_data.index:
            check_path()

    def set_first_job(self):
        return random.choice([{key: value} for key, value in self.jobs.items() if value['Level'] == 1])


class FinanceCareer(BaseCareer):
    def __init__(self):
        super().__init__()
        self.path = "Finance"
        self.set_jobs()
        self.first_job = self.set_first_job()


class CulinaryCareer(BaseCareer):
    def __init__(self):
        super().__init__()
        self.path = "Culinary"
        self.set_jobs()
        self.first_job = self.set_first_job()
