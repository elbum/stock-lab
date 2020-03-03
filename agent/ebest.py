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

    def get_stock_price_by_code(self, code=None, cnt="1"):
        in_params = {"shcode": code, "dwmcode": "1",
                     "date": "", "idx": "", "cnt": cnt}
        out_params = ['date', 'open', 'high', 'low', 'close', 'sign', 'change', 'diff', 'volume',
                      'diff', 'volume', 'diff_vol', 'chdegree', 'sojinrate', 'changerate', 'fpvolume', 'covolume',
                      'value', 'ppvolume', 'o_sign', 'o_change', 'o_diff',
                      'h_sign', 'h_change', 'h_diff', 'l_sign', 'l_change',
                      'l_diff', 'marketcap']
        result = self._execute_query(
            't1305', 't1305InBlock', 't1305OutBlock1', *out_params, **in_params)
        for item in result:
            item['code'] = code
        return result

    def get_credit_trend_by_code(self, code=None, date=None):
        # t1921 신용거래 동향
        in_params = {"shcode": code, "gubun": 0, 'date': date, 'idx': '0'}
        out_params = ['mmdate', 'close', 'sign', 'jchange', 'diff', 'nvolume',
                      'svolume', 'jvolume', 'price', 'change', 'gyrate', 'jkrate', 'shcode']
        result = self._execute_query(
            't1921', 't1921InBlock', 't1921OutBlock1', *out_params, **in_params)
        for item in result:
            item['code'] = code
        return result

    def get_agent_trend_by_code(self, code=None, fromdt=None, todt=None):
        # t1717 외인기관 종목동향
        in_params = {'gubun': 0, 'fromdt': fromdt,
                     'todt': todt, 'shcode': code}
        out_params = ['date', 'close', 'sign', 'change', 'diff', 'volume',
                      'tjj0000_vol', 'tjj0001_vol', 'tjj0002_vol', 'tjj0003_vol',
                      'tjj0004_vol', 'tjj0005_vol', 'tjj0006_vol', 'tjj0007_vol',
                      'tjj0008_vol', 'tjj0009_vol', 'tjj0010_vol', 'tjj0011_vol',
                      'tjj0018_vol', 'tjj0016_vol', 'tjj0017_vol', 'tjj0001_dan',
                      'tjj0002_dan', 'tjj0003_dan', 'tjj0004_dan', 'tjj0005_dan',
                      'tjj0006_dan', 'tjj0007_dan', 'tjj0008_dan', 'tjj0009_dan',
                      'tjj0010_dan', 'tjj0011_dan', 'tjj0018_dan', 'tjj0016_dan',
                      'tjj0017_dan']
        result = self._execute_query(
            't1717', 't1717InBlock', 't1717OutBlock', *out_params, **in_params)
        for item in result:
            item['code'] = code
        return result

    def get_short_trend_by_code(self, code=None, sdate=None, edate=None):
        # t1927 공매도일별추이
        in_params = {'date': sdate, 'sdate': sdate,
                     'edate': edate, 'shcode': code}
        out_params = ['date', 'price', 'sign', 'change', 'diff', 'volume', 'value',
                      'gm_vo', 'gm_va', 'gm_per', 'gm_avg', 'gm_avg', 'gm_vo_sum']
        result = self._execute_query(
            't1927', 't1927InBlock', 't1927OutBlock1', *out_params, **in_params)
        for item in result:
            item['code'] = code
        return result


class Field:
    t1101 = {
        "t1101OutBlock": {
            "hname": "한글명",
            "price": "현재가",
            "sign": "전일대비구분",
            "open": "시가",
            "high": "고가",
            "low": "저가"
        }
    }
    t1305 = {
        "t1305OutBlock1": {
            "date": "날짜",
            "open": "시가",
            "volume": "누적거래량",
            "marketcap": "시가총액"
        }
    }
    t1921 = {
        "t1921OutBlock1": {
            "mmdate": "날짜",
            "close": "종가",
            "sign": "전일대비구분",
            "shcode": "종목코드"
        }
    }

    t8436 = {
        "t8436OutBlock": {
            "hname": "종목명",
            "shcode": "단축코드",
            "expcode": "확장코드",
            "spac_gubun": "기업인수목적회사여부",
            "filler": "filler(미사용)"
        }
    }

    t1717 = {
        "t1717OutBlock": {
            "date": "일자",
            "close": "종가",
            "tjj0017_dan": "기다계(단가)(기타)+국가)"
        }
    }

    t1927 = {
        "t1927OutBlock1": {
            "date": "일자",
            "price": "현재가",
            "gm_vo_sum": "누적공매도수량"
        }
    }

    t0425 = {
        "t0425OutBlock1": {
            "ordno": "주문번호",
            "expcode": "종목번호",
            "medosu": "구분",
            "qty": "주문수량",
            "price": "주문가격",
            "loandt": "대출일자"
        }
    }

    t8412 = {
        "t8412OutBlock1": {
            "date": "날짜",
            "time": "시간",
            "sign": "종가등락구분"
        }
    }

    CSPAQ12200 = {
        "CSPAQ12200OutBlock2": {
            "RecCnt": "레코드갯수",
            "BrnNm": "지점명",
            "MnyOrdAbleAmt": "현금주문가능금액",
            "DpslRestrcAmt": "처분제한금액"
        }
    }

    CSPAQ12300 = {
        "CSPAQ12300OutBlock2": {
            "RecCnt": "레코드갯수",
            "BrnNm": "지점명",
            "MnyOrdAbleAmt": "현금주문가능금액",
            "LoanAmt": "대출금액"
        },
        "CSPAQ12300OutBlock3": {
            "IsuNo": "종목번호",
            "IsuNm": "종목명",
            "SecBalPtnCode": "유가증권잔고유형코드",
            "SecBalPtnNm": "유가증권잔고유형명",
            "BalQty": "잔고수량",
            "DpspdgLoanQty": "예탁담보대출수량"
        }
    }

    CSPAQ13700 = {
        "CSPAQ13700OutBlock3": {
            "OrdDt": "주문일",
            "MgmtBrnNo": "관리지점번호",
            "OdrrId": "주문자ID"
        }
    }

    CSPAT00600 = {
        "CSPAT00600OutBlock1": {
            "RecCnt": "레코드갯수",
            "ActNo": "계좌번호",
            "InptPwd": "입력비밀번호",
            "IsuNo": "종목번호",
            "CvrgTpCode": "반대매매구분"
        },
        "CSPAT00600OutBlock2": {
            "RecCnt": "레코드갯수",
            "OrdNo": "주문번호",
            "OrdTime": "주문시각",
            "AcntNm": "계좌명",
            "IsuNm": "종목명"
        }
    }

    CSPAT00800 = {
        "CSPAT00800OutBlock2": {
            "RecCnt": "레코드갯수",
            "OrdNo": "주문번호",
            "PrntOrdNo": "모주문번호",
            "IsuNm": "종목명"
        }
    }


class XAQuery:
    RES_PATH = 'C:\\eBEST\\xingAPI\\Res\\'
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnreceiveMessage", error, code, message)
