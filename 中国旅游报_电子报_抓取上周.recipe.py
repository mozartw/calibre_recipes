from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，各版面的url根据发行日期改变。


class zhongguolvyoubao(BasicNewsRecipe):

    title = '中国旅游报'
    description = '抓取上周中国旅游报各版面新闻'
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

    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'



    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):

        today = datetime.date.today()  # 获取当前日期, 因为要求时分秒为0, 所以不要求时间
        weekday = today.weekday()  # 获取当前周的排序, 周一为0, 周日为6
        # 旅游报周一到周五发行，以下算出日期区间
        last_monday_delta = weekday + 7  # 当前日期距离上周一的天数差
        last_friday_delta = weekday + 3  # 当前日期距离上周五的时间差

        ans0 = []
        for nu in range(last_friday_delta,last_monday_delta + 1): # for循环用于枚举上一个礼拜周一到周五的日期
            riqi = datetime.date.today() - datetime.timedelta(days = nu)
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
