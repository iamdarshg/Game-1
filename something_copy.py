
def solvemaze(maze,image):

    i = 0
    j = 0
    forkprocessor = []
    path = []
    while not (i == len(maze) - 1 and j == len(
            maze) - 1):  #make while true loop and have condition in here to break; and to add to incomplete path
        #print(i, j)
        #print("path = ", path)
        #print(forkprocessor)
        #print(i,j)
        if maze[i][j][0] == -2:
            i = forkprocessor[len(forkprocessor) - 3]
            j = forkprocessor[len(forkprocessor) - 2]
            #print("Reached dead end, coordinates of previous viable fork are", i, j)
            #print("This is path", path)
            while not (i == path[len(path) - 3] and j == path[
                len(path) - 2]):  # POPs path if i and j values are not equal; previous fork
                #print("Removing last fork from path as all paths from that one have been explored")
                path.pop()
                path.pop()
                path.pop()
            #  print("done,",path)
            if forkprocessor[len(forkprocessor) - 1]:  #==True
                path.pop()
                path.append(maze[i][j][1])
                if len(maze[i][j]) == 2:
                    #print("Trying to POP forkprocessor",forkprocessor)
                    forkprocessor.pop()
                    forkprocessor.pop()
                    forkprocessor.pop()
                    #print("done?",forkprocessor)
                else:
                    forkprocessor[len(forkprocessor) - 1] = False
                if maze[i][j][1] == 0:
                    i = i - 1
                elif maze[i][j][1] == 1:
                    i = i + 1
                elif maze[i][j][1] == 3:
                    j = j + 1
                else:
                    j = j - 1
            else:
                path.pop()
                path.append(maze[i][j][2])
                forkprocessor.pop()
                forkprocessor.pop()
                forkprocessor.pop()
                if maze[i][j][2] == 0:
                    i = i - 1
                elif maze[i][j][2] == 1:
                    i = i + 1
                elif maze[i][j][2] == 3:
                    j = j + 1
                else:
                    j = j - 1
            continue

        if len(maze[i][j]) == 1:
            if maze[i][j][0] == 0:
                i = i - 1
            elif maze[i][j][0] == 1:
                i = i + 1
            elif maze[i][j][0] == 3:
                j = j + 1
            else:
                j = j - 1

        else:
            #print("found fork at ", i, j)
            path.append(i)
            path.append(j)
            path.append(maze[i][j][0])
            #print("New path = ", path)
            forkprocessor.append(i)
            forkprocessor.append(j)
            forkprocessor.append(
                True)  #second path - true. then remove it based on the length. else third path, and remove it immediately
            if maze[i][j][0] == 0:
                i = i - 1
            elif maze[i][j][0] == 1:
                i = i + 1
            elif maze[i][j][0] == 3:
                j = j + 1
            else:
                j = j - 1

    #print(forkprocessor)  #true means the second path has not been taken...
    #forkprocessor stores positions of forks, always takes first path.  when taking the second and last path, deletes this entry from forkprocessor
    #print(path)
    for i in range(len(path) - 1, -1, -1):
        if not ((i + 1) % 3 == 0):
            path.pop(i)

    #print(path)
    #print(i, j)

    i = 0
    j = 0

    while not (i==len(maze)-1 and j==len(maze)-1):
        image.putpixel((j + j + 1, i + i + 1), (0, 255, 0))
        if len(maze[i][j]) == 1:
            if maze[i][j][0] == 0:
                image.putpixel((j + j + 1, i + i), (0, 255, 0))
                i = i - 1
            elif maze[i][j][0] == 1:
                image.putpixel((j + j + 1, i + i + 2), (0, 255, 0))
                i = i + 1
            elif maze[i][j][0] == 3:
                image.putpixel((j + j + 2, i + i + 1), (0, 255, 0))
                j = j + 1
            else:
                image.putpixel((j + j, i + i + 1), (0, 255, 0))
                j = j - 1
        else:
            image.putpixel((j + j + 1, i + i + 1), (0, 255, 0))
            if path[0] == 0:
                image.putpixel((j + j + 1, i + i), (0, 255, 0))
                i = i - 1
            elif path[0] == 1:
                image.putpixel((j + j + 1, i + i + 2), (0, 255, 0))
                i = i + 1
            elif path[0] == 3:
                image.putpixel((j + j + 2, i + i + 1), (0, 255, 0))
                j = j + 1
            else:
                image.putpixel((j + j, i + i + 1), (0, 255, 0))
                j = j - 1
            path.pop(0)
    return image

