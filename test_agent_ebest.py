import unittest
from agent.ebest import EBest
import inspect
import time


class TestEBest(unittest.TestCase):
    def setUp(self):
        self.ebest = EBest("DEMO")
        self.ebest.login()

    def test_get_code_list(self):
        print(inspect.stack()[0][3])
        all_result = self.ebest.get_code_list("ALL")
        assert all_result is not None
        kosdaq_result = self.ebest.get_code_list("KOSDAQ")
        assert all_result is not None
        kospi_result = self.ebest.get_code_list("KOSPI")
        assert all_result is not None
        try:
            error_result = self.ebest.get_code_list("KOS")
        except:
            error_result = None
        assert error_result is None
        print("result:", len(all_result), len(
            kosdaq_result), len(kospi_result))

    def test_get_stock_price_list_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_stock_price_by_code('005930', '2')
        assert result is not None
        print(result)

    def test_get_credit_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_credit_trend_by_code('005930', '20190302')
        assert result is not None
        print(result)

    def test_get_short_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_short_trend_by_code(
            '005930', sdate='20181201', edate='20181231')
        assert result is not None
        print(result)

    def test_get_agent_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_agent_trend_by_code(
            '005930', fromdt='20181201', todt='20181231')
        assert result is not None
        print(result)

    def test_get_account_info(self):
        result = self.ebest.get_account_info()
        assert result is not None
        print(result)

    def test_get_account_stock_info(self):
        result = self.ebest.get_account_stock_info()
        if result == None:
            print("Stock info nothing")
        print(result)

    def test_order_stock(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_stock("005930", "2", "45000", "2", "00")
        assert result
        print(result)

    def test_order_cancel(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_cancel("11571", "A005930", "2")
        assert result
        print(result)

    def test_order_check(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_check("11571")
        if result == None:
            print("Order info nothing")
        print(result)

    def test_get_current_call_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_current_call_price_by_code("005930")
        assert result
        return result

    # def test_get_price_n_min_by_code(self):
    #     print(inspect.stack()[0][3])
    #     result = self.ebest.get_price_n_min_by_code("20200323", "180640")
    #     assert result
    #     return result

    # def test_get_price_n_min_by_code(self):
    #     print(inspect.stack()[0][3])
    #     result = self.ebest.get_price_n_min_by_code("20200323", "005930", 0)
    #     assert result
    #     return result

    def tearDown(self):
        self.ebest.logout()


if __name__ == '__main__':
    # unittest.main()
    unittest.test_order_stock()

# test = TestEBest()
# test.setUp()
# test.tearDown()
