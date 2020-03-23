import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from agent.ebest import EBest
from db_handler.mongodb_handler import MongoDBHandler
from multiprocessing import Process

ebest_demo = EBest("DEMO")
ebest_demo.login()
mongo = MongoDBHandler()


def run_rpocess_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list,))
    p.start()
    p.join()
    print("run process join")


def check_buy_completed_order(code):
    buy_completed_order = list(mongo.find_items({"$and": [
        {"code": code}, {"status": "buy_completed"}]}, "stocklab_demo", "order"))
