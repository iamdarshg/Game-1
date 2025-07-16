import random
#import numpy as np
from PIL import Image

#makesure maze fits on screen

#n = 1000
#What is special about -2? indicates that cell has been visited

#maze = np.empty((n, n), dtype=object)
#for t in range(n):
 #   for x in range(n):
  #      maze[t][x] = [-1]


def mazegenerate(n):
    maze = [[[-1] for _ in range(n)] for _ in range(n)]


    i = 0  # x
    j = 0  # y

    # up = 0
    # down = 1
    # left = 2
    # right = 3
    arr = []
    count = 0
    temp = 0
    while count < (n * n):
        if count == (n * n) - 1:
            maze[i][j][0] = -2
            #print(i,j)
            break
        while True:
            #printmazey(i, j)
            arr = []  # resets arr to an empty array
            if j - 1 >= 0:
                if maze[i][j - 1][0] == -1:
                    arr.append(2)
            #print(i,j)
            if j + 1 < n:
                if maze[i][j + 1][0] == -1:
                    arr.append(3)
            #print(i,j)
            if i + 1 < n:
                if maze[i + 1][j][0] == -1:
                    arr.append(1)
            #print(i,j)
            if i - 1 >= 0:
                if maze[i - 1][j][0] == -1:
                    arr.append(0)
            #print(arr, " This is arr")
            #print()
            if len(arr) == 0:
                if maze[i][j][0] == -1:
                    maze[i][j][0] = -2
                try:
                    if j - 1 >= 0:
                        for g in range(0, len(maze[i][j - 1])):
                            #print(g, "j-1")
                            if maze[i][j - 1][g] == 3:
                                j = j - 1
                                raise Exception("")
                    if j + 1 < len(maze[i]):
                        for g in range(0, len(maze[i][j + 1])):
                            #print(g, "j+1")
                            if maze[i][j + 1][g] == 2:
                                j = j + 1
                                raise Exception("")
                    if i + 1 < len(maze):
                        for g in range(0, len(maze[i + 1][j])):
                            #print(g, "i+1")
                            if maze[i + 1][j][g] == 0:
                                i = i + 1
                                raise Exception("")
                    if i - 1 >= 0:
                        for g in range(0, len(maze[i - 1][j])):
                            #print(g, "i-1")
                            if maze[i - 1][j][g] == 1:
                                i = i - 1
                                raise Exception("")
                except Exception:
                    pass



            else:
                break

        temp = arr[random.randint(0, len(arr) - 1)]
        if maze[i][j][0] == -1:
            maze[i][j][0] = temp
        else:
            maze[i][j].append(temp)

        if temp == 0:
            i = i - 1
        elif temp == 1:
            i = i + 1
        elif temp == 3:
            j = j + 1
        else:
            j = j - 1
        count = count + 1

    #printmazey(-1,-1)
    #printmaze()
    n = n * 2
    image = Image.new('RGB', (n + 1, n + 1), color=(0, 0, 0))

    i = 0
    j = 0

    #in image.putpixel(), the j coordinate comes first. j,i. can use kinda the same i and j as for the array, its quite similar
    for ci in range(1, n, 2):
        j = 0
        for cj in range(1, n, 2):
            image.putpixel((cj, ci), (255, 255, 255))
            for g in range(len(maze[i][j])):
                if maze[i][j][g] == 0:
                    image.putpixel((cj, ci - 1), (255, 255, 255))  #for all, values of i and j are incremented
                elif maze[i][j][g] == 1:
                    image.putpixel((cj, ci + 1), (255, 255, 255))
                elif maze[i][j][g] == 2:
                    image.putpixel((cj - 1, ci), (255, 255, 255))
                elif maze[i][j][g] == 3:
                    image.putpixel((cj + 1, ci), (255, 255, 255))
            j = j + 1
        i = i + 1

    image.putpixel((n - 1, n - 1), (0, 255, 0))
    image.putpixel((1, 1), (255, 0, 0))
    #image = image.resize((2048, 2048), Image.NONE)
    #image.resize((2048, 2048), Image.NONE).save("E:\output3.png")
    return [image, maze]
