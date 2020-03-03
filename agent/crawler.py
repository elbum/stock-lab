from bs4 import BeautifulSoup
# from parser import html_parser
import re


class Crawler:
    def __init__(self):
        self.html_doc = """
        <html>
            <head>
                <title> Home </title>
            </head>
            <body>
                <div class="section">
                    <h2> 영역 제목 </h2>
                    <ul>
                        <li><a href="/news/news1">기사 제목1</a></li>
                        <li><a href="/news/news2">기사 제목2</a></li>
                        <li><a href="/news/news3">기사 제목3</a></li>
                    </ul>
                </div>
            </body>
        </html>
        """
        self.html_table = """
        <html>
            <div class="aside_section">
                <table class="tbl">
                    <thead>
                        <tr>
                            <th scope="col1">컬럼1</th>
                            <th scope="col2">컬럼2</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th><a href="/aside1">항목1</a></th>
                            <td>항목1값1</td>
                            <td>항목1값2</td>
                        </tr>
                        <tr>
                            <th><a href="aside2">항목2</a></th>
                            <td>항목2값1</td>
                            <td>항목2값2</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </html>
        """

    def get_news_section(self):
        soup = BeautifulSoup(self.html_doc, 'html.parser')
        print(soup.prettify())
        print('title=>', soup.title)

        print('title.string=>', soup.title.string)

        print('title parent name=>', soup.title.parent.name)

        print('div=>', soup.div)

    def get_side(self):
        soup = BeautifulSoup(self.html_table, 'html.parser')
        # print('table', soup.table)
        print('thead th', soup.thead.find_all(href=re.compile('/aside1')))

        col_list = [col.string for col in soup.thead.find_all(
            scope=re.compile('col'))]
        print('col_list =>', col_list)

        tr_list = soup.tbody.find_all('tr')
        print('tr_list =>', tr_list)

        for tr in tr_list:
            for td in tr.find_all('td'):
                print('tr td.string=>', td.string)


if __name__ == '__main__':
    crawler = Crawler()
    # crawler.get_news_section()
    crawler.get_side()
