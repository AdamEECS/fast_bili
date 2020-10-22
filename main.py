"""
pip3 install you-get requests argparse
"""

import os
import sys
import json
import time
import requests
import argparse

from you_get import common as yg


def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)
    

def time_str(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def cache_page(uid, page_num):
    page_size = 30
    base_url = 'https://api.bilibili.com/x/space/arc/search'
    u = f'{base_url}?mid={uid}&ps={page_size}&tid=0&pn={page_num}&keyword=&order=pubdate&jsonp=jsonp'
    filename = f'./cache/{uid}_page_{page_num}.json'
    if os.path.exists(filename):
        with open(filename, encoding='utf-8') as f:
            data = json.load(f)
    else:
        log('requesting...', filename)
        r = requests.get(u)
        data = r.json()
        with open(filename, 'w+', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def video_list(uid):
    page_num = 1
    d = cache_page(uid, page_num)['data']
    dp = d['page']
    l = d['list']['vlist']
    while dp['pn'] * dp['ps'] < dp['count']:
        page_num += 1
        d = cache_page(uid, page_num)['data']
        dp = d['page']
        l += d['list']['vlist']
    log('视频数量：', len(l))
    with open(f'./cache/{uid}_vlist.json', 'w+', encoding='utf-8') as f:
        json.dump(l, f, ensure_ascii=False, indent=2)
    return l


def download(video, path):
    files = os.listdir(path)
    if video['title'] + '.mp4' in files:
        log('! 已经存在：', video['title'])
        return
    bv = video['bvid']
    url = f'https://www.bilibili.com/video/{bv}'
    sys.argv = ['you-get', '-o', path, url, '--no-caption']
    t1 = time.time()
    log(time_str(t1), 'start', video['title'])
    yg.main()
    t2 = time.time()
    delta_t = int(t2 - t1)
    mm = delta_t // 60
    ss = delta_t % 60
    log(time_str(t2), 'time cost: {0:02}:{0:02}'.format(mm, ss))


def download_all(vs, path):
    for v in vs:
        download(v, path)


def main(args):
    vs = video_list(args.uid)
    download_all(vs, args.path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Download all videos of specified user''')
    parser.add_argument('-u', dest='uid', help='User id of the uploader.')
    parser.add_argument('-o', dest='path', default='./',
                        help='Path to save the download video. Default to the same folder with main.py')
    main(parser.parse_args())
