from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class jiangxilvyou(BasicNewsRecipe):

    title = '江西旅游政务网'
    description = '抓取江西旅游政务网旅游快报、行业新闻、地市动态' #三个栏目的索引页为三个不同页面，下面用for循环进行归纳
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    #定义一个通用的url地址。其他recipe中写的，这里懒得用了，下面直接用字符串
    #url_prefix = 'http://www.jxta.gov.cn/Column.shtml?p5='
    no_stylesheets = True
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
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y年 %b %d日 星期%a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表

    #下面这个函数用于添加自定义css，但是官方网站没有详细介绍，试了一下作用不明
    #def get_extra_css(self):
        #if not self.extra_css:
            #br = self.get_browser()
            #self.extra_css = br.open_novisit(
                #'https://raw.githubusercontent.com/YYTB/calibre_recipes/master/jiangxilvyou.css').read()
        #return self.extra_css


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        urlist = []
        #下面的for循环用于拼接三个栏目的url
        for nu in range(26,29):
            urlist.append('http://www.jxta.gov.cn/Column.shtml?p5='+str(nu))
        #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
        articles = []
        #下面的for循环用于给soup.find提供多个参数，找出包含正文链接的网页框架
        for ur in urlist:
            soup = self.index_to_soup(ur)
            table = soup.find('table',{'id':'Table'})

            article_link = []

            #下面的for循环在上面缩小范围的基础上用于继续寻找包含指定日期范围内的正文链接，并添加到article_link列表。
            for tr in table.findAll('tr'): #td,p14两个条件找出来的标签包含了链接块中的日期

                find_today = re.compile('(\d\d)-(\d\d)</font>')#构建找到末尾发布日期的正则表达式
                month = find_today.search(str(tr))#把上面构建的表达式作用于findAll找出来的内容
                #try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
                try:
                    d1 = datetime.date.today()  # 获取今天的日期
                    d2 = datetime.date(int(self.datetime_t[0]), int(month.group(1)), int(month.group(2)))  # 获取新闻的日期
                    days_betwen = (d1 - d2).days #获取时间差，结果为整数
                    if days_betwen <= 2 : #限定抓取几天内的新闻，当天的则为days_betwen == 0
                        article_link.append(str(tr))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据
                except:
                    pass

            soup2 = self.index_to_soup(''.join(article_link))

            #下面的for循环在上面找出指定日期范围内的正文链接当中提取url链接，并配合'http://www.jxta.gov.cn/'形成最终的正文链接
            for link in soup2.findAll('a'):
                if not 'News' in link['href']:
                    continue


                til = link.contents[0].contents[0].strip()
                url = 'http://www.jxta.gov.cn/' + link['href']
                a = { 'title':til , 'url': url }

                articles.append(a)

        ans = [('江西旅游政务网', articles)]

        return ans
