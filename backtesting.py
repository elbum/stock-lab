from multiprocessing import Process
import time
from datetime import datetime, timedelta
import inspect

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler

from agent.ebest import EBest
from agent.data import Data
from db_handler.mongodb_handler import MongoDBHandler

ebest_ace = EBest("ACE")
ebest_ace.login()
mongo = MongoDBHandler()


def run_process_trading_scenario(codel_list, date):
    p = Process(target=run_trading_scenario, args=(code_list, date))
    p.start()
    p.join()
    print("run process join")


def run_trading_scenario(code_list, date):
    tick = 0
