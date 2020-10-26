# Author: Sam0fc
# Date: 2020-10-26
# Program: Solving the n-puzzle
# Description: Solves a sliding tile puzzle using BFS, DFS and a bi-directional BFS.

# input filepath,
# @return full game state, as a tuple of state and size
def LoadFromFile(filepath):
    state,N = FileRead(filepath)
    if parseList(state):
        if VerifyList(state,N):
            return state,N

#input a function, and performs some caching
def memoize(f):
    cache = {}
    def g(x):
        if x not in cache:
            cache[x] = f(x)
        return cache[x]
    return g

#Memoized function, takes in the size, and returns the end state.
@memoize
def MakeGoal(N):
    number = 1
    goal = []
    for i in range(N):
        row = []
        for j in range(N):
            row.append(number)
            number += 1
        goal.append(row)
    goal[N-1][N-1] = 0
    return goal

#Reads the file from a filepath to a 2D array with a size.
def FileRead(filepath):
    line_list=[]
    file=open(filepath,"r")
    for line in file:
        line_list.append(line.rstrip('\n').split("\t"))
    N = int(line_list.pop(0)[0])
    return line_list,N

#Takes 2D array of strings, and turns it into ints, replacing * with 0. Verifies that they are ints.
def parseList(state):
    for row in state:
        for j,item in enumerate(row):
            if item == "*":
                row[j] = 0
            else:
                try:
                    row[j]=int(item)
                except:
                    print("Invalid Input, labels are not integers")
                    return False
    return True

#Takes in a list to test and a size.
#Returns true if it is a valid Input or false if the shape is wrong or the labels are incorrect
def VerifyList(test_list,N):
    if len(test_list) != N:
        print("Too many rows")
        return False
    label_list = []
    for i in test_list:
        if len(i) != N:
            print("Too many columns")
            return False
        for j in i:
            label_list.append(j)
    if sorted(label_list) != list(range((N**2))) :
        print("Incorrect Labels or Missing Gap")
        return False
    return True

#Computes neighbours in the 2D array, taking in the full game state, and returning a list of tuples of moves and gamestates.
def ComputeNeighbors(full_state):
    state, N = full_state
    out_list = []
    for i,row in enumerate(state):
        for j,value in enumerate(row):
            if value == 0:
                if j-1>=0:
                    out_list.append((state[i][j-1],SwapIn(state,i,j,i,j-1)))
                if j+1<N:
                    out_list.append((state[i][j+1],SwapIn(state,i,j,i,j+1)))
                if i-1>=0:
                    out_list.append((state[i-1][j],SwapIn(state,i,j,i-1,j)))
                if i+1<N:
                    out_list.append((state[i+1][j],SwapIn(state,i,j,i+1,j)))
    return out_list

#Swaps 2 locations in a 2d array, given the array and the coordinates
def SwapIn(state,row1,col1,row2,col2):
    new_state = [row[:] for row in state]
    oregano = new_state[row1][col1]
    new_state[row1][col1] = new_state[row2][col2]
    new_state[row2][col2] = oregano
    return new_state

#Tests agains the made goal.
def IsGoal(full_state):
    state, N = full_state
    goal = MakeGoal(N)
    return state == goal

#Implements breath first search, with optimisation of storing frontier seperately, as you do not have to perform len.
def BFS(full_state):
    state,N = full_state
    tuple_state = tuple(map(tuple,state))
    frontier = [state]
    lenFrontier = 1
    discovered = set(tuple_state)
    parents = {tuple_state: None}
    while lenFrontier > 0:
        current_state = frontier.pop(0)
        lenFrontier -= 1
        discovered.add(tuple(map(tuple,current_state)))
        if IsGoal((current_state,N)):
            return FindParentPath(current_state,parents)
        for moved, neighbor in ComputeNeighbors((current_state,N)):
            tuple_neighbour = tuple(map(tuple,neighbor))
            if tuple_neighbour not in discovered:
                frontier.append(neighbor)
                lenFrontier += 1
                discovered.add(tuple_neighbour)
                parents.update({tuple_neighbour:(moved,current_state)})
    print("Unsolvable.")

#Depth first search
def DFS(full_state):
    state,N = full_state
    tuple_state = tuple(map(tuple,state))
    frontier = [state]
    lenFrontier = 1
    discovered = set(tuple_state)
    parents = {tuple_state: None}
    while lenFrontier > 0:
        current_state = frontier.pop(0)
        lenFrontier -= 1
        discovered.add(tuple(map(tuple,current_state)))
        if IsGoal((current_state,N)):
            return FindParentPath(current_state,parents)
        for moved, neighbor in ComputeNeighbors((current_state,N)):
            tuple_neighbour = tuple(map(tuple,neighbor))
            if tuple_neighbour not in discovered:
                frontier.insert(0,neighbor)
                lenFrontier += 1
                discovered.add(tuple_neighbour)
                parents.update({tuple_neighbour:(moved,current_state)})
    print("Unsolvable.")

#Bi-directional breath first search
def BDS(full_state):
    state,N = full_state
    tuple_state = tuple(map(tuple,state))

    goal = MakeGoal(N)
    tuple_goal = tuple(map(tuple,goal))

    frontier = [state]
    discovered = set(tuple_state)
    parents = {tuple_state: None}

    frontier_back = [goal]
    discovered_back = set(tuple_goal)
    parents_back = { tuple_goal : None}

    while (( len(frontier) > 0) and (len(frontier_back) > 0)):
        current_state = frontier.pop()
        discovered.add(tuple(map(tuple,current_state)))
        if tuple(map(tuple,current_state)) in discovered_back:
            return BDSParents(current_state,parents,parents_back)
        for moved, neighbor in ComputeNeighbors((current_state,N)):
            tuple_neighbour = tuple(map(tuple,neighbor))
            if tuple_neighbour not in discovered:
                frontier.insert(0,neighbor)
                discovered.add(tuple_neighbour)
                parents.update({tuple_neighbour:(moved,current_state)})
                if tuple_neighbour in discovered_back:
                    return BDSParents(tuple_neighbour,parents,parents_back)

        current_state = frontier_back.pop()
        discovered_back.add(tuple(map(tuple,current_state)))
        if tuple(map(tuple,current_state)) in discovered:
            return BDSParents(current_state,parents,parents_back)
        for moved, neighbor in ComputeNeighbors((current_state,N)):
            tuple_neighbour = tuple(map(tuple,neighbor))
            if tuple_neighbour not in discovered_back:
                frontier_back.insert(0,neighbor)
                discovered_back.add(tuple_neighbour)
                parents_back.update({tuple_neighbour:(moved,current_state)})
                if tuple_neighbour in discovered:
                    return BDSParents(tuple_neighbour,parents,parents_back)
    print("Unsolvable.")

#Takes the two directions from Bi-directional search as combines the paths into one path, from start to end.
def BDSParents(current_state,parents,parents_back):
    path = (FindParentPath(current_state,parents))
    back_path = (list(reversed(FindParentPath(current_state,parents_back))))
    path.extend(back_path)
    return path

#Given a dictionary of parents and the current (end) state, finds the path back to the start, and returns as a list of strings.
def FindParentPath(current_state,parents):
    out_list = []
    past_state = parents.pop(tuple(map(tuple,current_state)))
    while past_state != None:
        moved,current_state = past_state
        out_list.insert(0,moved)
        past_state = parents.pop(tuple(map(tuple,current_state)))
    return list(map(str,out_list))

print(BDS(LoadFromFile("test_file.txt")))
