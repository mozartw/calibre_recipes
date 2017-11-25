from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，各版面的url根据发行日期改变。


class zqcn(BasicNewsRecipe):
    language = 'zh'
    encoding = 'UTF-8'

    month = 0 #表示抓取月份，0表示本月，-1表示上月，以此类推，可自行设定，必须小于等于0

    # 根据month设定，获取指定月份的一个日期，当月（month=0）则获取当日，前月（month为负数）则获取该月份最后一天。
    if month == 0:
        datetime_d = datetime.date.today() - datetime.timedelta(days=abs(month) * datetime.date.today().day)
    elif month < 0:
        datetime_d = datetime.date.today() - datetime.timedelta(days=datetime.date.today().day)
        for i in range(0, month+1, -1):
            datetime_d = datetime_d - datetime.timedelta(days=datetime_d.day)
    else:
        pass
    #以上结束

    title = '中国企业报'.decode('utf8') + str(datetime_d.year) + '年' + str(datetime_d.month) + '月'
<<<<<<< HEAD
    description = '抓取' + str(datetime_d.year) + '年' + str(datetime_d.month) + '月期间发行的中国旅游报。每周二发行一份。更改头部的month变量可以指定不同的抓取月份'
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'class': 'content' }] #保留的正文部分
    remove_tags = [dict(name='div', attrs={'class':'title04'})]
=======
    description = '抓取' + str(datetime_d.year) + '年' + str(datetime_d.month) + '月期间发行的中国旅游报。每周二发行一份。'
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'class': 'content' }] #保留的正文部分
    remove_tags = [dict(name='div', attrs={'class':'title04'})]
    """
    从这发现extra_css可以定义多个标签，用空格隔开即可，不可以加逗号，其实就是css的标准，只不过转化为字符串。
    而且这里的标签指定的是原网页中的标签，而不是抓出来的书里存在的标签。
    以人民日报为例，抓出来的书并没有h1，h2的标题标签，全换成了p，只在原来的网页中有h1,h2等。
    """
>>>>>>> 1de7ac2f2e9bfc416455a50b14d3e0554a028182
    extra_css = 'h1 { font-size: xx-large;}  h2 { font-size: large;}' #抓出来的文章标题太大，把字体改小一点，在人民日报网页中标题是h1标签
    #delay = 1
    #10线程下载
    simultaneous_downloads = 10
    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'，windows平台上此项不能包含中文字符，否则生成不了有日期的封面。linux下可以
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'



    # 以下函数用于生成默认封面。关键的是img_data。
    def default_cover(self, cover_file):
        '''
        Create a generic cover for recipes that don't have a cover
        '''
        try:
            from calibre.ebooks.covers import create_cover
            # 用上面覆写的标题放在封面
            title = '中国企业报'.decode('utf8')
            wenzi = '书籍内容：'
            date = str(self.datetime_d.year) + '年' + str(self.datetime_d.month) + '月发行的中国企业报'
            img_data = create_cover(title, [wenzi,date]) #这个列表里面的内容全部会显示在封面上，默认只有date，可以自己加
            cover_file.write(img_data)
            cover_file.flush()
        except:
            self.log.exception('Failed to generate default cover')
            return False
        return True


    def get_title(self, link):
        return link.contents[0].contents[0].strip()


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        datelist = [] # 用于存放所有获取的日期
        for i in range(self.datetime_d.day-1,-1,-1):
            date_d = self.datetime_d - datetime.timedelta(days=i)
            if date_d.weekday() == 1: # 中国企业报周二发行，如果日期为周二则添加到datelist
                datelist.append(date_d)
        ans0 = []
        for d in datelist:
            strdate = str(d).split('-')
            baseurl = 'http://epaper.zqcn.com.cn/content/' #url前缀
            baseurl_add = baseurl + strdate[0] + '-' + strdate[1] + '/' + strdate[2] + '/' #url前缀带日期
            baseurl_add2 = baseurl_add + 'node_2.htm' #头版完整url
            # 中国企业报网站有时候发行的报纸日期链接会放错，或者在有报纸发行的时候不放链接，所有下面用try/except结构避免错误
            try:
                soup = self.index_to_soup(baseurl_add2)
            except:
                continue
            vol_title = str(d)
            banmiankuai = soup.find('div',{'class':'mulu05'}) #可以有多个属性，比如'table',{'cellpadding':'2','width':'100%'}
            articles = []
            #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
            for link in banmiankuai.findAll('a'):
                if 'pdf' in link['href']:
                    continue
                banmiantitle = link.contents[0].strip()
                soup = self.index_to_soup(baseurl_add + link['href'])
                zhengwenlian = soup.find('ul',{'class':'list01'})#抓取的正文链接框架部分

                for link in zhengwenlian.findAll('a'):
                    til = banmiantitle + '_' + self.get_title(link)
                    url = baseurl_add + link['href']
                    a = { 'title':til , 'url': url }

                    articles.append(a)

            ans = (vol_title, articles)

            ans0.append(ans)

        return ans0
