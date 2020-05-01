from util.database_engine import DatabaseEngine
import numpy as np


def simple_compare(f1, f2, threshold=0.8):
    dist = np.sum(np.square(f1 - f2))
    if dist < threshold:
        return True
    return False


class RetrieveEngine:
    def __init__(self, db_engine, cmp=simple_compare):
        self.db_engine = db_engine
        self.cmp = cmp

    def research_in_group(self, group_id, feature):
        user_list = self.db_engine.get_retrieve_user(group_id)
        for x in user_list:
            if self.cmp(x['feature'], feature):
                return x
        return None

    @staticmethod
    def get_simple_instance():
        database = DatabaseEngine()
        return RetrieveEngine(database)
