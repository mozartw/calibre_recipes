from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class chinata(BasicNewsRecipe):

    title = '国家旅游局官网_重点工作多个栏目'
    description = '抓取国家旅游局官网_重点工作多个栏目' #三个栏目的索引页为三个不同页面，下面用for循环进行归纳
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    #定义一个通用的url地址。其他recipe中写的，这里懒得用了，下面直接用字符串
    url_prefix = 'http://www.cnta.gov.cn/zdgz/'
    no_stylesheets = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    keep_only_tags = [{ 'class': 'tpbfmain' }]
    #delay = 1
    simultaneous_downloads = 10
    remove_javascript = True
    compress_news_images_auto_size = 16
    #移除上下‘当前位置’和‘关闭本页’两个多余元素，典型的web1.0产物
    #remove_tags = [dict(name='td', attrs={'class':'dang'}),dict(name='table', attrs={'background':"resource/images/djxlyw/mma_12.jpg"})]
    compress_news_images= True
    #抓取出来的页面文章段落会居中，非常难看，即使在本句当中指定p元素的对齐方式也还是有部分文章依然居中，只能眉毛胡子一把抓，全部分散对齐算了这样做的结果是文章标题也没法居中了
    extra_css = 'p,table,td,tr,div { text-align: justify;}'
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y年 %b %d日 星期%a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'

    datetime_t = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表

    #定义函数，获得标题
    def get_title(self, link):
        title_find = re.compile(r'<.*><span>.*</span>(.*)</a>') #构建正则表达式查找标题内容，link形式为<a target="_blank" href="./201708/t20170825_836934.shtml"><span>2017-08-25</span>全域旅游广西模式提升与推广座谈会举行</a>
        title_search = title_find.search(str(link)) #查找内容，注意用str转化为字符串
        return title_search.group(1).strip() #返回最终结果并进一步优化，在recipe的最后给文章标题提供值


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):

        soup = self.index_to_soup(self.url_prefix)
        lanmu_tl = soup.findAll('div', {'class': 'text'}) #找出包含栏目标题的div标签
        lanmu_ul = soup.findAll('a', {'class': 'more'}) #找出包含栏目url的a标签

        ans0 = []
        for tl,ul in zip(lanmu_tl,lanmu_ul): #使用zip元素对，用都变量的for循环交替提取各栏目的标题和链接
            vol_tl = tl.contents[0].strip() #定义栏目标题
            vol_ul = self.url_prefix + ul['href'].lstrip('\./') #定义栏目第一个页面的url

            urlist = [vol_ul] #定义一个栏目多个页面url的列表，找出规律后在下面用for循环进行添加

            for nu in range(1,5): #生成同一栏目翻页后的多个页面url，第二页形式为http://www.cnta.gov.cn/zdgz/qyly/index_1.shtml
                u = vol_ul + 'index_' + str(nu) + r'.shtml'
                urlist.append(u)

            #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
            articles = []
            #下面的for循环用于给soup.find提供多个参数，找出包含正文链接的网页框架
            article_link = []
            for ur in urlist:
                #重要！！！下面的try/except结构是为了防止上面指定的翻页数过多，最终溢出原网页拥有的页面，导致calibre报错并中断抓取进程。所有指定翻页的网页必须添加这个语句。以备不测。
                try:
                    soup2 = self.index_to_soup(ur)
                except:
                    break

                for li in soup2.findAll('li'):
                    find_today = re.compile('(\d\d\d\d)-(\d\d)-(\d\d)</span>')
                    month = find_today.search(str(li))#把上面构建的表达式作用于findAll找出来的内容
                    #try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
                    try:
                        d1 = datetime.date.today()  # 获取今天的日期
                        d2 = datetime.date(int(month.group(1)), int(month.group(2)), int(month.group(3)))  # 获取新闻的日期
                        days_betwen = (d1 - d2).days #获取时间差，结果为整数
                        if days_betwen <= 30 : #限定抓取几天内的新闻，当天的则为days_betwen == 0
                            article_link.append(str(li))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据
                    except:
                        pass

            soup3 = self.index_to_soup(''.join(article_link))

            #下面的for循环在上面找出指定日期范围内的正文链接当中提取url链接，并配合'http://www.jxta.gov.cn/'形成最终的正文链接
            for link in soup3.findAll('a'):

                til = self.get_title(link)
                url = vol_ul + link['href']
                #calibre能够识别相对路径，以后相对路径一律不用修改特别是“厕所革命”栏目用的i是../../这种网上跳级的模式，更不能变动
                #url = vol_ul + link['href'].lstrip('\./')
                a = { 'title':til , 'url': url }

                articles.append(a)

            ans = (vol_tl, articles)

            ans0.append(ans)


        return ans0
