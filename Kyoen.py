from tkinter import *
from tkinter import ttk
from copy import deepcopy
import traceback
from random import randrange
from time import time
import sys 
sys.setrecursionlimit(10**7)

# ボードの一辺の長さ
ROW_NUM = 10
# 決定された点
STONE = '●'
# 一手前の点
PRE_STONE = '○'
# フォント指定
FONT_FAMILY = ''
FONT_SIZE = 30

# セルの前景色
FOREGROUND_COLOR = 'black'
# セルの背景色
BACKGROUND_COLOR = 'green'
# 先手後手
Ply = ['先手', '後手']

# CPU戦での制限時間
TIME_LIMIT = 30
# カウントダウンの刻み
INTERVAL = 100
# CPUの共円探索数
CPU_DIFFICULITY = 100
# ヒントの表示時間
HINT_TIME = 2000


class BoardUI(ttk.Frame):
    #目次
    '''
    __init__(self, objTk=None)
    clear_position_list(self)
    clear_disp_list(self)
    update_board(self)
    set_up(self)
    display_board(self, gamemode_num)
    on_click_board_cell(self, idx_x, idx_y)
    update_time(self)
    gameover(self)
    clear_chack(self)
    cpu_indicate(self)
    cpu_random(self)
    make_Kyoen(self, Kyoen_list)
    disp_Ng_list(self)
    update_Ng_position_list(self)
    restart(self)
    hint(self)
    on_click_indicate_button(self)
    on_click_in_indicate(self,x,y)
    indicate_mode_cancel(self)
    indicate_Kyoen(self)
    put_stone(self, x, y)
    set_indicate_button(self)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    are_these_Kyoen(search_list)
    find_Kyoen(x, y, prot_list)
    main()
    '''
    def __init__(self, objTk=None):
        '''
        初期化
        '''
        super().__init__(objTk)
        self.clear_position_list()
        self.clear_disp_list()
        self.End_flag = False
        self.pre = (-1,-1)   
        self.set_up()


    def clear_position_list(self):
        '''
        点の配置を初期化
        '''
        self.prot_list = []
        self.position_list = [['']*ROW_NUM for _ in range(ROW_NUM)]
        self.Ng_list = [] #[(x,y),....]
        self.Ng_position = [[False]*ROW_NUM for _ in range(ROW_NUM)]
        while len(self.Ng_list) < 3:
            x = randrange(ROW_NUM)
            y = randrange(ROW_NUM)
            if (x,y) in self.Ng_list:
                continue
            self.position_list[x][y] = STONE
            self.Ng_list.append((x,y))
            self.prot_list.append((x,y))
        

        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                stack = deepcopy(self.prot_list)
                stack.append((x,y))
                if are_these_Kyoen(stack):
                    self.Ng_position[x][y] = True
                    self.Ng_list.append((x,y))

    def clear_disp_list(self):
        '''
        点の配置（表示用）を初期化
        '''
        self.disp_list = [['']*ROW_NUM for _ in range(ROW_NUM)]
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                self.disp_list[x][y] = StringVar()
                self.disp_list[x][y].set('')

    def update_board(self):
        '''
        点の配置を画面に反映
        '''
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                self.disp_list[x][y].set(self.position_list[x][y])

    def set_up(self):
        '''
        モード選択
        '''
        for widget in self.winfo_children():
            widget.destroy()

        # 情報表示ラベルの表示内容
        self.main_display_var = StringVar()
        self.main_display_var.set('モードを選んでください')

        # 情報表示ラベル
        info_label = ttk.Label(
            self, textvariable=self.main_display_var
        )

        info_label.grid(
            row=0, column=0, columnspan=ROW_NUM, sticky=(N, S, E, W)
        )

        # フォント指定
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Main.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        style.configure('Sub.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background='gray')
        dx,dy = 210,54 #210,45

        button = ttk.Button(self,
                            text = '一人',
                            style='Sub.TButton',
                            command= lambda : self.display_board(1),
                            )
        button.grid(row=1, column=0, sticky=(N, S, E, W),padx=dx,pady=dy)
        
        button = ttk.Button(self,
                            text = '対人',
                            style='Sub.TButton',
                            command= lambda : self.display_board(2),
                            )
        button.grid(row=2, column=0, sticky=(N, S, E, W),padx=dx,pady=dy)

        button = ttk.Button(self,
                            text = '対CPU',
                            style='Sub.TButton',
                            command= lambda : self.display_board(3)
                            )
        button.grid(row=3, column=0,  
                    sticky=(N, S, E, W), padx=dx,pady=dy)
        
        button = ttk.Button(self,
                            text = '終了',
                            style='Sub.TButton',
                            command= lambda : exit(),
                            )
        button.grid(row=4, column=0, sticky=(N, S, E, W),padx=dx,pady=dy)
        
        self.grid(row=0, column=0, sticky=(N, S, E, W))
        

    def display_board(self, gamemode_num):
        '''
        メインボード表示
        '''
        self.gamemode = gamemode_num
        #画面リセット
        for widget in self.winfo_children():
            widget.destroy()

        # 情報表示ラベルの表示内容
        self.main_display_var = StringVar()
        self.main_display_var.set('点を打ちたい場所をクリックしてください。')

        self.sub_display_var = StringVar()
        if gamemode_num == 1:
            self.sub_display_var.set('score : %d   '%len(self.prot_list))
        elif gamemode_num == 2:
            self.sub_display_var.set('%s   '%Ply[(len(self.prot_list)+1)%2])
        elif gamemode_num == 3:
            #初期タイマー
            self.start_time = time()
            self.sub_display_var.set('%d   '%TIME_LIMIT)
            self.after_ID = self.after(INTERVAL, self.update_time)


        # 情報表示ラベル
        info_label = ttk.Label(
            self, textvariable=self.main_display_var
        )
        info_label.grid(
            row=0, column=0, columnspan=ROW_NUM, sticky=(N, S, E, W)
        )

        sub_label = ttk.Label(
            self, textvariable=self.sub_display_var
        )
        sub_label.grid(
            row=0, column=0, columnspan=ROW_NUM, sticky=(E)
        )

        # フォント指定
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Main.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        style.configure('Sub.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background='gray')
        style.configure('Red.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background='red')
        style.configure('Green_Yellow.TButton', font=(FONT_FAMILY, FONT_SIZE),
                        foreground=FOREGROUND_COLOR, background='green yellow')


        #ボタン初期設定
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                button = ttk.Button(self,
                                    textvariable=self.disp_list[x][y],
                                    style='Main.TButton',
                                    command=lambda idx_x=x, idx_y=y: 
                                        self.on_click_board_cell(
                                            idx_x, idx_y)
                                    )
                button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
        

        if self.gamemode == 1:
            button = ttk.Button(self,
                                text = 'ヒント',
                                style='Sub.TButton',
                                command= lambda : self.hint()
                                )
            button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                        sticky=(N, S, E, W), padx=0,pady=0)
        else:
            self.set_indicate_buttton()

        button = ttk.Button(self,
                            text = 'リスタート',
                            style='Sub.TButton',
                            command= lambda : self.restart()
                            )

        button.grid(row=ROW_NUM+1, column=ROW_NUM-(ROW_NUM//2), 
                    columnspan = ROW_NUM//2,rowspan = 1 , 
                    sticky=(N, S, E, W), padx=0,pady=0
                    )

        self.grid(row=0, column=0, sticky=(N, S, E, W))

        # 石の配置を画面に反映
        self.update_board()

        # 横方向の引き伸ばし設定
        for y in range(ROW_NUM):
            self.columnconfigure(y, weight=1)

        # 縦方向の引き伸ばし設定
        self.rowconfigure(0, weight=0)  # 情報表示欄
        for x in range(ROW_NUM):
            self.rowconfigure(x+1, weight=1)

        # ウィンドウ自体の引き伸ばし設定
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)



    def on_click_board_cell(self, idx_x, idx_y):
        '''
        マスクリック時の処理
        '''
        if self.gamemode == 1:
            """
            1人用共円
            """

            # 石が打てる位置（先手）
            if self.End_flag:
                return

            if (idx_x, idx_y) in self.prot_list:
                self.main_display_var.set('この位置には点を打つことができません。')
                return

            try:
                self.put_stone(idx_x, idx_y)
                self.Ng_list.append((idx_x,idx_y))
                self.prot_list.append((idx_x,idx_y))
                self.sub_display_var.set('score : %d   '%len(self.prot_list))
                # 石の配置を画面に反映
                self.update_board()

                if self.Ng_position[idx_x][idx_y]:
                    self.main_display_var.set('共円発生!')
                    Kyoen_list = find_Kyoen(idx_x,idx_y,self.prot_list)
                    self.disp_Ng_list()
                    self.make_Kyoen(Kyoen_list)
                    self.End_flag = True            
                    return

                self.update_Ng_position_list()

                #置ける場所がなければクリア
                self.clear_check()
                

            except Exception:
                print(traceback.format_exc())

        
        elif self.gamemode == 2:
            '''
            対人用共円
            '''
            if self.End_flag:
                return

            if (idx_x, idx_y) in self.prot_list:
                self.main_display_var.set('この位置には点を打つことができません。')
                return

            try:
                self.put_stone(idx_x, idx_y)
                self.Ng_list.append((idx_x,idx_y))
                self.prot_list.append((idx_x,idx_y))
                self.sub_display_var.set('%s   '%Ply[(len(self.prot_list)+1)%2])
                # 石の配置を画面に反映
                self.update_board()      
                self.update_Ng_position_list()
                self.set_indicate_buttton()

            except Exception:
                print(traceback.format_exc())


        elif self.gamemode == 3:
            '''
            対CPU用共円
            '''
            if self.End_flag:
                return

            if (idx_x, idx_y) in self.prot_list:
                self.main_display_var.set('この位置には点を打つことができません。')
                return

            try:
                self.after_cancel(self.after_ID)
                self.put_stone(idx_x, idx_y)
                self.Ng_list.append((idx_x,idx_y))
                self.prot_list.append((idx_x,idx_y))
                # 石の配置を画面に反映
                self.update_board()      
                self.update_Ng_position_list()

                self.cpu_indicate()
                if self.End_flag:
                    return
                self.cpu_random()
                self.set_indicate_buttton()

                self.start_time = time()
                self.sub_display_var.set('%d   '%TIME_LIMIT)
                self.after_ID = self.after(INTERVAL, self.update_time)

            except Exception:
                print(traceback.format_exc())

        else:
            print('Gamemode error')
            exit()

    def update_time(self):
        '''
        CPU戦でのカウントダウンタイマー
        '''
        self.after_ID = self.after(INTERVAL, self.update_time)
        now_time = time()
        elapsed_time = now_time - self.start_time
        elapsed_time = TIME_LIMIT - elapsed_time
        if elapsed_time <= 0:
            self.gameover()
            return
        elapsed_time_str = '{:.1f}'.format(elapsed_time)
        self.sub_display_var.set('%s   '%elapsed_time_str)
        return

    def gameover(self):
        '''
        時間切れゲームオーバー
        '''
        self.after_cancel(self.after_ID)
        self.sub_display_var.set('時間切れ! CPUの勝利!   ')
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                button = ttk.Button(self,
                                    textvariable=self.disp_list[x][y],
                                    style='Main.TButton'
                                    )
                button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
        
        self.disp_Ng_list()
        return

    def clear_check(self):
        '''
        1人用クリア判定
        '''
        if len(set(self.Ng_list)) == ROW_NUM**2 :
            self.End_flag = True
            self.main_display_var.set('Clear!!!')
            for x in range(ROW_NUM):
                for y in range(ROW_NUM):
                    if (x, y) not in self.Ng_list:
                        continue
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Green_Yellow.TButton'
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)



    def cpu_indicate(self):
        '''
        CPU側の共円指摘処理
        '''
        for _ in range(CPU_DIFFICULITY):
            search_list = [self.pre]
            for _ in range(3):
                rand_ind = randrange(len(self.prot_list))
                if self.prot_list[rand_ind] in search_list:
                    break
                search_list.append(tuple(self.prot_list[rand_ind]))
            if len(search_list) != 4:
                continue
            if are_these_Kyoen(search_list):
                self.after_cancel(self.after_ID)
                self.main_display_var.set('共円発生!')
                self.disp_Ng_list()
                self.make_Kyoen(search_list)
                self.End_flag = True            
        return

    def cpu_random(self):
        '''
        CPUの点を打ち行動
        '''
        while True:
            x = randrange(ROW_NUM)
            y = randrange(ROW_NUM)
            if (x,y) not in self.prot_list:
                break
            
        self.put_stone(x, y)
        self.Ng_list.append((x,y))
        self.prot_list.append((x,y))
        self.sub_display_var.set('%s   '%Ply[(len(self.prot_list)+1)%2])
        # 石の配置を画面に反映
        self.update_board()   
        self.update_Ng_position_list()
        return

    def make_Kyoen(self, Kyoen_list:list):
        '''
        共円となる点を赤く表示
        '''
        Kyoen_list.pop()
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                stack = deepcopy(Kyoen_list)
                stack.append((x,y))
                if are_these_Kyoen(stack):
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Red.TButton',
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W))
        
        for x,y in Kyoen_list:
            button = ttk.Button(self,
                                textvariable=self.disp_list[x][y],
                                style='Red.TButton',
                                )
            button.grid(row=x+1, column=y, sticky=(N, S, E, W))
        return
    
    def disp_Ng_list(self):
        '''
        共円候補地を黄緑表示
        '''
        for x,y in self.Ng_list:
            button = ttk.Button(self,
                                textvariable=self.disp_list[x][y],
                                style='Green_Yellow.TButton'
                                )
            button.grid(row=x+1, column=y, sticky=(N, S, E, W))
        return

    def update_Ng_position_list(self):
        '''
        直近に打った点に対し、共円となる点を更新
        '''
        N = len(self.prot_list)
        #更新点を全探索
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                if self.Ng_position[x][y]:
                    #既に共円候補(または既に設置済み)となっている点は除外
                    continue
                
                #設置済みから残り2点取り出す
                for i in range(N-1):
                    for j in range(i+1,N):
                        stack = [self.pre, (x,y)]
                        stack.append(self.prot_list[i])
                        stack.append(self.prot_list[j])
                        if are_these_Kyoen(stack):
                            self.Ng_position[x][y] = True
                            self.Ng_list.append((x,y))
        return 

    def restart(self):
        '''
        リスタートボタン処理
        '''
        self.End_flag = False
        self.pre = (-1, -1)
        if self.gamemode == 3:
            self.after_cancel(self.after_ID)
        self.clear_position_list()
        self.clear_disp_list()
        #self.main_display_var.set('石を置きたい場所をクリックしてください。')
        self.set_up()
        return

    def hint(self):
        '''
        共円となる候補地を一定時間表示
        '''
        if self.End_flag:
            return
        
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                if (x,y) in self.Ng_list:
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Green_Yellow.TButton'
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
                else:
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Main.TButton'
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)

        self.after(HINT_TIME, self.board_restoration)
        return

    def board_restoration(self):
        '''
        ボードを元の状態に戻す
        '''
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                button = ttk.Button(self,
                                    textvariable=self.disp_list[x][y],
                                    style='Main.TButton',
                                    command=lambda idx_x=x, idx_y=y: 
                                        self.on_click_board_cell(
                                            idx_x, idx_y)
                                    )
                button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
        return

    def on_click_indicate_button(self):
        '''
        共円を指摘できるモードへ移行
        '''
        if self.End_flag:
            return
        
        self.stack = [self.pre]
        #指摘取り消しボタン
        button = ttk.Button(self,
                            text = '指摘取り消し',
                            style='Sub.TButton',
                            command= lambda : self.indicate_mode_cancel()
                            )
        button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                    sticky=(N, S, E, W), padx=0,pady=0)

        #ボタンを指摘モードへ(一手前のみ初期選択)
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                if (x,y) == self.pre:
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Green_Yellow.TButton'
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
                else:
                    button = ttk.Button(self,
                                        textvariable=self.disp_list[x][y],
                                        style='Main.TButton',
                                        command=lambda idx_x=x, idx_y=y: self.on_click_in_indicate(
                                            idx_x, idx_y)
                                        )
                    button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)
        return
    
    def on_click_in_indicate(self,x,y):
        '''
        共円指摘モードにおけるクリック判定
        '''
        if self.End_flag:
            return
        if (x,y) not in self.prot_list:
            return

        # self.stackは共円候補点
        if (x,y) in self.stack: #選択キャンセル
            index = self.stack.index((x,y))
            self.stack.pop(index)
            button = ttk.Button(self,
                                textvariable=self.disp_list[x][y],
                                style='Main.TButton',
                                command=lambda idx_x=x, idx_y=y: self.on_click_in_indicate(
                                    idx_x, idx_y)
                                )
            button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)

        else: # 候補点に追加
            self.stack.append((x,y))
            button = ttk.Button(self,
                                textvariable=self.disp_list[x][y],
                                style='Green_Yellow.TButton',
                                command=lambda idx_x=x, idx_y=y: self.on_click_in_indicate(
                                    idx_x, idx_y)
                                )
            button.grid(row=x+1, column=y, sticky=(N, S, E, W), padx=0,pady=0)

        # 4点選択時に共円指摘可能にする
        if len(self.stack) == 4:
            button = ttk.Button(self,
                                text = '共円！',
                                style='Sub.TButton',
                                command= lambda : self.indicate_Kyoen()
                                )
            button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                        sticky=(N, S, E, W), padx=0,pady=0)
        else: # 4点選択時以外は指摘モード取り消しボタン
            button = ttk.Button(self,
                                text = '指摘取り消し',
                                style='Sub.TButton',
                                command= lambda : self.indicate_mode_cancel()
                                )
            button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                        sticky=(N, S, E, W), padx=0,pady=0)
        return


    def indicate_mode_cancel(self):
        '''
        共円指摘モード取り消し
        '''
        #ボタンを共円指摘に戻す
        self.set_indicate_buttton()

        #ボタン機能を元に戻す
        self.board_restoration()
        return

    
    def indicate_Kyoen(self):
        '''
        self.stackを共円として指摘
        '''
        if self.End_flag:
            return

        self.indicated_flag = True

        if are_these_Kyoen(self.stack):            
            if self.gamemode == 2:
                self.sub_display_var.set('%sの勝利!   '%Ply[(len(self.prot_list)+1)%2])
            elif self.gamemode == 3:
                self.after_cancel(self.after_ID)
                self.sub_display_var.set('あなたの勝利!   ')
            self.main_display_var.set('共円発生!')
            self.disp_Ng_list()
            self.make_Kyoen(self.stack)
            self.End_flag = True
        else:
            self.main_display_var.set('共円ではない！')
            button = ttk.Button(self,
                                text = '指摘不可',
                                style='Sub.TButton',
                                command= lambda :
                                    self.indicate_limit_message()
                                )
            button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                        sticky=(N, S, E, W), padx=0,pady=0)
            self.board_restoration()
            return
        return
    
    def indicate_limit_message(self):
        if self.End_flag:
            return
        self.main_display_var.set('1ターンの共円指摘可能回数は1回です!')
        return
    

    def put_stone(self, x, y):
        """
        点を打つ
        """
        pre_x, pre_y = self.pre
        if pre_x != -1:
            self.position_list[pre_x][pre_y] = STONE
        self.position_list[x][y] = PRE_STONE
        self.pre = (x,y)
        self.main_display_var.set('点を打ちたい場所をクリックしてください。')
        return

    def set_indicate_buttton(self):
        button = ttk.Button(self,
                            text = '共円指摘',
                            style='Sub.TButton',
                            command= lambda : self.on_click_indicate_button()
                            )
        button.grid(row=ROW_NUM+1, column=0, columnspan = ROW_NUM//2,rowspan = 1 , 
                    sticky=(N, S, E, W), padx=0,pady=0)

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def are_these_Kyoen(search_list): #search_list = [(x1,y1),(),(),()]
    '''
    共円かどうか判定
    '''
    x1,y1 = search_list[0]
    x2,y2 = search_list[1]
    x3,y3 = search_list[2]
    x4,y4 = search_list[3]
    a = complex(x1,y1)
    b = complex(x2,y2)
    c = complex(x3,y3)
    d = complex(x4,y4)
    
    if (a-b)*(a-c)*(a-d)*(b-c)*(b-d)*(c-d) == 0:
        return False

    z = ((d-a)*(b-c))/((b-a)*(d-c))

    if z.imag == 0:
        return True
    else:
        return False
    

def find_Kyoen(x, y, prot_list):
    '''
    (x, y)が共円候補地かどうか判定
    '''
    N = len(prot_list)
    stack = [(x,y)]
    for i in range(N-2):
        for j in range(i+1, N-1):
            for k in range(j+1, N):
                stack = [(x,y)]
                stack.append(prot_list[i])
                stack.append(prot_list[j])
                stack.append(prot_list[k])
                if are_these_Kyoen(stack):
                    return stack
    return []



def main():
    """
    メイン処理
    """
    objTk = Tk()
    objTk.title('共円')
    objTk.geometry('600x650')
    BoardUI(objTk)
    objTk.mainloop()


if __name__ == '__main__':
    main()
