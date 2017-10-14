from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime #导入日期时间模块，江西日报各版面的url根据发行日期改变。
#基本成功，制作了封面，但是美中不足的是removetags当中在删除正文顶端的px12元素时也删除了正文顶端的图片（如果该条新闻正好有的话），继续研究，看下是不是可以用if语句进行排除。包括试一下removetags能不能指定一个标签的多重属性，只有当多重属性同时符合的时候才进行删除。

class jiangxidaily(BasicNewsRecipe):

    title = '江西日报'
    description = '抓取江西日报各版面新闻'
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    datetime = str(datetime.date.today()).split('-')  #对日期进行拆分，返回一个['2017', '10', '09']形式的列表

    #以下用于抓取当日报纸
    url_prefix = 'http://epaper.jxnews.com.cn/jxrb/html/' #url前缀
    url_prefix_add = 'http://epaper.jxnews.com.cn/jxrb/html/' + datetime[0] + '-' + datetime[1] + '/' + datetime[2] + '/' #url前缀带日期
    url_prefix_add2 = 'http://epaper.jxnews.com.cn/jxrb/html/' + datetime[0] + '-' + datetime[1] + '/' + datetime[2] + '/' + 'node_187.htm' #完整url

    #以下用于指定下载日期的报纸，而非当日的报纸。与上面的链接二选一
    #year = '2017'
    #month = '08'
    #date = '28'
    #url_prefix = 'http://news.ctnews.com.cn/zglyb/html/' #url前缀
    #url_prefix_add = 'http://news.ctnews.com.cn/zglyb/html/' + year + '-' + month + '/' + date + '/' #url前缀带日期
    #url_prefix_add2 = 'http://news.ctnews.com.cn/zglyb/html/' + year + '-' + month + '/' + date + '/' + 'node_1.htm' #完整url

    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'width': '602' }] #保留的正文部分
    #移除上下多余元素，典型的web1.0产物
    remove_tags = [dict(name='td', attrs={'class':'px12'}),dict(name='table', attrs={'style':r'BORDER-BOTTOM: #555 1px dashed; BORDER-LEFT: #555 1px dashed; BORDER-RIGHT: #555 1px dashed; BORDER-TOP: #555 1px dashed'}),dict(name='tr', attrs={'nowrap':''}),dict(name='td', attrs={'width':'26%'})] 
    #delay = 1
    #10线程下载
    simultaneous_downloads = 10
    remove_javascript = True

    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]' 
    timefmt = '[%Y年 %b %d日 星期%a]' 
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com' 



    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
        #以下，测试的时候几个地方漏写了self，因为暂时还没学，根据上面的class看，这个self应该也是面向对象编程的一环，提醒自己在一些变量和函数引用是不能丢，否则calibre报错
        soup = self.index_to_soup(self.url_prefix_add2)
        banmiankuai = soup.find('table',{'cellpadding':'2'})
        urlist = [] #各版面链接
        for link in banmiankuai.findAll('a'):
            if 'pdf' in link['href']:
                continue
            urlist.append(self.url_prefix + link['href'])
        #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析
        articles = []
        #下面的for循环用于给soup.find提供多个参数,即包含最终文章的链接网页框架
        for ur in urlist:
            soup = self.index_to_soup(ur)
            td = soup.find('td',{'width':'403'})#抓取的正文链接框架部分


            for link in td.findAll('a'):
                #contens[]是BeautifulSoup的一个属性，我理解为用于去除标签，两层标签就来两次contents[0]，详见https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/。strip() 是通用字符串方法，不加参数则用于去除头尾空格
                til = link.contents[0].contents[0].strip()
                url = self.url_prefix_add + link['href']
                a = { 'title':til , 'url': url }

                articles.append(a)

        ans = [('江西日报', articles)]

        return ans


