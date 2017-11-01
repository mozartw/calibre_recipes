from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，各版面的url根据发行日期改变。


class zhongguolvyoubao(BasicNewsRecipe):

    title = '中国旅游报'
    description = '抓取中国旅游报各版面新闻'
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'

    #中国旅游报更新较慢，如果要获取昨天的日期，下面可写为str(datetime.date.today()-datetime.timedelta(days=1)).split('-')。如果是前天就改动days=2，以此类推
    datetime = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表

    #以下用于抓取当日报纸
    url_prefix = 'http://news.ctnews.com.cn/zglyb/html/' #url前缀
    url_prefix_add = 'http://news.ctnews.com.cn/zglyb/html/' + datetime[0] + '-' + datetime[1] + '/' + datetime[2] + '/' #url前缀带日期
    url_prefix_add2 = 'http://news.ctnews.com.cn/zglyb/html/' + datetime[0] + '-' + datetime[1] + '/' + datetime[2] + '/' + 'node_1.htm' #完整url

    #以下用于指定下载日期的报纸，而非当日的报纸。与上面的链接二选一
    #year = '2017'
    #month = '08'
    #date = '28'
    #url_prefix = 'http://news.ctnews.com.cn/zglyb/html/' #url前缀
    #url_prefix_add = 'http://news.ctnews.com.cn/zglyb/html/' + year + '-' + month + '/' + date + '/' #url前缀带日期
    #url_prefix_add2 = 'http://news.ctnews.com.cn/zglyb/html/' + year + '-' + month + '/' + date + '/' + 'node_1.htm' #完整url


    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'style': 'height:800px; overflow-y:scroll; width:100%; BORDER: #BDDBF7 1px solid' }] #保留的正文部分
    #移除上下多余元素，典型的web1.0产物
    #remove_tags = [dict(name='td', attrs={'class':'px12'}),dict(name='table', attrs={'style':r'BORDER-BOTTOM: #555 1px dashed; BORDER-LEFT: #555 1px dashed; BORDER-RIGHT: #555 1px dashed; BORDER-TOP: #555 1px dashed'}),dict(name='tr', attrs={'nowrap':''}),dict(name='td', attrs={'width':'26%'})]
    #delay = 1
    #10线程下载
    simultaneous_downloads = 10
    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y年 %b %d日 星期%a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'



    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
        soup = self.index_to_soup(self.url_prefix_add2)
        banmiankuai = soup.find('table',{'cellpadding':'2','width':'100%'})

        ans0 = []
        #下面的for循环依次遍历各个版面的url并生成二级内容
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
