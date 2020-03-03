import unittest
from agent.data import Data
import inspect
import time


class TestEBest(unittest.TestCase):
    def setUp(self):
        self.data = Data()

    # def test_get_corp_code(self):
    #     print(inspect.stack()[0][3])
    #     result = self.data.get_corp_code(name='삼성전자')
    #     assert result is not None
    #     print(result)

    def test_get_corp_info(self):
        print(inspect.stack()[0][3])
        result = self.data.get_corp_info(code='593')
        assert result is not None
        print(result)

    # def test_get_stk_distribution_info(self):
    #     print(inspect.stack()[0][3])
    #     result = self.data.get_stk_distribution_info(
    #         code='593', date='20181231')
    #     assert result is not None
    #     print(result)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
