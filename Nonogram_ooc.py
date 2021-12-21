# -*- coding: utf-8 -*-
"""
This is a first attempt to rewrite the nonogram game in terms of objects.  

Created on Sun Dec 19 09:21:44 2021
@author: Stu
"""
from tkinter import *
import numpy as np
import random
import time


#----------------------------------------------
# Global variables

GAME_SIZE = 525
GAME_DIFFICULTY = 3 
BACKGROUND_COLOR = '#E5F0F1' #"white"
N = GAME_DIFFICULTY * 5
DX = GAME_SIZE/21
NODES = np.array([[7,15],[4,18],[1,20]])*DX
LABEL_WIDTH = np.array([[3, 4, 4]])*DX
IDX = GAME_DIFFICULTY-1
OFFSET = int((LABEL_WIDTH[0,IDX]+NODES[IDX,0])/DX)


#----------------------------------------------
# initialize game object
#----------------------------------------------
class nonogame():
    
    # ------------------------------------------------------------------
    # Initialization Functions:
    # ------------------------------------------------------------------
    
    def __init__(self):
        
        # initialize Game window
        self.window = Tk()
        self.window.title('Nonogram puzzle')
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.resizable(height=False, width=False)
        
        # define upper label area
        self.top_label = Label(self.window, text="Nonogram Puzzle", font=("Century Schoolbook", 26), height=3, bg=BACKGROUND_COLOR)
        self.top_label.pack(side='top')
        
        #scoring label
        self.score_label = Label(self.window, text="You have found 0 so far!",
                    font=("Century Schoolbook", 14), fg='black', bg = BACKGROUND_COLOR)
        self.score_label.pack(side='top')
        
        # define gameboard area
        self.board_area = Canvas(self.window, width=GAME_SIZE, height=GAME_SIZE)
        self.board_area.pack()
        
        # bind board area button presses
        self.board_area.bind('<Button>', self.click)
        
        # define lower label/button area
        self.lower_area = Frame(self.window)
        self.lower_area.pack(side='bottom', fill=BOTH, expand=True, pady=30, padx=70)
        
        #game buttons
        self.new_game_button = Button(self.lower_area, text="New Game", font=("Century Schoolbook", 16), 
                                      command=self.draw_select_difficulty_page).pack(in_=self.lower_area, side=LEFT)
        self.reset_button = Button(self.lower_area, text="Reset board", font=("Century Schoolbook", 16), 
                                   command=self.reset_game).pack(in_=self.lower_area, side=RIGHT)
        self.submit_button = Button(self.lower_area, text="Submit", font=('Century Schoolbook', 16), 
                                    command=self.update_score).pack(in_=self.lower_area)
        
        #prompt user to select game difficulty
        self.draw_select_difficulty_page()
        
    
    def mainloop(self):
        self.window.mainloop()
     
    #--------------------------------------------------------------------------
    # Drawing methods
    #--------------------------------------------------------------------------
    
    def draw_game_board(self):
        
        # clear the game area
        self.board_area.delete("all")
        self.board_area.update()
        
        # game area outline
        game_xy = [2, 2, GAME_SIZE, 2, GAME_SIZE, GAME_SIZE, 2, GAME_SIZE] 
        self.board_area.create_polygon(game_xy, outline='#8e743d', fill='#f0d8c9')
         
        #draw board area outline
        global IDX        
        bxy = [NODES[IDX,0],NODES[IDX,0], #top left
               NODES[IDX,1],NODES[IDX,0], #top right
               NODES[IDX,1],NODES[IDX,1], #bottom right
               NODES[IDX,0],NODES[IDX,1]] #bottom left
        self.board_area.create_polygon(bxy, outline='black', fill='white')
        
        #draw game board
        for i in range(N+1):
            
            #draw board lines to board
            IDX = GAME_DIFFICULTY-1
            self.board_area.create_line(NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX,NODES[IDX,0],
                                        NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX,NODES[IDX,1],width=1+int(i%5==0))
            self.board_area.create_line(NODES[IDX,0],NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX,
                                        NODES[IDX,1],NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX,width=1+int(i%5==0))
           
            #add labels to board area
            if i<N:
                self.board_area.create_text(NODES[IDX,0]+LABEL_WIDTH[0,IDX]-0.25*DX,NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX+0.5*DX,
                                        font=("CenturySchoolbook", 11),text=self.h_strings[i], anchor='e')
                self.board_area.create_text(NODES[IDX,0]+LABEL_WIDTH[0,IDX]+i*DX+0.5*DX,NODES[IDX,0]+LABEL_WIDTH[0,IDX]-0.125*DX, 
                                        font=("CenturySchoolbook", 11-int(2*len(self.v_strings[i-5])>10)),text=self.v_strings[i], anchor='s')

    def draw_board_token(self, logical_position, symbol):
        #fetch the grid position for drawing the symbol grid_pos=[x0,y0,x1,y1]
        grid_pos = self.convert_logical_to_grid_position(logical_position) 
        
        #clear the square 
        self.board_area.create_rectangle(grid_pos[0],grid_pos[1],grid_pos[2],grid_pos[3], 
                                                 fill=BACKGROUND_COLOR, outline=BACKGROUND_COLOR)
        
        if symbol == 1: #if this was a left click, draw a black box
            self.board_area.create_rectangle(grid_pos[0],grid_pos[1],grid_pos[2],grid_pos[3], fill='black')
        elif symbol == -1: #if this was a right click, draw an x
            self.board_area.create_line(grid_pos[0],grid_pos[1],grid_pos[2],grid_pos[3], width=3, fill='red')
            self.board_area.create_line(grid_pos[0],grid_pos[3],grid_pos[2],grid_pos[1], width=3, fill='red')
                
    def draw_select_difficulty_page(self):
        self.done_selecting_difficulty = False
        
        #clear the board area
        self.board_area.delete('all')
        
        #generate node position vars for difficulty buttons
        x = np.array([1/4, 3/4])*GAME_SIZE
        y = np.array([1/10, 3/10, 2/5, 3/5, 7/10, 9/10])*GAME_SIZE

        #draw difficulty buttons
        self.board_area.create_rectangle(x[0],y[0],x[1],y[1], fill='green', outline='white')
        self.board_area.create_text(int((x[0]+x[1])/2),int((y[0]+y[1])/2), font=('Century Schoolbook', 20),
                        text="Easy: 5 x 5", anchor='c', fill='white')
        self.board_area.create_rectangle(x[0],y[2],x[1],y[3], fill='blue', outline='white')
        self.board_area.create_text(int((x[0]+x[1])/2),int((y[2]+y[3])/2), font=('Century Schoolbook', 20),
                        text="Medium: 10 x 10", anchor='c', fill='white')
        self.board_area.create_rectangle(x[0],y[4],x[1],y[5], fill='grey', outline='white')
        self.board_area.create_text(int((x[0]+x[1])/2),int((y[4]+y[5])/2), font=('Century Schoolbook', 20),
                        text="Hard: 15 x 15", anchor='c', fill='white')
        
        #refresh board area
        self.board_area.update()
        
    #--------------------------------------------------------------------------
    # Game intitialization methods
    #--------------------------------------------------------------------------
    
    def fetch_strings(self):
        #boolean to report whether an empty row or column exists
        self.empty_row_col = False
        
        #generate h and v arrays to analyze
        temp_v = np.array(self.solution_board)
        temp_h = temp_v.transpose()
                
        #generate vars to hold the row and column labels
        if N == 15:
            self.h_strings = ['','','','','','','','','','','','','','','']
            self.v_strings = ['','','','','','','','','','','','','','','']
        elif N == 10:
            self.h_strings = ['','','','','','','','','','']
            self.v_strings = ['','','','','','','','','','']
        else:
            self.h_strings = ['','','','','']
            self.v_strings = ['','','','','']
         
        #loop through N and generate row and column labels from solution array    
        for row in range(N):
            th = [0 for n in range(N)]  
            tv = [0 for n in range(N)]
            pv = 0; ph = 0
            
            for col in range(N):
                
                #build th variable to hold horizontal count vals
                if temp_h[row,col] == 1:
                    th[ph] += 1
                elif temp_h[row,col] == 0:
                    if col == 0 or temp_h[row,col-1]==0:
                        pass
                    else:
                        ph+=2
                        
                #build th variable to hold vertical count vals
                if temp_v[row,col] == 1:
                    tv[pv] += 1
                elif temp_v[row,col] == 0:
                    if col == 0 or temp_v[row,col-1]==0:
                        pass
                    else:
                        pv+=2
            
            #convert count var to string var of proper formatting
            h_str = ''; v_str = ''             
            for i in range(N):
                if tv[i] != 0:
                    if sum(tv[i+1:])==0:
                        v_str += str(tv[i])
                    else:
                        v_str += str(tv[i]) + '\n'
                if th[i] != 0:#if this is not a zero...
                    if sum(th[i+1:])==0:#and if there are no more non-zeros...
                        h_str += str(th[i]) #add this to the string
                    else: #otherwise...
                        h_str += str(th[i]) + ' '
            
            #note if there are any blank rows or cols or too many islands
            if len(h_str)==0 or len(v_str)==0 or len(v_str)>11:
                self.empty_row_col = True
             
            #assign the string values to game object for ease of access     
            self.h_strings[row] = h_str            
            self.v_strings[row] = v_str 
            
    def generate_new_board(self):
        #-- generates new game board using random number generator. Verifies adequate density
        done = False
        
        #generate board
        while not done:
            self.solution_board = np.zeros((N,N),dtype=int)
            for row in range(N):
                for col in range(N):
                    self.solution_board[row][col] = random.randint(0, 1)
            #limit density range
            if 0.85 >= self.solution_board.sum()/(N*N) >= 0.5:
                self.fetch_strings()
                if self.empty_row_col == False:
                    done = True
        
        #populate game vars
        self.total = self.solution_board.sum()
        self.solution_board = self.solution_board.transpose()

    def reset_game(self):
        #generate variable to hold current board status
        self.game_board = np.zeros((N, N), dtype='int')
        
        #reset game variables
        self.errors = 0
        self.game_over = False   
        
        #draw new game board
        self.draw_game_board()
        
        #update score for board
        self.update_score()  
        
    def reset_game_vars(self, difficulty):
        global GAME_DIFFICULTY, N, IDX, OFFSET
        GAME_DIFFICULTY = difficulty
        N = GAME_DIFFICULTY * 5
        IDX = GAME_DIFFICULTY-1
        OFFSET = int((LABEL_WIDTH[0,IDX]+NODES[IDX,0])/DX)      
        
    def start_new_game(self):               
        #generate new solution board
        self.generate_new_board()
        
        #reset game board and variables
        self.reset_game()
            
    #--------------------------------------------------------------------
    # logical methods
    #--------------------------------------------------------------------
    def convert_grid_to_difficulty(self, grid_position):
        if GAME_SIZE*3/4 >= grid_position[0] >= GAME_SIZE/4:
            if GAME_SIZE*3/10 >= grid_position[1] >= GAME_SIZE/10:
                return(1)
            elif GAME_SIZE*3/5 >= grid_position[1] >= GAME_SIZE*2/5:
                return(2)
            elif GAME_SIZE*9/10 >= grid_position[1] >= GAME_SIZE*7/10:
                return(3)
        return(0)
        
    def convert_grid_to_logical_position(self, grid_position):
        if NODES[IDX,1] >= grid_position[0] >= NODES[IDX,0]+LABEL_WIDTH[0,IDX]:
            if NODES[IDX,1] >= grid_position[1] >= NODES[IDX,0]+LABEL_WIDTH[0,IDX]:
                return np.array([grid_position[0]/DX-OFFSET, grid_position[1]/DX-OFFSET], dtype=int)
            else:
                return np.array([99,99], dtype=int)
        
    def convert_logical_to_grid_position(self, logical_position):       
        #choose line width var offset
        off = [0,0]
        for i in range(1):
            if logical_position[i] == 4 or logical_position[i] == 9 or logical_position[i] == 14:
                off[i] = 1          
        
        return np.array([(logical_position[0]+OFFSET)*DX+DX/8+1, (logical_position[1]+OFFSET)*DX+DX/8+1, 
                         (logical_position[0]+OFFSET+1)*DX-DX/8-off[0], (logical_position[1]+OFFSET+1)*DX-DX/8-off[1]], dtype=int)
    
    #---------------------------------------------------------------------
    # gameplay methods
    #---------------------------------------------------------------------    
    def click(self, event):
        grid_position = [event.x, event.y]
        if self.done_selecting_difficulty:
            logical_position = self.convert_grid_to_logical_position(grid_position)
            if logical_position[0]!=99:
                if not self.game_over:
                    if event.num == 1:
                        self.update_game_board(logical_position, 1)
                        # self.process_move(logical_position, 1)
                    elif event.num == 3:
                        self.update_game_board(logical_position, -1)
                        # self.process_move(logical_position, -1)
        else:
            difficulty = self.convert_grid_to_difficulty(grid_position)
            if difficulty:
                self.done_selecting_difficulty=True
                self.reset_game_vars(difficulty)
                self.start_new_game()
     
    def update_game_board(self, logical_position, symbol):        
        #choose game_board symbol based on previous value
        if self.game_board[logical_position[1],logical_position[0]]!=symbol: 
            pass
        else:
            symbol = 0
        
        #update game board variable and draw symbol
        self.game_board[logical_position[1],logical_position[0]]=symbol
        self.draw_board_token(logical_position,symbol)
    
    def update_score(self):        
        #count the errors and found tiles
        found = 0; errors = 0
        for row in range(N):
            for col in range(N):
                #print(self.game_board[row,col],",",self.solution_board[row,col])
                if self.game_board[row, col]==1 and self.game_board[row,col] != self.solution_board[row,col]:
                    errors += 1
                elif self.game_board[row, col]==-1 and self.solution_board[row,col]==1:
                    errors += 1
                elif self.game_board[row, col]==1 and self.game_board[row,col] == self.solution_board[row,col]:
                    found += 1

        #left = self.total - found
        if errors > 0:
            self.score_label.config(text="There are errors in your solution", fg='red', bg = BACKGROUND_COLOR)
            self.display_error_message()
        else:
            if found == self.total:
                self.game_over = True
                self.score_label.config(text="You won! Congratulations!", fg='blue', bg = BACKGROUND_COLOR)
            else:
                self.score_label.config(text="You have found " + str(found) + "/" + str(self.total) + " so far!", fg='blue', bg = BACKGROUND_COLOR)
     
    def display_error_message(self):
        self.errors += 1
        
        start_time = time.time()
        delay = 2
        
        error_message_text = ''
        for i in range(self.errors):
            error_message_text += "X"
            
        #display the error message
        error_message = self.board_area.create_text(GAME_SIZE/2,GAME_SIZE/2, font=("Times", 140),
                        text=error_message_text, anchor='c', fill='red')        
        self.board_area.update()
        
        #pause for dramatic effect
        while True:
            current_time = time.time()
            if (current_time-start_time)>delay:
                break
            
        #remove error message
        self.board_area.delete(error_message)
        
        #check if game over        
        if self.errors == 3:
            self.game_over = True
            self.board_area.delete('all')
            self.board_area.create_text(GAME_SIZE/2,GAME_SIZE/2, font=("Times", 60),
                        text="GAME OVER\nYou lost", anchor='c', fill='red', justify='center')
            
game_instance = nonogame()
game_instance.mainloop()




















