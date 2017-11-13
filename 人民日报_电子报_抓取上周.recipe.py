from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime,re #导入日期时间模块，各版面的url根据发行日期改变。


class renmindaily_week(BasicNewsRecipe):

    title = '人民日报_抓取上周'
    description = '抓取指定参照日期前一周的人民日报各版面新闻。***参照日期指定的具体办法见recipe当中的from_day变量，默认以当日为参照日，抓取上周'
    #通过url抓取封面
    #cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'



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
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y年 %b %d日 星期%a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'


    """
    本来大部分网站生成标题一般找出正文链接的<a>（定义为link）标签后，就可以通过link.contents[0].strip()来获得正文标题
    但是人民日报<a>标签形式是“<a href="nw.D110000renmrb_20171016_2-01.htm"><script>document.write(view("中共中央召开党外人士座谈会<br>征求对中共十九大报告的意见  "))</script></a>”这种多了script脚本等多余内容的形式
    本来在pycharm测试当中可以用“link2.contents[0].contents[0].lstrip(r'document.write(view("').rstrip(r'"))').strip().replace('<br>', ' ')”也可以取得简洁的标题
    但是在calibre当中总是报错，或者总在运行当中，但无法抓取任何内容，也不提示超时，原因不明
    万般无奈，只能把link（在这里定义为link2）转换为str字符串，然后用正则表达式对冗余内容进行替换（现在想起来有些复杂了，完全用replace()就行，不过写完了就算了吧）
    经验：这里定义的link为beautisoup返回的特殊对象，在calibre当中有特别的识别方法，有一些特别的而要求。如果用str()转换为字符串后则没有特别要求。事实上我用return任意一个‘字符串’都能运行，只不过抓取的文章标题全部是'字符串'
    """
    def get_title(self, link2):
        lchange = re.compile(r'<a.*\("') # 构建左侧查找冗余内容的正则表达式，注意对括号进行转义
        rchange = re.compile(r'"\).*</a>') # 构建右侧查找冗余内容的正则表达式，注意对括号进行转义
        lre = lchange.sub('',str(link2)) # 替换左侧内容
        rre = rchange.sub('',lre) # 替换右侧内容
        return rre.strip().replace('<br>', ' ') #返回最终结果并进一步优化，在recipe的最后给文章标题提供值


    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
        # from_day为参照基准日。
        # 如果是从当前日期开始，抓取上一周的报纸则：from_day = datetime.date.today()
        # 如果指定上周一个日期为参照基准日，抓取上上周的报纸则：datetime.date.today()-datetime.timedelta(days= 7)，即基准日从今天往前推7天
        # 如果指定上上周一个日期为参照基准日，抓取上上上周报纸则：datetime.date.today()-datetime.timedelta(days= 2*7)，即基准日从今天往前推2个7天。以此类推
        from_day = datetime.date.today()

        weekday = from_day.weekday()  # 获取指定日期的周的排序, 周一为0, 周日为6
        # 旅游报周一到周五发行，以下算出日期区间
        last_monday_delta = weekday + 7  # 当前日期距离上周一的天数差
        last_sunday_delta = weekday + 1  # 当前日期距离上周五的天数差

        ans0 = []
        for nu in range(last_monday_delta + 1,last_sunday_delta,-1): # for循环用于枚举上一个礼拜周一到周五的日期
            riqi = from_day - datetime.timedelta(days = nu)
            datetime_t = str(riqi).split('-')  #对日期进行拆分，返回一个['2017', '10', '09']形式的列表
            url_prefix = 'http://paper.people.com.cn/rmrb/html/' #url前缀
            url_prefix_add = 'http://paper.people.com.cn/rmrb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' #url前缀带日期
            url_prefix_add2 = 'http://paper.people.com.cn/rmrb/html/' + datetime_t[0] + '-' + datetime_t[1] + '/' + datetime_t[2] + '/' + 'nbs.D110000renmrb_01.htm' #头版完整url
            vol_title = str(riqi)

            #下面的for循环用soupfind找到各版面的url并生成列表，带pdf的链接抛弃
            soup = self.index_to_soup(url_prefix_add2)
            banmiankuai = soup.find('div',{'id':'pageList'}) #可以有多个属性，比如'table',{'cellpadding':'2','width':'100%'}
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
                div = soup.find('div',{'id':'titleList'})#抓取的正文链接框架部分


                for link2 in div.findAll('a'):
                    """
                    人民日报电子报有的版面带视频新闻，会在正文链接前放一个摄像机图标的链接，造成正文重复，而且会有img标签存在正文标题中
                    初步考虑用正则表达式查找图片标签所必须的src=字符串，只在没有找到的时候才继续执行下面的代码
                    本来calibre当中有一个根据链接或者标题去除重复文章的api参数，但是默认去除后一个重复元素，不能选择前一个。人民日报的图片链接在正文标题前，所以没用。
                    """
                    videolink = re.compile(r'src="')
                    vlinkfind = videolink.findall(str(link2))

                    if not vlinkfind:
                        til = self.get_title(link2)
                        url = url_prefix_add + link2['href']
                        a = { 'title':til , 'url': url }

                        articles.append(a)

                    ans = (vol_title, articles)

            ans0.append(ans)
        return ans0
