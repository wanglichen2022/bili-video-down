# import cv2.datasets
# import mediapipe
#
# mpPose = mediapipe.solutions.pose  # 姿态识别方法
# pose = mpPose.Pose(static_image_mode=False, # 静态图模式，False代表置信度高时继续跟踪，True代表实时跟踪检测新的结果
#                    #upper_body_only=False,  # 是否只检测上半身
#                    smooth_landmarks=True,  # 平滑，一般为True
#                    min_detection_confidence=0.5, # 检测置信度
#                    min_tracking_confidence=0.5)
#
# pose.process()


import json

import os

import requests

from lxml import etree

from bs4 import BeautifulSoup
# 防止因https证书问题报错

requests.packages.urllib3.disable_warnings()

headers = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',

    'Refer'

    'er': 'https://www.bilibili.com/'

}

'''

    获取bilibili视频的主要函数

    @param url 视频页面url 结构为:url?参数

    @param p 视频p数

    @param bv 视频bv数

'''


def getBiliBiliVideo(url, p, bv):
    session = requests.session()

    res = session.get(url=url, headers=headers, verify=False)

    response = requests.get(url=url, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')
    # 取视频标题
    name1 = bs.find('h1', class_='video-title tit').get_text().replace(" ","-")
    name1 += str(p)
    _element = etree.HTML(res.content)

    # 获取window.__playinfo__的json对象,[20:]表示截取'window.__playinfo__='后面的json字符串

    videoPlayInfo = str(_element.xpath('//head/script[3]/text()')[0].encode('utf-8').decode('utf-8'))[20:]

    videoJson = json.loads(videoPlayInfo)

    # 获取视频链接和音频链接

    try:

        # 2018年以后的b站视频由.audio和.video组成

        videoURL = videoJson['data']['dash']['video'][0]['baseUrl']

        audioURl = videoJson['data']['dash']['audio'][0]['baseUrl']

        flag = 0

    except Exception:

        # 2018年以前的b站视频音频视频结合在一起,后缀为.flv

        videoURL = videoJson['data']['durl'][0]['url']

        flag = 1

    # 指定文件生成目录,如果不存在则创建目录

    # dirname = ("/").encode("utf-8").decode("utf-8")
    #
    # if not os.path.exists(dirname):
    #     os.makedirs(dirname)
    #
    #     print('文件夹创建成功!')

    # 获取每一集的名称

    name = bv + "-" + str(p)

    # 下载视频和音频

    print('正在下载 "' + name + '" 的视频····')

    fileDownload(homeurl=url, url=videoURL, name='' + name + '_Video.mp4', session=session)

    if flag == 0:
        print('正在下载 "' + name + '" 的音频····')

        fileDownload(homeurl=url, url=audioURl, name='' + name + '_Audio.mp3', session=session)

        print('正在组合 "' + name + '" 的视频和音频····')

        combineVideoAudio('' + name + '_Video.mp4', '' + name + '_Audio.mp3',
                          '' + name1 + '.mp4')

    print(' "' + name + '" 下载完成！')


'''
    使用session保持会话下载文件

    @param homeurl 访问来源

    @param url 音频或视频资源的链接

    @param name 下载后生成的文件名

    @session 用于保持会话
'''


def fileDownload(homeurl, url, name, session=requests.session()):
    # 添加请求头键值对,写上 refered:请求来源

    headers.update({'Referer': homeurl})

    # 发送option请求服务器分配资源

    session.options(url=url, headers=headers, verify=False)

    # 指定每次下载1M的数据

    begin = 0

    end = 1024 * 512 - 1

    flag = 0

    while True:

        # 添加请求头键值对,写上 range:请求字节范围

        headers.update({'Range': 'bytes=' + str(begin) + '-' + str(end)})

        # 获取视频分片

        res = session.get(url=url, headers=headers, verify=False)

        if res.status_code != 416:

            # 响应码不为为416时有数据

            begin = end + 1

            end = end + 1024 * 512

        else:

            headers.update({'Range': str(end + 1) + '-'})

            res = session.get(url=url, headers=headers, verify=False)

            flag = 1

        with open(name.encode("utf-8").decode("utf-8"), 'wb') as fp:

            fp.write(res.content)

            fp.flush()

        # data=data+res.content

        if flag == 1:
            fp.close()

            break


'''

    用于合并音频与视频

    @param videopath 视频路径

    @param audiopath 音频路径

    @param outpath 生成合并视频的路径

'''


def combineVideoAudio(videopath, audiopath, outpath):
    os.system((
                                "ffmpeg.exe -i " + videopath + " -i " + audiopath + " -c copy " + outpath))

    os.remove(videopath)

    os.remove(audiopath)


if __name__ == '__main__':

    # 输入bilibili视频的BV号

    bv = input('视频BV号：')

    url = 'https://www.bilibili.com/video/' + bv

    # 选择视频从第几p开始到第几p结束

    startPart = input('起始P:')

    endPart = input('终止P:')

    for p in range(int(startPart), int(endPart) + 1):
        getBiliBiliVideo(url + '?p=' + str(p), p, bv)

