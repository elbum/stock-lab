import datetime
import pythoncom
import win32com.client
client = win32com.client.Dispatch("XA_Session.XASession")
client.ConnectServer("demo.ebestsec.co.kr", 20001)
print(client)


query_cnt = list(filter(lambda x: (datetime.today() - x).total_seconds()))
print(query_cnt)
