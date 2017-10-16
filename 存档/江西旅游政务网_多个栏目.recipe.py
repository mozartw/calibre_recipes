from calibre.web.feeds.recipes import BasicNewsRecipe

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
        #下面的for循环用于给soup.find提供多个参数
        for ur in urlist:
            soup = self.index_to_soup(ur)
            table = soup.find('table',{'id':'Table'})


            for link in table.findAll('a'):
                #抓取的链接有一些多余的元素，新闻链接含有‘News’关键字，一开始以为是in不是Notin，结果使用Notin，原因待分析
                if not 'News' in link['href']:
                    continue


                til = link.contents[0].contents[0].strip()
                url = 'http://www.jxta.gov.cn/' + link['href']
                a = { 'title':til , 'url': url }

                articles.append(a)

        ans = [('江西旅游政务网', articles)]

        return ans
