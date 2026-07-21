# install library
# pip install Pillow
# pip install ffmpeg
import os
os.chdir('/content/driv/Mydrive/Colab Notebooks') # 使用 Colab 要換路徑

# 定義轉換為總秒的函式
def time2sec(t) -> list[float]:
    arr = t.split(' --> ')  # according (' ---> ') to split the text
    s1 = arr[0].split(',')  # frontend of text is start time
    s2 = arr[1].split(',')  # backend of text is start time
    # clacus the start timie of total time
    start = int(s1[0].split(':')[0]) * 3600 + int(s1[0].split(':')[1]) * 60 + int(s1[0].split(':')[2]) + float(s1[1]) * 0.01
    # clacus the end timie of total time
    end = int(s2[0].split(':')[0]) * 3600 + int(s2[0].split(':')[1]) * 60 + int(s2[0].split(':')[2]) + float(s1[1]) * 0.01
    return [start, end]     # recall the start time and end time of string

f = open('test.srt', 'r')   # use the r to open method to open the subtitles file
srt = f.read()              # read the subtitles file content
f.close()                   # close the file
srt_list = srt.split('\n')  # according the tent enter \n to spilt to the string
sec = 1                     # string of second from the second to start (string of second of index is 1)
text = 2                    # string of chinese tent from the thired to start (string of thired of index is 2)
sec_list: list[list[float]] = [[0.0, 0.0]]  # define the time of string from [0, 0]
text_list = ['']            # define the subtitle content from list to started is empty string ''
# use the loop, read the subtitle file of string per project
for i in range(len(srt_list)):
    if i == sec:
        sec = sec + 4       # if occupied time content, use the sec + 4 (because the time per 4 project will be to show it.)
        # if the both string list start and end can't match it.
        if sec_list[-1][1] != time2sec(srt_list[i])[0]:
            # at the middle time list to add a start time and end time content (means the  haven't subtitles)
            sec_list.append([sec_list[-1][1], time2sec(srt_list[i])[0]])
            # at the middle of text string list to add a empty string (means the haven't subtitles)
            text_list.append('')
        sec_list.append(time2sec(srt_list[i]))  # add time to time list
    if i == text:
        text = text + 4                 # if occupied the content, use text + 4 (because per 4 text will be show it.)
        text_list.append(srt_list[i])   # add text to text list
print(sec_list)
print(text_list)