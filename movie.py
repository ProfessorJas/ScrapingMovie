import urllib.request
from urllib import parse
from lxml import etree
import ssl
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QTextEdit, QVBoxLayout, QPushButton, QMessageBox
import sys

# 取消代理验证
ssl._create_default_http_context = ssl._create_unverified_context

class TextEditMeiJu(QWidget):
    def __init__(self, parent=None):
        super(TextEditMeiJu, self).__init__(parent)

        # 定义窗口头部消息
        self.setWindowTitle('美剧天堂')

        # set the size
        self.resize(500, 600)

        # create a single-line text area
        self.textLineEdit = QLineEdit()

        # create a button
        self.btnButton = QPushButton('Go!')

        # create a mutli-line textaarea
        self.textEdit = QTextEdit()

        # instantiate layout
        layout = QVBoxLayout()

        # add the component to the layout
        layout.addWidget(self.textLineEdit)
        layout.addWidget(self.btnButton)
        layout.addWidget(self.textEdit)

        # set the layout
        self.setLayout(layout)

        # bind the click action with the function
        self.btnButton.clicked.connect(self.buttonClick)

    # When you click the 'Go' button
    def buttonClick(self):
        start = QMessageBox.information(
            self, 'Prompt', '是否开始爬取《' + self.textLineEdit.text() + "》",
            QMessageBox.Ok | QMessageBox.No, QMessageBox.Ok
        )

        # 确定爬取
        if start == QMessageBox.Ok:
            self.page = 1
            self.loadSearchPage(self.textLineEdit.text(), self.page)
        else:
            pass

    # add the page after you put in the name of the TV show
    def loadSearchPage(self, name, page):
        # change the encoding to gb2312
        name = parse.quote(name.encode('gb2312'))

        # the address send the request
        url = "https://www.meijutt.com/search/index.asp?page=" + str(page) + "&searchword=" + name + "&searchtype=-1"

        # 请求报头
        headers =  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

        # send request
        request = urllib.request.Request(url, headers=headers)

        # 获取请求的 html 文档
        html = urllib.request.urlopen(request).read()

        # 对 html 文档进行解析
        text = etree.HTML(html)

        # xpath 获取想要的信息
        pageTotal = text.xpath('//div[@class="page"]/span[1]/text()')

        # check whether it has the reuslt
        if pageTotal:
            self.loadDetailPage(pageTotal, text, headers)
        else:
            self.infoSearchNull()

    # 加载点击搜索页面点击的本季页面
    def loadDetailPage(self, pageTotal, text, headers):
        # get how many pages
        pageTotal = pageTotal[0].split('/')[1].rstrip("页")

        # get the content(name and link)
        node_list = text.xpath('//a[@class="B font_14"]')

        items = {}

        items['name'] = self.textLineEdit.text()

        # Looping to get the content of each season
        for node in node_list:
            # get the infor
            title = node.xpath('@title')[0]
            link = node.xpath('@href')[0]
            items["title"] = title

            # jump to the detail page according to the link for a single season
            requestDetail = urllib.request.Request("https://www.meijutt.com" + link, headers=headers)
            htmlDetail = urllib.request.urlopen(requestDetail).read()
            textDetail = etree.HTML(htmlDetail)
            node_listDetail = textDetail.xpath('//div[@class="tabs-list current-tab"]//strong//a/@href')

            self.writeDetailPage(items, node_listDetail)

        if self.page == int(pageTotal):
            self.infoSearchDone()
        else:
            self.infoSearchContinue(pageTotal)
    
    # show the data to the GUI
    def writeDetailPage(self, items, node_listDetail):
        for index, nodeLink in enumerate(node_listDetail):
            items["link"] = nodeLink

            # display the GUI
            self.textEdit.append(
                "<div>"
                    "<font color='black' size='3'>" + items['name'] + "</font>" + "\n"
                    "<font color='red' size='3'>" + items['title'] + "</font>" + "\n"
                    "<font color='orange' size='3'>第" + str(index + 1) + "集</font>" + "\n"
                    "<font color='green' size='3'>下载链接：</font>" + "\n"
                    "<font color='blue' size='3'>" + items['link'] + "</font>"
                    "<p></p>"
                "</div>"
            )

    # no search information
    def infoSearchNull(self):
        QMessageBox.information(
            self, 'Prompt', 'Content does not exist, please search again...',
            QMessageBox.Ok, QMessageBox.Ok
        )

    # finish searching
    def infoSearchDone(self):
        QMessageBox.information(
            self, 'Prompt', '爬取《' + self.textLineEdit.text() + '》完毕',
            QMessageBox.Ok, QMessageBox.Ok
        )

    # ask whether you would like to continue if it has multiple pages
    def infoSearchContinue(self, pageTotal):
        end = QMessageBox.information(
            self, '提示', '爬取第' + str(self.page) + '页《' + self.textLineEdit.text() + '》完毕，还有' + str(int(pageTotal) - self.page) + '页，是否继续爬取',
            QMessageBox.Ok | QMessageBox.No, QMessageBox.No
        )

        if end == QMessageBox.Ok:
            self.page += 1
            self.loadSearchPage(self.textLineEdit.text(), self.page)
        else:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextEditMeiJu()
    win.show()
    sys.exit(app.exec_())
    
















