import re,json
import config
import requests
from bs4 import BeautifulSoup
import threadpool
from collections import OrderedDict

allpiclen = 0
now_num = 0

def readhtml():
    rawhtml = ''
    with open(config.filename, 'rb') as f:
        fraw = f.read()
        f.close()
        rawhtml = fraw.decode('UTF-8')
    return rawhtml

class getallimg(object):
    def __init__(self,rawhtml):
        self.rawhtml = rawhtml

    def find_html_img(self):
        img_list = []
        regex = re.compile(r'http://t[0-9].qpic.cn/mblogpic/[A-Fa-f0-9]*/[0-9]*')
        tmp = re.findall(regex,rawhtml)
        img_list = img_list + tmp
        return list(set(img_list))

    def downloadall(self,url):
        global now_num
        filename = '.'.join(url.split('/')[4:6]) + '.jpg'
        now_num+=1
        print(f'({now_num}/{allpiclen}) 正在下 {url} ')

        try:
            reponse = requests.get(url,timeout=10)
            with open('img' + '/' + filename, 'wb') as f:
                f.write(reponse.content)
                complate_url = url
        except requests.exceptions.RequestException as e:
                print(f'{url} 下载失败')
                failed_url = url


class wbhtml(object):
    def __init__(self,rawhtml):
        self.rawhtml = rawhtml

    def analyzeitem(self):
        itemdict = {}
        soup = BeautifulSoup(rawhtml,'html5lib')
        item = soup.find_all(name='div',attrs='item')
        for i , items in enumerate(item):
            def getdivtext(classname,work):
                if work == 1:
                    item_tmp = items
                if work == 2:
                    item_tmp = items.find('div',class_='repost-content')
                tmp = item_tmp.find('div', class_=classname,recursive=False).text
                return tmp

            def imagediscovery():
                srclist = []
                tmp = items.find_all('img',class_="single-image")
                for i in tmp:
                    a = i['src'].split('/')
                    fix_src = '.'.join(a[4:6]) + '.jpg'
                    srclist.append(fix_src)
                return srclist

            if i != -1:
                tmp_list = {}
                tmp_list['author_name'] = getdivtext('author-name',1)
                tmp_list['weibo_date'] = getdivtext('date',1)
                tmp_list['post_content'] = getdivtext('post',1)

                if items.find('div',class_="repost-content"):
                    tmp_list['repost_content'] = {}
                    tmp_list['repost_content']['author_name'] = getdivtext('author-name',2)
                    tmp_list['repost_content']['weibo_date'] = getdivtext('date',2)
                    tmp_list['repost_content']['content'] = getdivtext('post',2)
                    tmp_list['repost_content']['image-container'] = imagediscovery()
                else:
                    tmp_list['image-container'] = imagediscovery()

            itemdict[i] = tmp_list

        wbhtml.exportdata(self,itemdict)

    def exportdata(self,dict1):
        print('分析完毕，正在保存中...')
        sort = OrderedDict(sorted(dict1.items(), key=lambda obj: obj[0]))
        with open('weibo_data.json','w',encoding="utf8") as f:
            json.dump(sort,f,indent=4,ensure_ascii=False)

if __name__ == '__main__':
    #global allpiclen
    print('读取中...')
    rawhtml = readhtml()
    img = getallimg(rawhtml)
    wb = wbhtml(rawhtml)
    urllist = img.find_html_img()

    allpiclen = len(urllist)
    print(f'一共有 {allpiclen} 张图片，开始爬取...')

    # pool = threadpool.ThreadPool(config.threadsnum)
    # request = threadpool.makeRequests(img.downloadall, urllist)
    # [pool.putRequest(req) for req in request]
    # pool.wait()

    print('下载完毕，开始整理数据')
    print('正在解析备份微博的内容')
    wb.analyzeitem()
