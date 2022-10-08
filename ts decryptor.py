from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import urllib.request
import requests
import re
import os
import subprocess
import shutil
link=input('m3u8 url: ')
file_name=input('file name: ')
index=requests.get(link).text
def load_dirs(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        return False
def load_segs(index,dict):
    load_dirs('segs_ts')
    for i in enumerate(re.split('#EXTINF:',index),0):
        if 'https' in i[1]:
            dict[re.split('#EXTINF:', index)[i[0] + 1].split('\n')[1]]=requests.get((i[1].split('URI="')[1]).split('"')[0]).content
        if 'seg' in i[1]:
            with open('all_segs.txt','a+') as file:
                file.write('file '+'segs_ts/'+i[1].split('\n')[1]+'\n')
            urllib.request.urlretrieve((re.split('URI="',index)[1]).split('key.pub')[0]+i[1].split('\n')[1],'segs_ts/'+i[1].split('\n')[1])
def decryption(aes):
    for i in aes:
        iv = int(i.split('-')[1]).to_bytes(length=16, byteorder='big')
        with open(f'segs_ts/{i}', 'rb') as file_in:
            ciphered_data = file_in.read()
            cipher = AES.new(aes[i], AES.MODE_CBC, iv=iv)
            original_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
            with open(f'segs_ts/{i}', 'wb') as out:
                out.write(original_data)
def ffmpeg():
    subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'all_segs.txt', '-c', 'copy', f'{file_name}.mp3'])
    os.remove('all_segs.txt')
    shutil.rmtree('segs_ts')
aes={}
load_segs(index,aes)
decryption(aes)
ffmpeg()