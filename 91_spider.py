import requests
import os
import re
import time
import random


'''
保存路径设置，这里包括 / 结尾的绝对或者相对路径
'''
save_path=""
'''
设置开始页数
'''
start_page=0
'''
设置结束页数
'''
end_page=100
'''
如果存在cloudflare验证，请填写以下参数
'''
anticaptcha_key=""


def anti_captcha(sitekey,pageurl):
    from python3_anticaptcha import NoCaptchaTaskProxyless
    user_answer = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key = anticaptcha_key)\
                    .captcha_handler(websiteURL=pageurl,
                                     websiteKey=sitekey)
    if user_answer['errorId']==0:
        return user_answer['solution']['gRecaptchaResponse']
    else:
        print("retry get response")
        anti_captcha(sitekey,pageurl)


def download_mp4(url, dir):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'https://91porn.com'}
    req = requests.get(url=url,headers=headers)
    filename = str(dir) + '/1.mp4'
    with open(filename, 'wb') as f:
        f.write(req.content)


def download_img(url, dir):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'https://91porn.com'}
    req = requests.get(url=url,headers=headers)
    with open(str(dir) + '/thumb.png', 'wb') as f:
        f.write(req.content)


def random_ip():
    a = random.randint(1, 255)
    b = random.randint(1, 255)
    c = random.randint(1, 255)
    d = random.randint(1, 255)
    return (str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d))



def pass_cloudflare(context,requrl):
    print("start pass cloudflare. Please wait.")
    r=re.findall("name=\"r\" value=\"(.*?)\"",context)[0]
    id=re.findall("<strong>(.*?)</strong>",context)[0]
    rt_url=re.findall("id=\"challenge-form\" action=\"(.*?)\"",context)[0]
    site_key=re.findall("data-sitekey=\"(.*?)\"",context)[0]
    g_recaptcha_response=anti_captcha(site_key,requrl)
    req=requests.session()
    d=req.post(requrl+rt_url,data={'r':r,'id':id,'g-recaptcha-response':g_recaptcha_response})
    req.cookies.set("language","cn_CN")
    #print(d.text)
    if 'captcha-bypass' not in d.text:
        return req
    else:
        print("pass error,now retry again.")
        pass_cloudflare(d.text,requrl)

def main():
    flag = start_page
    url="http://91porn.com"
    req = requests.session()
    r=req.get(url)
    if 'captcha-bypass' in r.text:
        req=pass_cloudflare(r.text,url)
    while flag <= end_page:
        base_url = 'https://91porn.com/view_video.php?viewkey='
        page_url = 'https://91porn.com/v.php?next=watch&page=' + str(flag)
        get_page = req.get(url=page_url)
        viewkey = re.findall('http://91porn.com/view_video.php\?viewkey=(.*?)&page=.*?&viewtype=basic&category=.*?" title=',
                             get_page.text)
        for key in viewkey:
            header=req.headers
            header['X-Forwarded-For']=random_ip()
            header['Accept-Language']="Accept-Language: zh-CN,zh;q=0.9"
            base_req = req.get(url=base_url + key,headers=header)
            #print(base_req.text)
            ifm = re.findall('<iframe width="560" height="315" src="(.*?)" frameborder="0" allowfullscreen></iframe>',
                             base_req.text)
            try:
                bases_req = req.get(ifm[0])
            except:
                continue
            video_url = re.findall('source src="(.*?)"',bases_req.text)
            tittle = re.findall(r'<div id="viewvideo-title">(.*?)</div>', str(base_req.content, 'utf-8', errors='ignore'),re.S)
            try:
                t = tittle[0]
                tittle[0] = t.replace('\n', '')
                t = tittle[0].replace(' ', '')
            except Exception as e:
                print(e)
            savepath = save_path + str(t)  # 保存路径
            if os.path.exists(savepath) == False:
                try:
                    os.makedirs(savepath)
                    print('开始下载:' + str(t))
                    download_mp4(str(video_url[0]), savepath)
                    print('下载完成')
                except Exception as e:
                    print(e)
            else:
                print('已存在文件夹,跳过')
                time.sleep(2)
        flag = flag + 1
        print('此页已下载完成，下一页是' + str(flag))

if __name__=="__main__":
    main()
