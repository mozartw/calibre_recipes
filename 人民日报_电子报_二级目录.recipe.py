from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime,re #导入日期时间模块，各版面的url根据发行日期改变。


class renmindaily(BasicNewsRecipe):

    title = '人民日报'
    description = '抓取人民日报各版面新闻'
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    datetime_t = str(datetime.date.today()).split('-')  #对日期进行拆分，返回一个['2017', '10', '09']形式的列表

    #以下用于抓取当日报纸
    url_prefix = 'http://paper.people.com.cn/rmrb/html/' #url前缀
    url_prefix_add = 'http://paper.people.com.cn/rmrb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' #url前缀带日期
    url_prefix_add2 = 'http://paper.people.com.cn/rmrb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' + 'nbs.D110000renmrb_01.htm' #头版完整url

    #以下用于指定下载日期的报纸，而非当日的报纸。与上面的链接二选一
    #year = '2017'
    #month = '08'
    #date = '28'
    #url_prefix = 'http://paper.people.com.cn/rmrb/html/' #url前缀
    #url_prefix_add = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + date + '/' #url前缀带日期
    #url_prefix_add2 = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + date + '/' + 'nbs.D110000renmrb_01.htm' #完整url


    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'class': 'text_c' }] #保留的正文部分
    """
    从这发现extra_css可以定义多个标签，用空格隔开即可，不可以加逗号，其实就是css的标准，只不过转化为字符串。
    而且这里的标签指定的是原网页中的标签，而不是抓出来的书里存在的标签。
    以人民日报为例，抓出来的书并没有h1，h2的标题标签，全换成了p，只在原来的网页中有h1,h2等。
    """
    extra_css = 'h1 { font-size: xx-large;}  h2 { font-size: large;}' #抓出来的文章标题太大，把字体改小一点，在人民日报网页中标题是h1标签
    #delay = 1
    #10线程下载
    simultaneous_downloads = 10
    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    #压缩图片
    #compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'，windows平台上此项不能包含中文字符，否则生成不了有日期的封面。linux下可以
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'


    # 以下conversion_options利用calibre自带参数覆写上面的title，让电子书标题显示为"宜春政府网宜春要闻2017-11-13"格式，可以直接看出抓取操作的日期。
    # 也可以直接在title中直接写，但是会造成calibre的GUI recipe界面中标题显示杂乱，不太好看。
    conversion_options = {'title': '人民日报' + '-'.join(datetime_t)}


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

    """
    本来大部分网站生成标题一般找出正文链接的<a>（定义为link）标签后，就可以通过link.contents[0].strip()来获得正文标题
    但是人民日报<a>标签形式是“<a href="nw.D110000renmrb_20171016_2-01.htm"><script>document.write(view("中共中央召开党外人士座谈会<br>征求对中共十九大报告的意见  "))</script></a>”这种多了script脚本等多余内容的形式
    本来在pycharm测试当中可以用“link.contents[0].contents[0].lstrip(r'document.write(view("').rstrip(r'"))').strip().replace('<br>', ' ')”也可以取得简洁的标题
    但是在calibre当中总是报错，或者总在运行当中，但无法抓取任何内容，也不提示超时，原因不明
    万般无奈，只能把link转换为str字符串，然后用正则表达式进行查找并引用找到的编组
    经验：这里定义的link为beautisoup返回的特殊对象，在calibre当中有特别的识别方法，有一些特别的要求。如果用str()转换为字符串后则没有特别要求。事实上我用return任意一个‘字符串’都能运行，只不过抓取的文章标题全部是'字符串'
    """
    def get_title(self, link):
        find_title = re.compile(r'<.*><script>document\.write\(view\("(.*)"\)\)</script></a>') # 构建正则表达式，注意对括号进行转义
        search_title = find_title.search(str(link)) # 查找内容
        return search_title.group(1).replace('<br>', ' ').strip() #返回最终结果并进一步优化，在recipe的最后给文章标题提供值


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
        soup = self.index_to_soup(self.url_prefix_add2)
        banmiankuai = soup.find('div',{'id':'pageList'}) #可以有多个属性，比如'table',{'cellpadding':'2','width':'100%'}

        ans0 = []
        #下面的for循环依次遍历各个版面的url并生成二级内容
        for link in banmiankuai.findAll('a'):
            articles = []
            if 'pdf' in link['href']:
                continue
            soup = self.index_to_soup(self.url_prefix_add + link['href'].lstrip(r'./'))
            vol_title = link.contents[0].strip()
            div = soup.find('div',{'id':'titleList'})#抓取的正文链接框架部分

            for link in div.findAll('a'):
                videolink = re.compile(r'src="')
                vlinkfind = videolink.findall(str(link))

                if not vlinkfind:
                    til = self.get_title(link)
                    url = self.url_prefix_add + link['href']
                    a = { 'title':til , 'url': url }

                    articles.append(a)

            ans = (vol_title, articles)

            ans0.append(ans)

        return ans0
