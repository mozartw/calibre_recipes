from calibre.web.feeds.recipes import BasicNewsRecipe

class yichunyaowen(BasicNewsRecipe):

    title = '宜春政府网宜春要闻'
    description = ''
#   cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'


    url_prefix = 'http://www.yichun.gov.cn/zwgk/zwdt/zwyw/'
    no_stylesheets = True
    keep_only_tags = [{ 'class': 'Custom_UnionStyle' }]
#    delay = 1
    simultaneous_downloads = 5
    remove_javascript = True
    timefmt = '[%Y年 %b %d日 星期%a]' #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    __author__ = 'suchao.personal@gmail.com' # 这个订阅列表的作者
#   oldest_article = 1  #下载的最旧的文章是几天前的。默认是7天，单位是天。如果文章有日期，这个参数起作用。但是这个日期暂时不知道怎么认定，这个参数在宜春政府网的政务要闻不起作用


    def get_title(self, link):
        return link.contents[0].strip()

    def parse_index(self):
        soup = self.index_to_soup(self.url_prefix)
        table = soup.find('table', { 'style' : 'margin-top:5px;' })

        arti = []#用正则表达式找出包含当日新闻的框架形成一个列表，会有一些多余的标签，所以下面继续用for循环去除多余标签
        for tr in table.findAll('tr'):

            find_today = re.compile(r'(\d\d)-(\d\d)</td>')  # 构建找到末尾发布日期的正则表达式
            month = find_today.search(str(tr))  # 把上面构建的表达式作用于findAll找出来的内容

            try:
                if not month.group(2) == '14':#self.datetime[2]:  # 判断日期是否为当日
                    continue
                if not month.group(1) == '10':#self.datetime[1]:  # 判断月份是否为当日
                    continue
                arti.append(str(tr))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据

            except:
                pass


        soup2 = self.index_to_soup(''.join(arti))

        articles = []
        for link in soup2.findAll('a'):


#            link['href']=link['href'].lstrip('\./')
            til = self.get_title(link)
            url = self.url_prefix + link['href']
            a = { 'title': til, 'url': url }

            articles.append(a)

        ans = [('宜春政府网宜春要闻', articles)]

        return ans
