from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class yichunxianshiqudongtai(BasicNewsRecipe):

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表，如果指定一个具体的日期进行抓取的话写为str(datetime.date(2017, 10, 07)).split('-')，或者直接写一个['2017', '10', '07']列表
    days_delta = 7 # 定义抓取区间，非calibre自带参数，在parse_index(self)中用于判断，具体见下
    #以下用于算出抓取新闻区间前后两个日期，在封面底端显示：抓取新闻日期区间\n2017-11-6至2017-11-13
    today = datetime.date(int(datetime_t[0]),int(datetime_t[1]),int(datetime_t[2]))
    before = datetime.date.today()-datetime.timedelta(days = days_delta)
    title = '宜春政府网县市区动态'.decode('utf8') + '-'.join(datetime_t) + '前'.decode('utf8') + str(days_delta) + '天'.decode('utf8')
    url_prefix = 'http://www.yichun.gov.cn/zwgk/zwdt/xsqdt/'
    description = '抓取宜春政府网县市区动态（'.decode('utf8') + url_prefix + '）'.decode('utf8') + '-'.join(datetime_t) + '前'.decode('utf8') + str(days_delta) + '天的新闻'.decode('utf8') + str(before) + '至' + str(today)
    no_stylesheets = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    keep_only_tags = [{ 'style': ' border:3px solid #f0f0f0;' }]
    remove_tags = [dict(name='td', attrs={'style':'font-size:12px;'}),dict(name='td', attrs={'width':'50%'})] #移除上下‘更新时间’和‘信息来源’两个多余元素
#    delay = 1
    simultaneous_downloads = 5
    remove_javascript = True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'，windows平台上此项不能包含中文字符，否则生成不了有日期的封面。linux下可以
    timefmt = '[%Y %b %d %a]'
    __author__ = 'suchao.personal@gmail.com' # 这个订阅列表的作者
#   oldest_article = 1  #下载的最旧的文章是几天前的。默认是7天，单位是天。如果文章有日期，这个参数起作用。但是这个日期暂时不知道怎么认定，这个参数在宜春政府网的政务要闻不起作用

    # 以下函数用于生成默认封面。关键的是img_data。
    def default_cover(self, cover_file):
        '''
        Create a generic cover for recipes that don't have a cover
        '''
        try:
            from calibre.ebooks.covers import create_cover
            title = '宜春政府网县市区动态'.decode('utf8')
            date = '抓取新闻日期区间' + '\n' + str(self.before) + '至' + str(self.today)
            img_data = create_cover(title, [date])
            cover_file.write(img_data)
            cover_file.flush()
        except:
            self.log.exception('Failed to generate default cover')
            return False
        return True


    def get_title(self, link):
        return link.contents[0].strip()

    def parse_index(self):

        urlist = [self.url_prefix]
        """
        下面的for循环用于拼接多个页面的url，并添加到urlist
        翻页后第2页的链接形式为“http://www.yzq.gov.cn/zwgk/zwdt/zwyw/index_1.html”
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
                    if days_betwen <= self.days_delta : #限定抓取几天内的新闻，当天的则为days_betwen == 0

                        soup2 = self.index_to_soup(str(tr))
                        for link in soup2.findAll('a'):
                            link['href'] = link['href'].lstrip('\.') #从抓取的链接当中删除多余的\.
                            til = self.get_title(link) + '(发布日期：' + str(d2) + ')'
                            url = self.url_prefix + link['href']
                            a = { 'title': til, 'url': url }

                            articles.append(a)
                except:
                    pass




        ans = [('宜春政府网县市区动态', articles)]

        return ans
