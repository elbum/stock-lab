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
                  len(self.query_cnt))
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

    def get_account_info(self):
        in_params = {"RecCnt": 1, "AcntNo": self.account, "Pwd": self.passwd}
        out_params = ["MnyOrdAbleAmt", "BalEvalAmt",
                      "DpsastTotamt", "InvstOrgAmt", "InvstPlamt", "Dps"]
        result = self._execute_query(
            "CSPAQ12200", "CSPAQ12200InBlock1", "CSPAQ12200OutBlock2", *out_params, **in_params)
        return result

    def get_account_stock_info(self):
        # 현물계좌 잔고정보조회
        in_params = {"RecCnt": 1, "AcntNo": self.account, "Pwd": self.passwd, "BalCreTp": "0",
                     "CmsnAppTpCode": "0", "D2balBaseQryTp": "0", "UprcTpCode": "0"}
        out_params = ["IsuNo", "IsuNm", "BalQty", "SellPrc",
                      "BuyPrc", "NowPrc", "AvrUprc", "BalEvalAmt", "PrdayCprc"]
        result = self._execute_query(
            "CSPAQ12300", "CSPAQ12300InBlock1", "CSPAQ12300OutBlock3", *out_params, **in_params)

    def order_stock(self, code, qty, price, bns_type, order_type):
        # 현물주문
        # bns_type : 1 매도 , 2 매수
        # order_type : 00 지정가 , 03 시장가 , 05 조건부시장가 , 07 최우선지정가
        #              61 장개시전시간외종가 , 81 시간외종가 , 82 시간외단일가
        in_params = {"AcntNo": self.account, "InptPwd": self.passwd, "IsuNo": code, "OrdQty": qty,
                     "OrdPrc": price, "BnsTpCode": bns_type, "OrdprcPtnCode": order_type}
        out_params = ["OrdNo", "OrdTime", "OrdMktCode", "OrdPtnCode", "ShtnIsuNo", "MgemNo",
                      "OrdAmt", "SpotOrdQty", "IsuNm"]
        result = self._execute_query(
            "CSPAT00600", "CSPAT00600InBlock1", "CSPAT00600OutBlock2", *out_params, **in_params)
        return result

    def order_cancel(self, order_no, code, qty):
        # 주문취소
        in_params = {"OrgOrdNo": order_no, "AcntNo": self.account,
                     "InptPwd": self.passwd, "IsuNo": code, "OrdQty": qty}
        out_params = {"OrdNo", "PrntOrdNo", "OrdTime", "OrdPtnCode", "IsuNm"}
        result = self._execute_query(
            "CSPAT00800", "CSPAT00800InBlock1", "CSPAT00800OutBlock2", *out_params, **in_params)
        return result

    def order_check(self, order_no):
        # (체결/미체결) 주문조회
        in_params = {"accno": self.account, "passwd": self.passwd, "expcode": "", "chegb": "0", "medosu": "0",
                     "sortgb": "1", "cts_ordno": " "}
        out_params = ["ordno", "expcode", "medosu", "qty", "price", "cheqty", "cheprice", "ordrem", "cfmqty",
                      "status", "orgordno", "ordermtd", "sysprocseq", "hogagb", "price1", "orggb", "singb", "loandt"]
        result_list = self._execute_query(
            "t0425", "t0425Inblock", "t0425OutBlock1", *out_params, **in_params)
        result = {}
        if order_no is not None:
            for item in result_list:
                if item['주문번호'] == order_no:
                    result = item
            return result
        else:
            return result_list

    def get_current_call_price_by_code(self, code=None):
        # 현재가 호가 조회
        tr_code = "t1101"
        in_params = {"shcode": code}
        out_params = ["hname", "price", "sign", "change", "diff", "volume", "jniclose", "offerho1", "bidho1", "offerem1",
                      "bidrem1", "offerho2", "bidho2", "offerrem2", "bidrem2",
                      "offerho3", "bidho3", "offerrem3", "bidrem3",
                      "offerho4", "bidho4", "offerrem4", "bidrem4",
                      "offerho5", "bidho5", "offerrem5", "bidrem5",
                      "offerho6", "bidho6", "offerrem6", "bidrem6",
                      "offerho7", "bidho7", "offerrem7", "bidrem7",
                      "offerho8", "bidho8", "offerrem8", "bidrem8",
                      "offerho9", "bidho9", "offerrem9", "bidrem9",
                      "offerho10", "bidho10", "offerrem10", "bidrem10",
                      "preoffercha10", "prebidcha", "hotime", "yeprice", "yevolume",
                      "yesign", "yechange", "yediff", "tmoffer", "tmbid", "ho_status",
                      "shchode", "uplmtprice", "dnlmtprice", "open", "high", "low"]

        result = self._execute_query(
            "t1101", "t1101InBlock", "t1101OutBlock", *out_params, **in_params)

        for item in result:
            item["code"] = code

        return result

    def get_tick_size(self, price):
        # 호가단위 조회 메서드
        if price < 1000:
            return 1
        elif price >= 1000 and price < 5000:
            return 5
        elif price >= 5000 and price < 10000:
            return 10
        elif price >= 10000 and price < 50000:
            return 50
        elif price >= 50000 and price < 100000:
            return 100
        elif price >= 100000 and price < 500000:
            return 500
        elif price >= 500000:
            return 1000


