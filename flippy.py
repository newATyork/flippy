# Flippy (an "Othello" or "Reversi" clone)
# http://inventwithpython.com/blog
# By Al Sweigart al@inventwithpython.com

"""IMPORTANT NOTE: All of the "logic" part of this program (the code for the AI player and code that handles game play) is basically copied and pasted from the text-based Othello game that was featured in the "Invent Your Own Computer Games with Python" book (freely available at http://inventwithpython.com).

You might want to read through that code and chapter 15 of the book before looking through this code, because I really only cover the Pygame parts in the source code. http://inventwithpython.com/chapter15.html

Basically, this program == (old text-based othello program) - (text & keyboard stuff) + (Pygame graphics & mouse stuff).

You should compare the code between these two programs to see how you could go about reusing other people's code and giving it a new makeover.

This program was programmed for Python 3, but should be compatible with Python 2.
"""

import random
import sys
import pygame
from pygame.locals import *
import time

FPS = 10 # frames per second to update the screen
WINDOWWIDTH = 640 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels
SPACESIZE = 50 # width & height of each space on the board, in pixels
BOARDWIDTH = 8 # how many columns of spaces on the game board
BOARDHEIGHT = 8 # how many rows of spaces on the game board
WHITETILE = 'X' # an arbitrary but unique value
BLACKTILE = 'O' # an arbitrary but unique value
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (XMARGIN) or above and below (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

# Colors used in the game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 50, 255)
BROWN = (174, 94, 0)

BGCOLOR = BRIGHTBLUE # TODO change var name
BOARDBGCOLOR = GREEN # TODO change var name
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN


def main():
    global MAINCLOCK, MAINSURF, FONT, BIGFONT, BGIMAGE, BGIMAGE_RECT

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    MAINSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Flippy')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    # Set up the background image.
    boardImage = pygame.image.load('flippyboard.png')
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (XMARGIN, YMARGIN)
    BGIMAGE = pygame.image.load('flippybackground.png')
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(boardImage, boardImageRect)
    BGIMAGE_RECT = BGIMAGE.get_rect()

    # Run the main game.
    while playGame() == True:
        pass # The while loop does nothing but call playGame() until it returns False.


def playGame():
    # Plays a single game of reversi each time this function is called.

    # Reset the board and game.
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = whoGoesFirst()

    # Draw the starting board and ask the player what color they want to be.
    drawBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()

    # Make the text for the "New Game" and "Hints" buttons
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, BOARDBGCOLOR)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    hintsSurf = FONT.render('Hints', True, TEXTCOLOR, BOARDBGCOLOR)
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 8, 40)

    while True:
        # Keep looping for player and computer's turns.
        if turn == 'player':
            # Player's turn.
            if getValidMoves(mainBoard, playerTile) == []:
                # If it was set to be the player's turn but they can't move, then end the game.
                break
            move = None
            while move == None:
                # Keep looping until the player clicks on a valid space.

                # Determine if we should show a board with hints marked or not.
                if showHints:
                    boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                else:
                    boardToDraw = mainBoard

                # Process all events.
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                        terminate()
                    if event.type == MOUSEBUTTONUP:
                        # Handle mouse click events
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            # Start a new game
                            return True
                        elif hintsRect.collidepoint( (mousex, mousey) ):
                            # Toggle hints mode
                            showHints = not showHints
                        move = getSpaceClicked(mousex, mousey)
                        if move != None and not isValidMove(mainBoard, playerTile, move[0], move[1]):
                            move = None

                # Draw the game board.
                drawBoard(boardToDraw)
                drawInfo(boardToDraw, playerTile, computerTile, turn)

                # Draw the "New Game" and "Hints" buttons.
                MAINSURF.blit(newGameSurf, newGameRect)
                MAINSURF.blit(hintsSurf, hintsRect)

                MAINCLOCK.tick(FPS)
                pygame.display.update()

            # Make the move and end the turn.
            makeMove(mainBoard, playerTile, move[0], move[1], True)
            if getValidMoves(mainBoard, computerTile) != []:
                # Only set it to be the computer's turn if it can make a move.
                turn = 'computer'

        else:
            # Computer's turn.
            if getValidMoves(mainBoard, computerTile) == []:
                # If it was set to be the computer's turn but they can't move, then end the game.
                break

            # Draw the board.
            drawBoard(mainBoard)
            drawInfo(mainBoard, playerTile, computerTile, turn)

            # Draw the "New Game" and "Hints" buttons.
            MAINSURF.blit(newGameSurf, newGameRect)
            MAINSURF.blit(hintsSurf, hintsRect)

            # Pause the game for bit to give the illusion that the computer is thinking.
            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            # Make the move and end the turn.
            x, y = getComputerMove(mainBoard, computerTile)
            makeMove(mainBoard, computerTile, x, y, True)
            if getValidMoves(mainBoard, playerTile) != []:
                # Only set it to be the player's turn if they can make a move.
                turn = 'player'

    # Display the final score.
    drawBoard(mainBoard)
    scores = getScoreOfBoard(mainBoard)

    # Determine the text of the message to display.
    if scores[playerTile] > scores[computerTile]:
        text = 'You beat the computer by %s points! Congratulations!' % \
               (scores[playerTile] - scores[computerTile])
    elif scores[playerTile] < scores[computerTile]:
        text = 'You lost. The computer beat you by %s points.' % \
               (scores[computerTile] - scores[playerTile])
    else:
        text = 'The game was a tie!'

    textSurf = FONT.render(text, True, TEXTCOLOR, BGCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    MAINSURF.blit(textSurf, textRect)

    # Display the "Play again?" text with Yes and No buttons.
    text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, BGCOLOR)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

    # Make "Yes" button.
    yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, BGCOLOR)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

    # Make "No" button.
    noSurf = BIGFONT.render('No', True, TEXTCOLOR, BGCOLOR)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

    while True:
        # Process events until the user clicks on Yes or No.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yesRect.collidepoint( (mousex, mousey) ):
                    return True
                elif noRect.collidepoint( (mousex, mousey) ):
                    return False
        MAINSURF.blit(textSurf, textRect)
        MAINSURF.blit(text2Surf, text2Rect)
        MAINSURF.blit(yesSurf, yesRect)
        MAINSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def translateBoardToPixelCoord(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def animateTileChange(board, tilesToFlip, tileColor, additionalTile):
    # Draw the additional tile that was just laid down. (We do this because
    # otherwise we'd have to completely redraw the board & the board info.)
    if tileColor == WHITETILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(MAINSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    if tileColor == WHITETILE:
        m = 0
    else:
        m = 255
    for i in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if i > 255:
            i = 255
        elif i < 0:
            i = 0
        color = tuple([abs(m - i)] * 3)
        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(MAINSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()


def drawBoard(board):
    # Draw background of board.
    MAINSURF.blit(BGIMAGE, BGIMAGE_RECT)

    # Draw grid lines of the board.
    for x in range(BOARDWIDTH + 1):
        # Draw the horizontal lines.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(MAINSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        # Draw the vertical lines.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(MAINSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Draw the black & white tiles or hint spots.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITETILE or board[x][y] == BLACKTILE:
                if board[x][y] == WHITETILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(MAINSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == '.':
                pygame.draw.rect(MAINSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))


def getSpaceClicked(mousex, mousey):
    # Return a list with two integers [x, y] of the board space coordinates where
    # the mouse was clicked. Or returns None if the mouse click is not in any space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XMARGIN and \
               mousex < (x + 1) * SPACESIZE + XMARGIN and \
               mousey > y * SPACESIZE + YMARGIN and \
               mousey < (y + 1) * SPACESIZE + YMARGIN:
                return [x, y]
    return None


def drawInfo(board, playerTile, computerTile, turn):
        # Draws the game info at the bottom of the screen (scores and whose turn it is)
        scores = getScoreOfBoard(board)
        scoreSurf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), True, TEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
        MAINSURF.blit(scoreSurf, scoreRect)


def resetBoard(board):
    # Blanks out the board it is passed, except for the original starting position.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = ' '

    # Starting pieces:
    board[3][3] = WHITETILE
    board[3][4] = BLACKTILE
    board[4][3] = BLACKTILE
    board[4][4] = WHITETILE


def getNewBoard():
    # Creates a brand new, blank board data structure.
    board = []
    for i in range(BOARDWIDTH):
        board.append([' '] * BOARDHEIGHT)

    return board


def isValidMove(board, tile, xstart, ystart):
    # Returns False if the player's move on space xstart, ystart is invalid.
    # If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
    if board[xstart][ystart] != ' ' or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile # temporarily set the tile on the board.

    if tile == WHITETILE:
        otherTile = BLACKTILE
    else:
        otherTile = WHITETILE

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection # first step in the direction
        y += ydirection # first step in the direction
        if isOnBoard(x, y) and board[x][y] == otherTile:
            # There is a piece belonging to the other player next to our piece.
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y): # break out of while loop, then continue in for loop
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the tiles along the way.
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = ' ' # restore the empty space
    if len(tilesToFlip) == 0: # If no tiles were flipped, this is not a valid move.
        return False
    return tilesToFlip


def isOnBoard(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


def getBoardWithValidMoves(board, tile):
    # Returns a new board with . marking the valid moves the given player can make.
    dupeBoard = getBoardCopy(board)

    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = '.'
    return dupeBoard


def getValidMoves(board, tile):
    # Returns a list of [x,y] lists of valid moves for the given player on the given board.
    validMoves = []

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves


def getScoreOfBoard(board):
    # Determine the score by counting the tiles. Returns a dictionary with keys WHITETILE and BLACKTILE.
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITETILE:
                xscore += 1
            if board[x][y] == BLACKTILE:
                oscore += 1
    return {WHITETILE:xscore, BLACKTILE:oscore}


def enterPlayerTile():
    # Draws the text and handles the mouse click events for letting the player
    # choose which color they want to be.
    # Returns [WHITETILE, BLACKTILE] if the player chooses to be White,
    # [BLACKTILE, WHITETILE] if Black.

    # Create the text.
    textSurf = FONT.render('Do you want to be white or black?', True, TEXTCOLOR, BGCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    xSurf = BIGFONT.render('White', True, TEXTCOLOR, BGCOLOR)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    oSurf = BIGFONT.render('Black', True, TEXTCOLOR, BGCOLOR)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return [WHITETILE, BLACKTILE]
                elif oRect.collidepoint( (mousex, mousey) ):
                    return [BLACKTILE, WHITETILE]

        # Draw the screen.
        MAINSURF.blit(textSurf, textRect)
        MAINSURF.blit(xSurf, xRect)
        MAINSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def whoGoesFirst():
    # Randomly choose the player who goes first.
    if random.randint(0, 1) == 0:
        return 'computer'
    else:
        return 'player'


def makeMove(board, tile, xstart, ystart, realMove=False):
    # Place the tile on the board at xstart, ystart, and flip any of the opponent's pieces.
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(board, tilesToFlip, tile, (xstart, ystart))

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True


def getBoardCopy(board):
    # Make a duplicate of the board list and return the duplicate.
    dupeBoard = getNewBoard()

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            dupeBoard[x][y] = board[x][y]

    return dupeBoard


def isOnCorner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)


def getComputerMove(board, computerTile):
    # Given a board and the computer's tile, determine where to
    # move and return that move as a [x, y] list.
    possibleMoves = getValidMoves(board, computerTile)

    # randomize the order of the possible moves
    random.shuffle(possibleMoves)

    # always go for a corner if available.
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    # Go through all the possible moves and remember the best scoring move
    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove


def terminate():
    # Remember to call pygame.quit() before sys.exit(), or else IDLE will hang
    # if you run this script from IDLE.
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()