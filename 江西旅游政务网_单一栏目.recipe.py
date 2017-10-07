from calibre.web.feeds.recipes import BasicNewsRecipe
 
class jiangxilvyouzhengwu(BasicNewsRecipe):
 
    title = '江西旅游政务网'
    description = '抓取江西旅游政务网旅游快报、行业新闻、地市动态'
#   cover_url = 'http://akamaicovers.oreilly.com/images/0636920024972/lrg.jpg'
    
 

    url_prefix = 'http://www.jxta.gov.cn/Column.shtml?p5=28'
    no_stylesheets = True
    keep_only_tags = [{ 'id': 'container' }] 
#   delay = 1
    simultaneous_downloads = 10
#   remove_javascript = True
    compress_news_images_auto_size = 16
    remove_tags = [dict(name='td', attrs={'class':'dang'}),dict(name='table', attrs={'background':"resource/images/djxlyw/mma_12.jpg"})] #移除上下‘更新时间’和‘信息来源’两个多余元素
    compress_news_images= True
    extra_css = 'p { text-align: justify;}'  
    timefmt = '[%Y年 %b %d日 星期%a]' #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    __author__ = 'suchao.personal@gmail.com' # 这个订阅列表的作者
    
#   def get_extra_css(self):
#       if not self.extra_css:
#           br = self.get_browser()
#           self.extra_css = br.open_novisit(
#               'https://raw.githubusercontent.com/YYTB/calibre_recipes/master/jiangxilvyou.css').read()
#       return self.extra_css
     
    def parse_index(self):
        soup = self.index_to_soup(self.url_prefix)
        table = soup.find('table',{'id':'Table'})
 
        articles = []
        for link in table.findAll('a'):
            if not 'News' in link['href']:
                continue

            
            til = link['title'].strip()
            url = 'http://www.jxta.gov.cn/' + link['href']
            a = { 'title':til , 'url': url }
 
            articles.append(a)
 
        ans = [('江西旅游政务网', articles)]
 
        return ans