class Field:
    t1101 = {
        "t1101OutBlock": {
            "hname": "한글명",
            "price": "현재가",
            "sign": "전일대비구분",
            "change": "전일대비",
            "diff": "등락율",
            "volume": "누적거래량",
            "jiniclose": "전일종가",
            "offerho1": "매도호가1",
            "bidho1": "매수호가1",
            "offerrem1": "매도호가수량1",
            "bidrem1": "매수호가수량1",
            "uplmtprice": "상한가",
            "dnlmtprice": "하한가",
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

    CSPAQ12200 = {
        "CSPAQ12200OutBlock2": {
            "MnyOrdAbleAmt": "현금주문가능금액",
            "BalEvalAmt": "잔고평가금액",
            "InvstOrgAmt": "투자원금",
            "InvstPlamt": "투자손익금액",
            "Dps": "예수금"
        }
    }

    CSPAQ12300 = {
        "CSPAQ12300OutBlock3": {
            "IsuNo": "종목번호",
            "IsuNm": "종목명",
            "BnsBaseBalQty": "매매기준잔고수량",
            "NowPrc": "현재가",
            "AvrUprc": "평균단가"
        }
    }

    CSPAT00600 = {
        "CSPAT00600OutBlock2": {
            "RecCnt": "레코드갯수",
            "OrdNo": "주문번호",
            "OrdTime": "주문시각",
            "OrdMktCode": "주문시장코드",
            "OrdPtnCode": "주문유형코드",
            "ShtnIsuNo": "단축종목번호",
            "MgemNo": "관리사원번호",
            "OrdAmt": "주문금액",
            "SpareOrdNo": "예비주문번호",
            "CvrgSeqno": "반대매매일련번호",
            "RsvOrdNo": "예약주문번호",
            "SpotOrdQty": "실물주문수량",
            "RuseOrdQty": "재사용주문수량",
            "MnyOrdAmt": "현금주문금액",
            "SubstOrdAmt": "대용주문금액",
            "RuseOrdAmt": "재사용주문금액",
            "AcntNm": "계좌명",
            "IsuNm": "종목명"
        }
    }

    CSPAT00800 = {
        "CSPAT00800OutBlock2": {
            "RecCnt": "레코드갯수",
            "OrdNo": "주문번호",
            "PrntOrdNo": "모주문번호",
            "OrdTime": "주문시각",
            "OrdMktCode": "주문시장코드",
            "OrdPtnCode": "주문유형코드",
            "ShtnIsuNo": "단축종목번호",
            "PrgmOrdprcPtnCode": "프로그램호가유형코드",
            "StslOrdprcTpCode": "공매도호가구분",
            "StslAbleYn": "공매도가능여부",
            "MgntrnCode": "신용거래코드",
            "LoanDt": "대출일",
            "CvrgOrdTp": "반대매매주문구분",
            "LpYn": "유동성공급자여부",
            "MgemNo": "관리사원번호",
            "BnsTpCode": "매매구분",
            "SpareOrdNo": "예비주문번호",
            "CvrgSeqno": "반대매매일련번호",
            "RsvOrdNo": "예약주문번호",
            "AcntNm": "계좌명",
            "IsuNm": "종목명"
        }
    }

    t0425 = {
        "t0425OutBlock1": {
            "ordno": "주문번호",
            "expcode": "종목번호",
            "medosu": "구분",
            "qty": "주문수량",
            "price": "주문가격",
            "cheqty": "체결수량",
            "cheprice": "체결가격",
            "ordrem": "미체결잔량",
            "cfmqty": "확인수량",
            "status": "상태",
            "orgordno": "원주문번",
            "ordgb": "유형",
            "ordtime": "주문시간",
            "ordermtd": "주문매체",
            "sysprocseq": "처리순번",
            "hogagb": "호가유형",
            "price1": "현재가",
            "orggb": "주문구분",
            "singb": "신용구분",
            "loandt": "대출일자"
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
