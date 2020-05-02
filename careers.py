import random
import pandas as pd

career_data = pd.read_excel(open('career_info.xlsx', 'rb'))

class BaseCareer:
    def __init__(self):
        self.path = str()
        self.jobs = dict()
        self.career_path = dict()

    def update(self):
        pass

    def find_jobs(self):
        columns = list(career_data)

        def check_path():
            if career_data['Path'][ind] == self.path:
                job = dict()

                for column in columns:
                    job.update({column: career_data[column][ind]})

                self.jobs.update({f'{self.path}_{job["Name"]}': job})

        for ind in career_data.index:
            check_path()

    def set_career_path(self):
        level = 0
        job_dict = dict()

        for i in self.jobs:
            if level < 10:
                level += 1
                job = random.choice([{key: value} for key, value in self.jobs.items() if value['Level'] == level])
                job_dict.update({level: job})
                

        return job_dict


class FinanceCareer(BaseCareer):
    def __init__(self):
        super().__init__()
        self.path = "Finance"
        self.find_jobs()


class CulinaryCareer(BaseCareer):
    def __init__(self):
        super().__init__()
        self.path = "Culinary"
        self.find_jobs()


class LawCareer(BaseCareer):
    def __init__(self):
        super().__init__()
        self.path = "Law"
        self.find_jobs()