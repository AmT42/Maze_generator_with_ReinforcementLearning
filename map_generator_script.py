# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 05:10:21 2022

@author: ahmet
"""
import numpy as np

class Maze:
    '''
    This is the main class to create maze.
    '''
    def __init__(self,agent,rows=4,cols=4):
        '''
        rows--> No. of rows of the maze
        cols--> No. of columns of the maze
        agent--> Our agent to train
        Need to pass just the two arguments. The rest will be assigned automatically
        maze_map--> Will be set to a Dicationary. Keys will be cells and
                    values will be another dictionary with keys=['E','W','N','S'] for
                    East West North South and values will be 0 or 1. 0 means that 
                    direction(EWNS) is blocked. 1 means that direction is open.
        grid--> A list of all cells
        path--> Shortest path from start(bottom right) to goal(by default top left)
                It will be a dictionary
        _win,_cell_width,_canvas -->    _win and )canvas are for Tkinter window and canvas
                                        _cell_width is cell width calculated automatically
        _agents-->  A list of aganets on the maze
        markedCells-->  Will be used to mark some particular cell during
                        path trace by the agent.
        _
        '''
        self.rows=rows
        self.cols=cols
        self.ix = agent.ix ## Pos of agent on rows 
        self.iy = agent.iy ## Pos of agent on cols
        
        #### I didn't use this feature but it keeps the beggening pos of our agent ####
        # self.visited_beg = []
        ## Saving all our visited starting point
        # if (self.ix,self.iy) not in self.visited_beg :
        #     self.visited_beg.append((self.ix,self.iy)) 
            
        self.eps = agent.eps ## eps determinated in agent class
        #### Starting point, end point, treasure point set at None in the beginning ####
        self.start= None 
        self.end=None
        self.treasure = None
        
        ## If there exist a path between start and end point set the false because there is no keypoint at the beggening 
        self.isFeasable = False 
        
        #### Path between Start - End / Start - Treasure / Treasure-End points ####
        self.path_SE=[]
        self.path_ST=[]
        self.path_TE=[]
        
        ### Set dist between Start and End to None ( there is no path in the beggening )
        self.dist_SE=None
        ### Dist Start Treasure
        self.dist_ST=None
        ### Dist Treasure End
        self.dist_TE=None
        
        
        
        ### Actions spaces
        self.actions = ["addTreasure","addStart","addEnd","editEast","editWest","editNorth","editSouth","goRight","goLeft","goUp",
        "goLeft"]
        ## Len of actions spaces        
        self.len_actions = len(self.actions)

        ## At the beggening there is 0 connection (all the walls are closed)
        self.nbConnection = 0
        
        ## Initialization of our maze matrix   
        self.maze_map = {}
        for x in range(self.rows):
            for y in range(self.cols):
                self.maze_map[x,y]={'E':0,'W':0,'N':0,'S':0}
        
        ## First initiale state with all the walls closed
        self.state = hash(str(self.maze_map)+str(self.start)+str(self.end)+str(self.treasure)+str((self.ix,self.iy)))
        
        ## Add our first state to our Q_hash and initialize all q_values to 0 for each action
        self.Q_hash = {self.state:[0]*self.len_actions}
        
        ## Keep visited_state at each game dict : {key = state : value = action(state)}
        self.visited_state = {self.state:0} 
        
        
    def __str__(self):
        """
        Return a (crude) string representation of the maze.
        Used only for debugging 
        """

        maze_rows = ['-' * self.rows * 2]
        for x in range(self.rows):
            maze_row = ['|']
            for y in range(self.cols):
                if x == 0 and y == 0:
                    maze_row.append('S')
                elif x == 3 and y == 3:
                    maze_row.append('E')
                elif x == 1 and y == 2:
                    maze_row.append('T')
                if not self.maze_map[x,y]['E']:
                    maze_row.append(' |')
                else:
                    maze_row.append('  ')
            maze_rows.append(''.join(maze_row))
            maze_row = ['|']
            for y in range(self.cols):
                if not self.maze_map[x,y]['N']:
                    maze_row.append('-+')
                else:
                    maze_row.append(' +')
            maze_rows.append(''.join(maze_row))
        
        return '\n'.join(maze_rows)
    def write_svg(self, filename):
        """
        Write an SVG image of the maze to filename.
        Used only for debugging  with a better grapgic interface
        """

        aspect_ratio = self.rows / self.cols
        # Pad the maze all around by this amount.
        padding = 10
        # Height and width of the maze image (excluding padding), in pixels
        height = 500
        width = int(height * aspect_ratio)
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = height / self.cols, width / self.rows

        def write_wall(ww_f, ww_x1, ww_y1, ww_x2, ww_y2):
            """Write a single wall to the SVG image file handle f."""

            print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                  .format(ww_x1, ww_y1, ww_x2, ww_y2), file=ww_f)

        # Write the SVG image file for maze
        with open(filename, 'w') as f:
            # SVG preamble and styles.
            print('<?xml version="1.0" encoding="utf-8"?>', file=f)
            print('<svg xmlns="http://www.w3.org/2000/svg"', file=f)
            print('    xmlns:xlink="http://www.w3.org/1999/xlink"', file=f)
            print('    width="{:d}" height="{:d}" viewBox="{} {} {} {}">'
                  .format(width + 2 * padding, height + 2 * padding,
                          -padding, -padding, width + 2 * padding, height + 2 * padding),
                  file=f)
            print('<defs>\n<style type="text/css"><![CDATA[', file=f)
            print('line {', file=f)
            print('    stroke: #000000;\n    stroke-linecap: square;', file=f)
            print('    stroke-width: 5;\n}', file=f)
            print(']]></style>\n</defs>', file=f)
            # Draw the "South" and "East" walls of each cell, if present (these
            # are the "North" and "West" walls of a neighbouring cell in
            # general, of course).
            for x in range(self.rows):
                for y in range(self.cols):
                    if not self.maze_map[y, x]['N']:
                        x1, y1, x2, y2 = x * scx, (y + 1) * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
                    if not self.maze_map[y, x]['E']:
                        x1, y1, x2, y2 = (x + 1) * scx, y * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
            # Draw the North and West maze border, which won't have been drawn
            # by the procedure above.
            print('<line x1="0" y1="0" x2="{}" y2="0"/>'.format(width), file=f)
            print('<line x1="0" y1="0" x2="0" y2="{}"/>'.format(height), file=f)
            print('</svg>', file=f)
            

    def reset(self):
        """
        Reset the env 
        """
        for x in range(self.rows):
            for y in range(self.rows):
                self.maze_map[x,y]={'E':0,'W':0,'N':0,'S':0}
        self.start = None
        self.end = None
        self.treasure= None
        self.ix , self.iy = np.random.randint(self.rows),np.random.randint(self.cols)

            
        self.path_SE=[]    
        self.path_ST=[]
        self.path_TE=[]   
        
        self.dist_SE = None
        self.dist_ST=None
        self.dist_TE=None
        
        self.map_representaion =[]
        for x in range(self.rows):
            for y in range(self.rows) :
                self.maze_map[x,y]={'E':0,'W':0,'N':0,'S':0}
         

        self.state = hash(str(self.maze_map)+str(self.start)+str(self.end)+str(self.treasure)+str((self.ix,self.iy)))
        ###Q_hash doesn't reset thus it can be possible that this state was already visited
        if not self.state in self.Q_hash.keys():
            self.Q_hash[self.state] = [0]*self.len_actions
        self.visited_state = {self.state:0}
        

            
        
    def take_actions(self,eps):
        """
        Choose randomly an action with proba eps otherwise take the best action given state : self.state
        """
        if np.random.random() < eps : 
            return np.random.randint(self.len_actions)
        else : 
            return np.argmax(self.Q_hash[self.state])
            
    def update_states(self,action_index):
        """
        Update state with respect to action_index then get the state from :str(self.maze_map)+str(self.start)+str(self.end)+str(self.treasure), and keep his hash 
        in self.state. self.state = hash(str(self.maze_map)+str(self.start)+str(self.end)+str(self.treasure))
        if it's a new state we add it on our Q_hash and then we initialize self.Q_hash [self.state] = [0]*number of possible actions 
        and we add self.state in our visited_state dictionary 
        """
        if self.actions[action_index] == "editEast" :
            self._Edit_East()
            
        elif self.actions[action_index] == "editWest" :
            self._Edit_West()
            
        elif self.actions[action_index] == "editNorth" :
            self._Edit_North()
            
        elif self.actions[action_index] == "editSouth" :
            self._Edit_South()
            
        elif self.actions[action_index] == "goRight" :
            self._Right()
            
        elif self.actions[action_index] == "goLeft" :
            self._Left()
            
        elif self.actions[action_index] == "goUp" :
            self._Up()
            
        elif self.actions[action_index] == "goDown" :
            self._Down()
            
        elif self.actions[action_index] == "addStart" :
            self._Add_Start()
            
        elif self.actions[action_index] == "addEnd" :
            self._Add_End()
        
        elif self.actions[action_index] == "addTreasure" :
            self._Add_Treasure()  
                     
        self.state = hash(str(self.maze_map)+str(self.start)+str(self.end)+str(self.treasure)+str((self.ix,self.iy)))
        ### If it's a new state add it on our Q_hash
        if not self.state in self.Q_hash.keys():
            self.Q_hash[self.state] = [0]*self.len_actions
        self.visited_state[self.state] = action_index
        

        self.update_path()
        
        
    def update_path(self):
        """     
        Update the path and distance between each end points 
        (We don't use isFeasable in our last release)
        """ 
        self.path_SE = self.BFS(self.start,self.end)
        self.path_ST = self.BFS(self.start,self.treasure)
        self.path_TE = self.BFS(self.treasure,self.end)
        
        if self.end in self.path_SE :
            # self.isFeasable = True
            self.dist_SE = len(self.path_SE) - 1
        
        if self.treasure in self.path_ST :
            self.dist_ST = len(self.path_ST) - 1
        
        
        if self.end in self.path_TE : # not 
            self.dist_TE = len(self.path_TE) - 1
        
        
        
        
   
    def _Down(self):
        """
        If the south wall is open, the agent moves down
        """ 
        if self.maze_map[self.ix,self.iy]['S'] == True :
            self.ix = self.ix-1  
            
            
            
    def _Up(self):
        if self.maze_map[self.ix,self.iy]['N'] == True :
            self.ix = self.ix+1  
            
            
            
    def _Left(self):
        if self.maze_map[self.ix,self.iy]['W'] == True :
            self.iy = self.iy-1  
            
            
            
    def _Right(self):
        if self.maze_map[self.ix,self.iy]['E'] == True :
            self.iy = self.iy+1 
    
    def _Add_Treasure(self):
        """
        Add a treasure point only if this cell is not already another key point
        """
        if self.start != (self.ix,self.iy) and self.end != (self.ix,self.iy)  :
            self.treasure = (self.ix, self.iy)
            
    def _Add_End(self):
        if self.start != (self.ix,self.iy) and self.treasure != (self.ix,self.iy) :
            self.end = (self.ix, self.iy)
    
    def _Add_Start(self):
        if self.end != (self.ix,self.iy) and self.treasure != (self.ix,self.iy) :
            self.start = (self.ix, self.iy)

                              
    def _Edit_East(self):
        '''
        Edit East Wall
        Open if it's close
        Close if it's open
        '''
        if self.maze_map[self.ix,self.iy]['E']==0:
            if self.iy+1<self.cols:
                self.maze_map[self.ix,self.iy]['E']=1
                self.maze_map[self.ix,self.iy+1]['W']=1
                self.nbConnection += 1
        else :
            if self.iy+1<self.cols:
                self.maze_map[self.ix,self.iy]['E']=0
                self.maze_map[self.ix ,self.iy+1]['W']=0
                self.nbConnection -= 1
            
    def _Edit_West(self):
        if self.maze_map[self.ix,self.iy]['W']==0 :
            if self.iy-1>=0:
                self.maze_map[self.ix,self.iy]['W']=1
                self.maze_map[self.ix,self.iy-1]['E']=1
                self.nbConnection += 1   
        else :
            if self.iy-1>=0:
                self.maze_map[self.ix,self.iy]['W']=0
                self.maze_map[self.ix,self.iy-1]['E']=0
                self.nbConnection -= 1
            
            
            
    def _Edit_North(self):
        if self.maze_map[self.ix,self.iy]['N']==0:
            if self.ix+1<self.rows:
                self.maze_map[self.ix,self.iy]['N']=1
                self.maze_map[self.ix+1,self.iy]['S']=1
                self.nbConnection += 1
        else :
            if self.ix+1<self.rows:
                self.maze_map[self.ix,self.iy]['N']=0
                self.maze_map[self.ix+1,self.iy]['S']=0
                self.nbConnection -= 1
            
            
    def _Edit_South(self):
        if self.maze_map[self.ix,self.iy]['S']==0:
            if self.ix-1>=0:
                self.maze_map[self.ix,self.iy]['S']=1
                self.maze_map[self.ix-1,self.iy]['N']=1
                self.nbConnection += 1
        else : 
            if self.ix-1>=0:
                self.maze_map[self.ix,self.iy]['S']=0
                self.maze_map[self.ix-1,self.iy]['N']=0
                self.nbConnection -= 1
               
                    
    def BFS(self,from_,to_):
        """
        Find path between from_ to_ Using BFS
        Returns:
            [List]: [Path(from_,to_)]
        """
        start = from_
        end = to_ 
        path = {}
        if from_ and to_ :
            frontier = [start]
            visited =[start]
            while len(frontier)>0 :
                currCell = frontier.pop(0) #first in first out
                for d in 'ESNW':
                    if self.maze_map[currCell][d] == True :
                        if d=="E":
                            childCell=(currCell[0],currCell[1]+1)
                        elif d=="S":
                            childCell=(currCell[0]-1,currCell[1])
                        elif d=="N":
                            childCell=(currCell[0]+1,currCell[1])
                        elif d=="W":
                            childCell=(currCell[0],currCell[1]-1) 
                        if childCell in visited:
                            continue
                        frontier.append(childCell)
                        visited.append(childCell)
                        path[childCell]=currCell
                        if currCell == end :
                            break
        ## keeping only the working path 
        if not end in path.keys() :
            return []
        fwdPath = {}
        
        cell = end
        while cell != start :
            fwdPath[path[cell]] = cell
            cell = path[cell]
        return [end] + list(fwdPath.keys())

               
    def give_reward(self,prev_nbConnection):#prev_isFeasable,prev_distSE,prev_nbConnection,prev_start,prev_end):
        
        """Function that gives rewards, this is the most customizable method in this class to make changes in performance.
           At first I used a complex reward function that you can see at the bottom of the function in the comments, then I realized that it worked quite well with these conditions. 
        Returns:
            [Int]: [Reward]
        """
        reward = 0
        
        if self.dist_SE :
            reward += self.dist_SE
        if self.dist_ST :
            reward += self.dist_ST 
        if self.dist_TE :
            reward += self.dist_TE 
            
        if all((self.dist_SE,self.dist_ST)):
            reward += (self.dist_SE + self.dist_ST)*2
        if all((self.dist_SE,self.dist_TE)):
            reward += (self.dist_SE + self.dist_TE)*2
        if all((self.dist_ST,self.dist_TE)):
            reward += (self.dist_ST + self.dist_TE)*2
            
        if all((self.dist_SE,self.dist_ST,self.dist_TE)):
            reward += (self.dist_SE + self.dist_ST + self.dist_TE)*3
            
        ## this conditions are good to avoid cluster of closed box
        if prev_nbConnection > self.nbConnection :
            reward -= 10
        elif prev_nbConnection < self.nbConnection :
            reward += 10
        # if not prev_start == True and self.start :
        #     reward +=4
        # ## the first time we add a starting point
        # if not prev_end == True and self.end :
        #     reward +=4
            
        # if self.isFeasable == True :
        #     ## The first time we reach distance(Start,end) == 4 we give a big reward and set reached_dist = True
        #     if self.dist_SE ==4 and self.reached_dist == False :
        #             reward += 100
        #             self.reached_dist = True
            
        #     ## if the maze was feasable this stade and the last stade the reward = difference between prev dist and new dist * 2        
        #     if prev_isFeasable == True :
        #         reward += (self.dist_SE - prev_distSE)*2
        #     ## if the maze wasn't feasable in the previous step we give +8reward
        #     elif prev_isFeasable == False :
        #         reward += 8
        
        # ## if the agent make the maze unfeasable from one step to the next we give -8 reward        
        # if prev_isFeasable == True and self.isFeasable == False :
        #     reward -= 5
        
        # ## if the agent make the maze unfeasable after  having reached the reached_dist we give a bigger penalty
        # if self.reached_dist==True and self.isFeasable == False:
        #     reward -= 8
        
        # ### small reward after increasing the number of connection in the maze
        return reward
    
    


class Agent():
    """
    Agent class that will live in our Maze env
    """
    def __init__(self,name="first_game", alpha=0.3, gamma=0.9, eps=0.10,rand_range=4):
        """
        alpha : learning rate 
        gamma : discount factor 
        eps : exploration/exploitation greedy score
        """
        self.name = name
        self.eps= eps
        self.gamma = gamma
        self.alpha = alpha
        self.ix = np.random.randint(rand_range)
        self.iy = np.random.randint(rand_range)
        self.reward = 0
    
    def reset_agent(self): 
        self.ix = np.random.randint(rand_range)
        self.iy = np.random.randint(rand_range)
        self.reward = 0
                                    
        return(self.ix,self.iy)
    
  
    
if __name__ == "__main__":
    """
    Training phase Using simple Belleman equations 
    """
    
    agent = Agent()
    maze = Maze(agent)
    j=0
    for epochs in range(10000):
        for step in range(500):
            ## choose best action with respect to current Q table 
            current_nbConnection = maze.nbConnection
            current_action_index = maze.take_actions(agent.eps)
            current_state = maze.state
            current_q_value = maze.Q_hash[current_state][current_action_index]
            
            ## update state with respect to  the current best action 
            maze.update_states(current_action_index)
            maze.update_path()
            
            ## the reward function is highly depending of the prev_state
            reward = maze.give_reward(current_nbConnection)
            
            ## new best action with respect to new Q table, we don't want to explore here so eps = 0
            new_action_index = maze.take_actions(0)
            new_state = maze.state 
            new_q_value = maze.Q_hash[new_state][new_action_index]
            ##belleman equation 
            temporal_difference = reward + agent.gamma * new_q_value - current_q_value
            
            maze.Q_hash[current_state][current_action_index] = current_q_value + (agent.alpha * temporal_difference)
        maze.reset()
        
    
"""
Testing our AI
Our algorithm does not really generate an infinite number of maze since we always give the same maze at the beginning with all the walls that are closed,
only the position of the agent in the beggening differ froms one game to an other but there is only 16 possibles differents starting pos for the agent.
Thus, our AI generates only a small number of different maze given our algorithm. But this is not a problem, we just need to make some modifications to have an "infinite" number of maze.
One solution could be to randomly select a starting state in Q_hash.keys() (we can only start with a state already visited). 
"""

"""
Testing our AI
Our algorithm does not really generate an infinite number of maze since we always give the same maze at the beginning with all the walls that are closed,
only the position of the agent in the beggening differ froms one game to an other but there is only 16 possibles differents starting pos for the agent.
Thus, our AI generates only a small number of different maze given our algorithm. But this is not a problem, we just need to make some modifications to have an "infinite" number of maze.
One solution could be to randomly select a starting state in Q_hash.keys() (we can only start with a state already visited). 
"""
list_=[]
for x in  range(maze.rows): 
        for y in range(maze.cols) :
                maze.reset()
                maze.ix, maze.iy = x,y
                for step in range(500):
                        ## choose best action with respect to current Q table
                        current_action_index = maze.take_actions(0)
                        ## update state with respect to  the current best action 
                        maze.update_states(current_action_index)
                filename1 = f'maze{maze.ix,maze.iy}.svg'
                maze.write_svg(filename1) 
                list_.append(maze)
                
### this part will be use in our React graphic interphace
for i in range(len(list_)):
        maze_copy = list_[i].maze_map.copy()
        for ix in  range(maze.rows): 
                for iy in range(maze.cols):
                        print(ix,iy)
                        ### this part will be use in our React graphic interphace
                        for d in 'EWSN':
                                maze_copy[(ix,iy)][d]=str(maze_copy[(ix,iy)][d])
                        maze_copy[str((ix,iy))]=maze_copy[(ix,iy)]
                        del maze_copy[(ix,iy)]
                        filename2 = f'string_maze_to_copy{ix,iy}.txt'
                        #with open(filename2, 'w') as f:
                        #        f.write(str(list([maze_copy,maze.start,maze.end,maze.treasure])))
                                
with open("Maze_sample.txt", 'w') as f:
        f.write(str(list([maze_copy,maze.start,maze.end,maze.treasure])))
