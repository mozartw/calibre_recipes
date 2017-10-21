from calibre.web.feeds.recipes import BasicNewsRecipe
 
class yichunxianshiqudongtai(BasicNewsRecipe):
 
    title = '宜春政府网县市区动态'
    description = ''
#   cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'
    
 
    url_prefix = 'http://www.yichun.gov.cn/zwgk/zwdt/xsqdt'
    no_stylesheets = True
    keep_only_tags = [{ 'style': ' border:3px solid #f0f0f0;' }]
    remove_tags = [dict(name='td', attrs={'style':'font-size:12px;'}),dict(name='td', attrs={'width':'50%'})] #移除上下‘更新时间’和‘信息来源’两个多余元素
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
 
        articles = []
        for link in table.findAll('a'):

            
            link['href']=link['href'].lstrip('\.') #从抓取的链接当中删除多余的\.
            til = self.get_title(link)
            url = self.url_prefix + link['href']
            a = { 'title': til, 'url': url }
 
            articles.append(a)
 
        ans = [('宜春政府网县市区动态', articles)]
 
        return ans
