from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class gaoanredian(BasicNewsRecipe):

    title = '高安市热点新闻'
    description = '抓取高安市新闻网头条和热点新闻2个栏目1个月内的新闻。高安政府网更新较慢，可能当地重点放在高安新闻网上。持续观察中'
#   cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    url_prefix = 'http://www.gaxww.com/hot/index.shtml' # 热点新闻栏目
    url_prefix2 = 'http://www.gaxww.com/tt/index.shtml' # 头条新闻栏目_更新较少
    no_stylesheets = True
    extra_css = 'h1 { font-size: xx-large;}  h2 { font-size: large;}' #抓出来的文章标题太大，把字体改小一点
    ignore_duplicate_articles = {'url'} #正文链接中还有一个阅读原文，与标题链接重复，用这个参数可以去除
    keep_only_tags = [{ 'class': 'con_wz' }]
    #remove_tags = [dict(name='td', attrs={'height':'10'}),dict(name='table', attrs={'width':'92%'})] #移除正文多余元素
#    delay = 1
    simultaneous_downloads = 5
    compress_news_images_auto_size = 16
    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    timefmt = '[%Y年 %b %d日 星期%a]' #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    __author__ = 'suchao.personal@gmail.com' # 这个订阅列表的作者
#   oldest_article = 1  #下载的最旧的文章是几天前的。默认是7天，单位是天。如果文章有日期，这个参数起作用。但是这个日期暂时不知道怎么认定，这个参数在宜春政府网的政务要闻不起作用

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表





    def get_title(self, link):
        return link.contents[0].strip()


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):


        #高安新闻网比较操蛋，除栏目首页外，接续页面根据页面总数变化，所以先用正则表达式获取JavaScript当中的页面总数，用于拼接需要抓取的url。
        redian = self.index_to_soup(self.url_prefix)
        toutiao = self.index_to_soup(self.url_prefix2)

        redianbanmian_nu = redian.findAll('script')
        toutiaobanmian_nu = toutiao.findAll('script')

        find_script = re.compile(r'http.*count_page_list_.*?.js')

        redian_re = find_script.search(str(redianbanmian_nu))
        toutiao_re = find_script.search(str(toutiaobanmian_nu))

        redian_url = redian_re.group()
        toutiao_url = toutiao_re.group()

        redian_soup = self.index_to_soup(redian_url)
        toutiao_soup = self.index_to_soup(toutiao_url)

        toutiao_page_find =  toutiao_soup.find(text = re.compile('.*' , re.DOTALL))
        redian_page_find =  redian_soup.find(text = re.compile('.*' , re.DOTALL))

        page_refind = re.compile(r'maxpage = (\d*?);')

        toutiao_page_refind = page_refind.search(str(toutiao_page_find))
        redian_page_refind = page_refind.search(str(redian_page_find))

        toutiao_maxpage_nu = int(toutiao_page_refind.group(1))
        redian_maxpage_nu = int(redian_page_refind.group(1))
        #以上结束，找出两个版面的最大页面数字，第二页就是http://www.gaxww.com/system/count//0088001/000000000000/000/000/c0088001000000000000_000000304.shtml形式，尾巴上的304就是上面找出来的最大数字。前面那些数字串没有多少规律，基本每个版面固定一串。


        urlist = [self.url_prefix,self.url_prefix2]
        """
        下面的for循环用于拼接多个页面的url，并添加到urlist
        县级政府网站更新较慢，一个月抓一次的话翻上个3到4页绰绰有余了。翻多了影响抓取效率
        """
        for nu in range(redian_maxpage_nu,redian_maxpage_nu-10,-1):
            if redian_maxpage_nu <= 99:
                urlist.append(r'http://www.gaxww.com/system/count//0088001/000000000000/000/000/c0088001000000000000_000000' + '0' + str(nu) + r'.shtml')
            else:
                urlist.append(r'http://www.gaxww.com/system/count//0088001/000000000000/000/000/c0088001000000000000_000000' + str(nu) + r'.shtml')
        for nu2 in range(toutiao_maxpage_nu,toutiao_maxpage_nu-10,-1):
            if toutiao_maxpage_nu <= 99:
                urlist.append(r'http://www.gaxww.com/system/count//0088001/000000000000/000/000/c0088001000000000000_000000' + '0' + str(nu2) + r'.shtml')
            else:
                urlist.append(r'http://www.gaxww.com/system/count//0088001/000000000000/000/000/c0088001000000000000_000000' + str(nu2) + r'.shtml')

        #重要！！！这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
        articles = []
        for ur in urlist:
            soup = self.index_to_soup(ur)
            div = soup.find('div', {'class': 'conn_left'})

            arti = []#用正则表达式找出包含当日新闻的框架形成一个列表，会有一些多余的标签，所以下面继续用for循环去除多余标签
            for newsmb in div.findAll('div', {'class': 'newsmb'}):

                find_today = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)</dd>')  # 构建找到末尾发布日期的正则表达式
                month = find_today.search(str(newsmb))  # 把上面构建的表达式作用于findAll找出来的内容
                #try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
                try:
                    d1 = datetime.date.today()  # 获取今天的日期
                    d2 = datetime.date(int(month.group(1)), int(month.group(2)), int(month.group(3)))  # 获取新闻的日期
                    days_betwen = (d1 - d2).days #获取时间差，结果为整数
                    if days_betwen <= 30 : #限定抓取几天内的新闻，当天的则为days_betwen == 0
                        arti.append(str(newsmb))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据
                except:
                    pass


            soup2 = self.index_to_soup(''.join(arti))

            for link in soup2.findAll('a'):

                til = self.get_title(link)
                url = link['href']
                a = { 'title': til, 'url': url }

                articles.append(a)

        ans = [('高安市热点新闻', articles)]

        return ans
