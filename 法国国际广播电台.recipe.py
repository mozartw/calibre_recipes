from calibre.web.feeds.recipes import BasicNewsRecipe
import datetime,re #导入日期时间模块，各版面的url根据发行日期改变。


class cnrfi(BasicNewsRecipe):

    title = '法国国际广播电台'
    description = '抓取法国国际广播电台中文网各栏目新闻'
    no_stylesheets = True #不采用页面样式表
    keep_only_tags = [{ 'class': 'article-page' }] #保留的正文部分
    remove_tags = [dict(name='div', attrs={'class':'soc-connect clearfix'}),dict(name='div', attrs={'class':'actions'}),dict(name='div', attrs={'class':'meta'})] #移除上下多余元素
    extra_css = 'h1 { font-size: xx-large;}  h2 { font-size: large;}' #抓出来的文章标题太大，把字体改小一点
    #delay = 1 #网页访问较慢（fuck！！），设置1秒延时

    remove_javascript = True
    max_articles_per_feed  = 999 #最大文章数，默认为100
    #压缩图片
    compress_news_images= True
    #在首页所显示的日期格式，缺省格式为日，月，年：timefmt = '[%a, %d %b %Y]'
    timefmt = '[%Y %b %d %a]'
    # 声明这个订阅列表的作者
    __author__ = 'suchao.personal@gmail.com'

    url_prefix = 'http://cn.rfi.fr'

    #下面的函数为recipe必要函数，返回的内容直接用于生成电子书
    def parse_index(self):
		liebie_dic = {'中国':'%E4%B8%AD%E5%9B%BD','港澳台':'%E6%B8%AF%E6%BE%B3%E5%8F%B0', '国际':'%E5%9B%BD%E9%99%85', '人权':'%E4%BA%BA%E6%9D%83', '政治':'%E6%94%BF%E6%B2%BB', '经贸':'%E7%BB%8F%E8%B4%B8', '社会':'%E7%A4%BE%E4%BC%9A', '生态':'%E7%94%9F%E6%80%81', '科技与文化':'%E7%A7%91%E6%8A%80%E4%B8%8E%E6%96%87%E5%8C%96'} # 栏目及对应的url编码
		liebie_list = ['中国','港澳台','国际','人权','政治','经贸','社会','生态','科技与文化'] #在上面的字典范围内设置需要抓取的栏目，可增可减

		ans0 = []
		for lan in liebie_list:
			articles = []
			url_list = []
			vol_tl = lan + '时事'
			for nu in range(1,3): #翻页后的url，以中国板块为例，两个页面一般就包含了4天左右的新闻
				vol_ul = 'http://cn.rfi.fr/' + liebie_dic[lan] + '/all/?page=' + str(nu)
				url_list.append(vol_ul)

			for ul in url_list:
				soup = self.index_to_soup(ul)
				artiultag = soup.find('ul', attrs = {'class':'list'})
				article_link = []
				for li in artiultag.findAll('li'):

					find_today = re.compile('(\d\d)/(\d\d)/(\d\d\d\d)</time>')
					month = find_today.search(str(li))  # 把上面构建的表达式作用于findAll找出来的内容
					# try/except结构主要是用于正则表达式查找，如果不用这个结构，在部分标签当中查找不到内容的时候，下面引用查找结果group()就会报错，造成崩溃。
					try:
						d1 = datetime.date.today()  # 获取今天的日期
						d2 = datetime.date(int(month.group(3)), int(month.group(2)), int(month.group(1)))  # 获取新闻的日期
						days_betwen = (d1 - d2).days  # 获取时间差，结果为整数
						if days_betwen <= 1:  # 限定抓取几天内的新闻，当天的则为days_betwen == 0
							article_link.append(str(li))  # 注意要转换为字符串，beautifusoup不接受列表和其他类型的数据
					except:
						pass

				soup2 = self.index_to_soup(''.join(article_link))

				#下面的for循环在上面找出指定日期范围内的正文链接当中提取url链接
				for link in soup2.findAll('a'):
					imagelink = re.compile(r'src="')
					ilinkfind = imagelink.findall(str(link))
					if ilinkfind:
						continue
					if '/tag/' in link['href']:
						continue
					til = link.contents[0].strip()
					url = self.url_prefix + link['href']
					a = { 'title':til , 'url': url }

					articles.append(a)

			ans = (vol_tl, articles)

			ans0.append(ans)

		return ans0
