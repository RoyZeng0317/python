import tkinter as tk
import webbrowser

class VIPVideo:
    def __init__(self, root):
        self.root = root
        self.root.title('VIP Video 破解工具')
        self.root.geometry('400x200')
        self.create_widgets()

    def create_widgets(self):
        # hint
        label_movie_link = tk.Label(self.root, text="輸入網址: ")
        label_movie_link.place(x=20, y=30, width=100, height=30)

        # input
        self.entry_movie_link = tk.Entry(self.root)
        self.entry_movie_link.place(x=125, y=30, width=260, height=30)

        # clear button
        button_movie_link = tk.Button(self.root, text='clear', command=self.empty)

        button_movie1 = tk.Button(self.root, text="愛奇藝", command=self.open_iqy)
        button_movie1.place(x=25, y=80, width=60, height=40)

        button_movie2 = tk.Button(self.root, text="騰訊視頻", command=self.open_tx)
        button_movie2.place(x=125, y=80, width=80, height=40)

        button_movie3 = tk.Button(self.root, text="優酷視頻", command=self.open_yq)
        button_movie3.place(x=125, y=80, width=80, height=40)

        button_movie = tk.Button(self.root, text="播放 VIP 影片", command=self.play_video)
        button_movie.place(x=125, y=80, width=80, height=40)

        # 
        text = ''
        lab_remind = tk.Label(self.root, text=text, font=('Arial', 15, 'bold'))
        lab_remind.place(x=50, y=150, width=400, height=30)

        self.root.resizeable(False, False)

    def open_iqy(self):
        webbrowser.open('https://www.iqiyi.com')

    def open_tx(self):
        webbrowser.open('https://v.qq.com')

    def open_yq(self):
        webbrowser.open('https://www.youku.com/')

    def play_video(self):
        video = self.entry_movie_link.get()
        webbrowser.open('https://jx.xmflv.cc/?url=' + video)

    def empty(self):
        self.entry_movie_link.delete(0, 'end')

if __name__ == '__main__':
    root = tk.Tk()
    app = VIPVideo(root)
    root.mainloop()