from calibre.web.feeds.recipes import BasicNewsRecipe
#导入日期时间模块和正则表达式，用于判定链接是否为当日
import datetime,re

class jiangxidaily(BasicNewsRecipe):
 
    title = '江西日报'
    description = '抓取江西日报各版面新闻'
    url_prefix = 'http://www.jxnews.com.cn/jxrb/index.shtml' #url前缀
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'class': 'p14' }] #保留的正文部分
    #移除上下多余元素，典型的web1.0产物
    remove_tags = [dict(name='td', attrs={'bgcolor':'eeeeee'}),dict(name='td', attrs={'height':'50'}),dict(name='td', attrs={'bgcolor':'f8f8f8'})] 
    #remove_tags_after = {'class': 'ScrollDoor_Con'}
    #delay = 1
    #抓取出来的页面文章段落会居中，非常难看，即使在本句当中指定p元素的对齐方式也还是有部分文章依然居中，只能眉毛胡子一把抓，全部分散对齐算了这样做的结果是文章标题也没法居中了
    extra_css = 'p{ text-align: justify;}' 
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

    
    datetime = str(datetime.date.today()).split('-')  #对当天日期进行拆分，返回一个['2017', '10', '09']形式的列表    

    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书 
    def parse_index(self):
        #下面的for循环用soupfind找到各版面的url并生成列表，抛弃
        #以下，测试的时候几个地方漏写了self，因为暂时还没学，根据上面的class看，这个self应该也是面向对象编程的一环，提醒自己在一些变量和函数引用是不能丢，否则calibre报错
        soup = self.index_to_soup(self.url_prefix) 
        banmiankuai = soup.find('table',{'style':'border:1px solid #ffffff;'})
        urlist = [] #各版面链接
        for link in banmiankuai.findAll('a'):
            if not 'jxrb' in link['href']:
                continue
            urlist.append(link['href']) 
        

        
    
        #这个articles列表必须放在这个位置，放下下面的for循环里面会造成最终结果缺少东西，试了很多次的结果，原因待分析            
        articles = []
        #下面的for循环用于给soup.find提供多个参数,即包含最终文章的链接网页框架
        for ur in urlist:
            soup = self.index_to_soup(ur)
            table = soup.find('table',{'cellspacing':'2','width':'96%'})#抓取的正文链接框架部分

            #以下for循环用于判定链接日期是否为当日，并把符合当日条件的标签块提取到artical_link列表   
            
            artical_link = []

            for td in table.findAll('td',"p14"):

                find_today = re.compile('(\d\d)-(\d\d)</td>')
                month = find_today.search(str(td))
                if not month.group(2) == self.datetime[2]:
                    continue
                if not month.group(1) == self.datetime[1]:
                    continue
                artical_link.append(str(td))
        
            soup2 = self.index_to_soup(''.join(artical_link))
            

            for link in soup2.findAll('a'):
                if 'index' in link['href']:
                    continue
                #contens[]是BeautifulSoup的一个属性，我理解为用于去除标签，两层标签就来两次contents[0]，详见https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/。strip() 是通用字符串方法，不加参数则用于去除头尾空格
                til = link.contents[0].strip() 
                url = link['href']
                a = { 'title':til , 'url': url }
                
                articles.append(a)
 
        ans = [('江西日报', articles)]
 
        return ans


