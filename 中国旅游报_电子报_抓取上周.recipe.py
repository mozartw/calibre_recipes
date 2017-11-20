from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，各版面的url根据发行日期改变。


class zhongguolvyoubao_week(BasicNewsRecipe):
    language = 'zh'
    encoding = 'UTF-8'
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'style': 'height:800px; overflow-y:scroll; width:100%; BORDER: #BDDBF7 1px solid' }] #保留的正文部分
    #移除上下多余元素，典型的web1.0产物
    #remove_tags = [dict(name='td', attrs={'class':'px12'}),dict(name='table', attrs={'style':r'BORDER-BOTTOM: #555 1px dashed; BORDER-LEFT: #555 1px dashed; BORDER-RIGHT: #555 1px dashed; BORDER-TOP: #555 1px dashed'}),dict(name='tr', attrs={'nowrap':''}),dict(name='td', attrs={'width':'26%'})]
    #delay = 1
    #5线程下载
    simultaneous_downloads = 5
    remove_javascript = True

    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'



    # from_day为参照基准日。
    # 如果是从当前日期开始，抓取上一周的报纸则：from_day = datetime.date.today()
    # 如果指定上周一个日期为参照基准日，抓取上上周的报纸则：datetime.date.today()-datetime.timedelta(days= 7)，即基准日从今天往前推7天
    # 如果指定上上周一个日期为参照基准日，抓取上上上周报纸则：datetime.date.today()-datetime.timedelta(days= 2*7)，即基准日从今天往前推2个7天。以此类推
    from_day = datetime.date.today()
    weekday = from_day.weekday()  # 获取指定日期的周的排序, 周一为0, 周日为6
    # 旅游报周一到周五发行，以下算出日期区间
    last_monday_delta = weekday + 7  # 当前日期距离上周一的天数差
    last_friday_delta = weekday + 3  # 当前日期距离上周五的天数差
    last_monday = datetime.date.today() - datetime.timedelta(days = last_monday_delta)
    last_friday = datetime.date.today() - datetime.timedelta(days = last_friday_delta)

    week_rank = last_monday.isocalendar() # 返回结果是三元组（年号，第几周，第几天），用于写入书籍标题
    title = '中国旅游报' + str(week_rank[0]) + '年第' + str(week_rank[1]) + '周'
    description = '抓取' + str(last_monday) + '至' + str(last_friday) + '期间发行的中国旅游报' + '*****参照日期指定的具体办法见recipe当中的from_day变量，默认以当日为参照日，抓取上周*****'

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

            wenzi = '书籍内容：'
            date = str(self.last_monday) + '至' + str(self.last_friday) + '\n期间发行的中国旅游报'
            img_data = create_cover(title, [wenzi,date]) #这个列表里面的内容全部会显示在封面上，默认只有date，可以自己加
            cover_file.write(img_data)
            cover_file.flush()
        except:
            self.log.exception('Failed to generate default cover')
            return False
        return True



    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        ans0 = []
        for nu in range(self.last_monday_delta , self.last_friday_delta - 1 , -1): # for循环用于枚举上一个礼拜周一到周五的日期 。注意：如果先抓取发行最晚的则写为self.last_friday_delta , self.last_monday_delta + 1。
            riqi = self.from_day - datetime.timedelta(days = nu)
            datetime_t = str(riqi).split('-')  #对日期进行拆分，返回一个['2017', '10', '09']形式的列表
            url_prefix = 'http://news.ctnews.com.cn/zglyb/html/' #url前缀
            url_prefix_add = 'http://news.ctnews.com.cn/zglyb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' #url前缀带日期
            url_prefix_add2 = 'http://news.ctnews.com.cn/zglyb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' + 'node_1.htm' #完整url
            vol_title = str(riqi)
            #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
            soup = self.index_to_soup(url_prefix_add2)
            banmiankuai = soup.find('table',{'cellpadding':'2','width':'100%'})
            urlist = [] #各版面链接
            for link in banmiankuai.findAll('a'):
                if 'pdf' in link['href']:
                    continue
                urlist.append(url_prefix_add + link['href'].lstrip(r'./'))
                #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
            articles = []
            #下面的for循环用于给soup.find提供多个参数,即包含最终文章的链接网页框架
            for ur in urlist:
                soup = self.index_to_soup(ur)
                td = soup.find('ul',{'class':'ul02_l'})#抓取的正文链接框架部分


                for link2 in td.findAll('a'):
                    #contens[]是BeautifulSoup的一个属性，我理解为用于去除标签，两层标签就来两次contents[0]，详见https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/。strip() 是通用字符串方法，不加参数则用于去除头尾空格
                    til = link2.contents[0].contents[0].strip()
                    url = url_prefix_add + link2['href']
                    a = { 'title':til , 'url': url }

                    articles.append(a)

                ans = (vol_title, articles)
            ans0.append(ans)

        return ans0
