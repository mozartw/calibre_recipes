from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class jiangxilvyou(BasicNewsRecipe):
    language = 'zh'
    encoding = 'UTF-8'
    url = 'http://www.jxta.gov.cn'

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表

    days_delta = 7 # 定义抓取区间，非calibre自带参数，在parse_index(self)中用于判断，具体见下
    #以下用于算出抓取新闻区间前后两个日期，在封面底端显示：抓取新闻日期区间\n2017-11-6至2017-11-13
    today = datetime.date(int(datetime_t[0]),int(datetime_t[1]),int(datetime_t[2]))
    before = datetime.date.today()-datetime.timedelta(days = days_delta)
    title = '江西旅游政务网'.decode('utf8') + '-'.join(datetime_t) + '前'.decode('utf8') + str(days_delta) + '天'.decode('utf8')
    description = '抓取江西旅游政务网旅游快报、行业新闻、地市动态（'.decode('utf8') + url + '）'.decode('utf8') + '-'.join(datetime_t) + '前'.decode('utf8') + str(days_delta) + '天的新闻'.decode('utf8') + str(before) + '至' + str(today) #三个栏目的索引页为三个不同页面，下面用for循环进行归纳

    remove_attributes = ['style', 'font']
    no_stylesheets = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    keep_only_tags = [{ 'id': 'container' }]
    #delay = 1
    simultaneous_downloads = 10
    remove_javascript = True
    compress_news_images_auto_size = 16
    #移除上下‘当前位置’和‘关闭本页’两个多余元素，典型的web1.0产物
    remove_tags = [dict(name='td', attrs={'class':'dang'}),dict(name='table', attrs={'background':"resource/images/djxlyw/mma_12.jpg"})]
    compress_news_images= True
    #抓取出来的页面文章段落会居中，非常难看，即使在本句当中指定p元素的对齐方式也还是有部分文章依然居中，只能眉毛胡子一把抓，全部分散对齐算了这样做的结果是文章标题也没法居中了
    extra_css = 'p,table,td,tr,div { text-align: justify;}'
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'，windows平台上此项不能包含中文字符，否则生成不了有日期的封面。linux下可以
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'


    #下面这个函数用于添加自定义css，但是官方网站没有详细介绍，试了一下作用不明
    #def get_extra_css(self):
        #if not self.extra_css:
            #br = self.get_browser()
            #self.extra_css = br.open_novisit(
                #'https://raw.githubusercontent.com/YYTB/calibre_recipes/master/jiangxilvyou.css').read()
        #return self.extra_css


    # 以下函数用于生成默认封面。关键的是img_data。
    def default_cover(self, cover_file):
        '''
        Create a generic cover for recipes that don't have a cover
        '''

        try:
            from calibre.ebooks.covers import create_cover
            title = '江西旅游政务网'.decode('utf8')
            date = '抓取新闻日期区间' + '\n' + str(self.before) + '至' + str(self.today)
            img_data = create_cover(title, [date])
            cover_file.write(img_data)
            cover_file.flush()
        except:
            self.log.exception('Failed to generate default cover')
            return False
        return True


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        ans0 = []
        lanmu = {26:'旅游快报',27:'行业动态',28:'地市动态'}
        for nu in range(26,29): #生成三个版面url并添加到urlist列表
            u = 'http://www.jxta.gov.cn/Column.shtml?p5='+str(nu)
            urlist = [u]
            voltitle = lanmu[nu]
            for n in range(2,10): #生成三个版面翻页后的页面url并添加到urlist。比如第2页形式为“http://www.jxta.gov.cn/Column.shtml?p5=26&p7=2”。根据抓取日期范围调整range范围
                urlist.append(u + '&p7=' + str(n))

            #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
            articles = []
            #下面的for循环用于给soup.find提供多个参数，找出包含正文链接的网页框架
            for ur in urlist:
                soup = self.index_to_soup(ur)
                table = soup.find('table',{'id':'Table'})

                #下面的for循环在上面缩小范围的基础上用于继续寻找包含指定日期范围内的正文链接，并添加到article_link列表。
                for tr in table.findAll('tr'): #td,p14两个条件找出来的标签包含了链接块中的日期

                    find_today = re.compile('(\d\d\d\d)-(\d\d)-(\d\d)</font>')#构建找到末尾发布日期的正则表达式
                    month = find_today.search(str(tr))#把上面构建的表达式作用于findAll找出来的内容
                    #try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
                    try:
                        d1 = datetime.date.today()  # 获取今天的日期
                        d2 = datetime.date(int(month.group(1)), int(month.group(2)), int(month.group(3)))  # 获取新闻的日期
                        days_betwen = (d1 - d2).days #获取时间差，结果为整数
                        if days_betwen <= self.days_delta : #限定抓取几天内的新闻，当天的则为days_betwen == 0
                            soup2 = self.index_to_soup(str(tr))

                            #下面的for循环在上面找出指定日期范围内的正文链接当中提取url链接，并配合'http://www.jxta.gov.cn/'形成最终的正文链接
                            for link in soup2.findAll('a'):
                                if not 'News' in link['href']:
                                    continue

                                til = link.contents[0].contents[0].strip() + '(发布日期：' + str(d2) + ')'
                                url = 'http://www.jxta.gov.cn/' + link['href']
                                a = { 'title':til , 'url': url }

                                articles.append(a)
                    except:
                        pass

            ans = (voltitle, articles)
            ans0.append(ans)

        return ans0
