from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，各版面的url根据发行日期改变。


class zhongguolvyoubao(BasicNewsRecipe):

    title = '中国旅游报'
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'style': 'height:800px; overflow-y:scroll; width:100%; BORDER: #BDDBF7 1px solid' }] #保留的正文部分
    #移除上下多余元素，典型的web1.0产物
    #remove_tags = [dict(name='td', attrs={'class':'px12'}),dict(name='table', attrs={'style':r'BORDER-BOTTOM: #555 1px dashed; BORDER-LEFT: #555 1px dashed; BORDER-RIGHT: #555 1px dashed; BORDER-TOP: #555 1px dashed'}),dict(name='tr', attrs={'nowrap':''}),dict(name='td', attrs={'width':'26%'})]
    #delay = 1
    #10线程下载
    simultaneous_downloads = 10
    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    #压缩图片，抓取内容不多的话可以不压缩
    #compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'，windows平台上此项不能包含中文字符，否则生成不了有日期的封面。linux下可以
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'


    #中国旅游报更新较慢，如果要获取昨天的日期，下面可写为str(datetime.date.today()-datetime.timedelta(days=1)).split('-')。如果是前天就改动days=2，以此类推
    datetime_t = str(datetime.date.today()).split('-') #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表，如果指定一个具体的日期进行抓取的话写为str(datetime.date(2017, 10, 07)).split('-')，或者直接写一个['2017', '10', '07']列表

    #以下用于抓取当日报纸
    url_prefix = 'http://news.ctnews.com.cn/zglyb/html/' #url前缀
    url_prefix_add = 'http://news.ctnews.com.cn/zglyb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' #url前缀带日期
    url_prefix_add2 = 'http://news.ctnews.com.cn/zglyb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' + 'node_1.htm' #完整url

    # 以下conversion_options利用calibre自带参数覆写上面的title，让电子书标题显示为"宜春政府网宜春要闻2017-11-13"格式，可以直接看出抓取操作的日期。
    # 也可以直接在title中直接写，但是会造成calibre的GUI recipe界面中标题显示杂乱，不太好看。
    conversion_options = {'title': '中国旅游报'.decode('utf8') + '-'.join(datetime_t)} # 不加decode选项在windows中书名会有乱码
    description = '抓取中国旅游报' + '-'.join(datetime_t) + '各版面新闻'

    # 以下函数用于生成默认封面。关键的是img_data。
    def default_cover(self, cover_file):
        '''
        Create a generic cover for recipes that don't have a cover
        '''
        try:
            from calibre.ebooks.covers import create_cover
            # 用上面覆写的标题放在封面
            title = title = self.title if isinstance(self.title, unicode) else \
                    self.title.decode(preferred_encoding, 'replace')
            date = '发行日期：' + '-'.join(self.datetime_t)
            img_data = create_cover(title, [date]) #这个列表里面的内容全部会显示在封面上，默认只有date，可以自己加
            cover_file.write(img_data)
            cover_file.flush()
        except:
            self.log.exception('Failed to generate default cover')
            return False
        return True

    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        soup = self.index_to_soup(self.url_prefix_add2)
        banmiankuai = soup.find('table',{'cellpadding':'2','width':'100%'})

        ans0 = []
        #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
        for link in banmiankuai.findAll('a'):
            articles = []
            if 'pdf' in link['href']:
                continue
            vol_title = link.contents[0].strip()
            soup = self.index_to_soup(self.url_prefix_add + link['href'].lstrip(r'./'))

            td = soup.find('ul',{'class':'ul02_l'})#抓取的正文链接框架部分

            for link2 in td.findAll('a'):
                #contens[]是BeautifulSoup的一个属性，我理解为用于去除标签，两层标签就来两次contents[0]，详见https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/。strip() 是通用字符串方法，不加参数则用于去除头尾空格
                til = link2.contents[0].contents[0].strip()
                url = self.url_prefix_add + link2['href']
                a = { 'title':til , 'url': url }

                articles.append(a)

            ans = (vol_title, articles)
            ans0.append(ans)

        return ans0
