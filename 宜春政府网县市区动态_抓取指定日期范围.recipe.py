from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class yichunxianshiqudongtai(BasicNewsRecipe):

    title = '宜春政府网县市区动态'
    description = ''
#   cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    url_prefix = 'http://www.yichun.gov.cn/zwgk/zwdt/xsqdt/'
    no_stylesheets = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    keep_only_tags = [{ 'style': ' border:3px solid #f0f0f0;' }]
    remove_tags = [dict(name='td', attrs={'style':'font-size:12px;'}),dict(name='td', attrs={'width':'50%'})] #移除上下‘更新时间’和‘信息来源’两个多余元素
#    delay = 1
    simultaneous_downloads = 5
    remove_javascript = True
    timefmt = '[%Y年 %b %d日 星期%a]' #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    __author__ = 'suchao.personal@gmail.com' # 这个订阅列表的作者
#   oldest_article = 1  #下载的最旧的文章是几天前的。默认是7天，单位是天。如果文章有日期，这个参数起作用。但是这个日期暂时不知道怎么认定，这个参数在宜春政府网的政务要闻不起作用

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表

    def get_title(self, link):
        return link.contents[0].strip()

    def parse_index(self):

        urlist = [self.url_prefix]
        """
        下面的for循环用于拼接多个页面的url，并添加到urlist
        翻页后的链接形式为“http://www.yzq.gov.cn/zwgk/zwdt/zwyw/index_1.html”
        政府网站更新较慢，需根据抓取日期范围决定range范围，翻页少了缺内容，翻多了影响抓取效率
        """
        for nu in range(1,10):
            urlist.append(self.url_prefix + 'index_' + str(nu) + r'.html')

        #重要！！！这个articles列表必须放在这个位置
        articles = []
        for ur in urlist:
            soup = self.index_to_soup(ur)
            table = soup.find('table', { 'style' : 'margin-top:5px;' })

            arti = []#用正则表达式找出包含当日新闻的框架形成一个列表，会有一些多余的标签，所以下面继续用for循环去除多余标签

            for tr in table.findAll('tr'):

                find_today = re.compile(r'(\d\d)-(\d\d)</td>')  # 构建找到末尾发布日期的正则表达式
                month = find_today.search(str(tr))  # 把上面构建的表达式作用于findAll找出来的内容
                #try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
                try:
                    d1 = datetime.date.today()  # 获取今天的日期
                    d2 = datetime.date(int(self.datetime_t[0]), int(month.group(1)), int(month.group(2)))  # 获取新闻的日期
                    days_betwen = (d1 - d2).days #获取时间差，结果为整数
                    if days_betwen <= 30 : #限定抓取几天内的新闻，当天的则为days_betwen == 0
                        arti.append(str(tr))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据
                except:
                    pass


            soup2 = self.index_to_soup(''.join(arti))

            for link in soup2.findAll('a'):


                link['href'] = link['href'].lstrip('\.') #从抓取的链接当中删除多余的\.
                til = self.get_title(link)
                url = self.url_prefix + link['href']
                a = { 'title': til, 'url': url }

                articles.append(a)

        ans = [('宜春政府网县市区动态', articles)]

        return ans
