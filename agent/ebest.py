import configparser
import win32com.client
import pythoncom
from datetime import datetime
import time


class XASession:
    login_state = 0

    def OnLogin(self, code, msg):
        if code == "0000":
            print('Login Success..')
            print(code, msg)
            XASession.login_state = 1
        else:
            print(code, msg)

    def OnDisconnect(self):
        print('Session Disconnected.')
        XASession.login_state = 0


class EBest:
    QUERY_LIMIT_10MIN = 200
    LIMIT_SECONDS = 600   # 10min

    def __init__(self, mode=None):
        if mode not in ['PROD', 'DEMO']:
            raise Exception("Need to run_mode PROD or DEMO")

        run_mode = "EBEST_"+mode
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.user = config[run_mode]['user']
        self.passwd = config[run_mode]['password']
        self.cert_passwd = config[run_mode]['cert_passwd']
        self.host = config[run_mode]['host']
        self.port = config[run_mode]['port']
        self.account = config[run_mode]['account']

        self.xa_session_client = win32com.client.DispatchWithEvents(
            "XA_Session.XASession", XASession)

        self.query_cnt = []

    def login(self):
        self.xa_session_client.ConnectServer(self.host, self.port)
        self.xa_session_client.Login(
            self.user, self.passwd, self.cert_passwd, 0, 0)
        while XASession.login_state == 0:
            pythoncom.PumpWaitingMessages()

    def logout(self):
        XASession.login_state = 0
        self.xa_session_client.DisconnectServer()

    def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields):
        time.sleep(1)
        print("current query cnt :", len(self.query_cnt))
        print(res, in_block_name, out_block_name)
        while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
            time.sleep(1)
            print("waiting for execute query... current query cnt:",
                  len(self, query_cnt))
            self.query_cnt = list(
                filter(lambda x: (datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))

        xa_query = win32com.client.DispatchWithEvents(
            "XA_DataSet.XAQuery", XAQuery)
        xa_query.LoadFromResFile(XAQuery.RES_PATH+res+'.res')

        # in block
        for key, value in set_fields.items():
            xa_query.SetFieldData(in_block_name, key, 0, value)
        errorCode = xa_query.Request(0)

        #request and wait
        waiting_cnt = 0
        while xa_query.tr_run_state == 0:
            waiting_cnt += 1
            if waiting_cnt % 100000 == 0:
                print("Waiting...", self.xa_session_client.GetLastError())
            pythoncom.PumpWaitingMessages()

        # result
        result = []
        count = xa_query.GetBlockCount(out_block_name)

        for i in range(count):
            item = {}
            for field in out_fields:
                value = xa_query.GetFieldData(out_block_name, field, i)
                item[field] = value
            result.append(item)

        # time restrict
        XAQuery.tr_run_state = 0
        self.query_cnt.append(datetime.today())

        # 영문필드 -> 한글필드
        for item in result:
            for field in list(item.keys()):
                if getattr(Field, res, None):
                    res_field = getattr(Field, res, None)
                    if out_block_name in res_field:
                        field_hname = res_field[out_block_name]
                        if field in field_hname:
                            item[field_hname[field]] = item[field]
                            item.pop(field)
        return result

    def get_code_list(self, market=None):
        # 코스피 코스닥 종목리스트 가져옴
        # market 0 전체 , 1 코스피 , 2 코스닥

        if market != "ALL" and market != "KOSPI" and market != "KOSDAQ":
            raise Exception("Need to market param(ALL,KOSPI,KOSDAQ")

        market_code = {"ALL": "0", "KOSPI": "1", "KOSDAQ": "2"}
        in_params = {"gubun": market_code[market]}
        out_params = ['hname', 'shcode', 'expcode',
                      'etfgubun', 'memedan', 'gubun', 'spac_gubun']
        result = self._execute_query(
            "t8436", "t8436InBlock", "t8436OutBlock", *out_params, **in_params)
        return result


class XAQuery:
    RES_PATH = 'C:\\eBEST\\xingAPI\\Res\\'
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnreceiveMessage", error, code, message)
