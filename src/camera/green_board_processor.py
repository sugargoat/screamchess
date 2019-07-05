import cv2
import numpy as np
import bisect
import math
import operator
from pyzbar import pyzbar
import zbarlight

class BoardImg:
    """
    Represents the image when rendered per-cell
    """
    image_pixel_width = 1280 # FIXME one global, also on each img - warn if off?
    image_pixel_height = 960
    num_squares = 8

    def __init__(self, img, cell_radius = None, debug = False):
        self.raw_img = img
        height, width, channels = img.shape
        self.height = height
        self.width = width
        if cell_radius is None:
            self.cell_radius = self.height / (self.num_squares)
        else:
            self.cell_radius = cell_radius

        self.cell_width = self.width/self.num_squares
        self.cell_height = self.height/self.num_squares

        self.centers = []
        for j in range(self.num_squares):
            # FIXME: I might have width and height backwards
            xs = [ i*self.cell_width for i in range(self.num_squares) ]
            ys = [ j*self.cell_height for i in range(self.num_squares) ]
            self.centers.extend(list(zip(xs, ys)))

        self.square_index = 0

        self.debug = debug

        self.contour_len_threshold = 10

    def get_circle_positions(self):
        green = self.raw_img[:,:,1]
        cv2.imshow("test", green)
        cv2.waitKey(0)

        ret,thresh = cv2.threshold(green,100,200,0)
        cv2.imshow("test", thresh)
        cv2.waitKey(0)

        mask = cv2.inRange(thresh, 100, 255)
        cv2.imshow("test", mask)
        cv2.waitKey(0)

        contours, heirarchy, question = cv2.findContours(
            mask, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

        image = mask[:]
        cnts = [c for c in contours if len(c) > self.contour_len_threshold]
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            denom = M["m00"]
            if denom == 0:
                continue
            cX = int(M["m10"] / denom)
            cY = int(M["m01"] / denom)

            # draw the contour and center of the shape on the image
            print('contour = ', c)
#            cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
            cv2.putText(image, "center", (cX - 20, cY - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


        cv2.imshow("test", image)

    def next_square(self):
        """Iterate through chessboard squares"""
        if self.debug:
            print("centers = ", self.centers)
        for index, (x, y) in enumerate(self.centers):
            ll = int(x)
            lr = int(x+self.cell_radius)
            ul = int(y)
            ur = int(y + self.cell_radius)
            cropped = self.raw_img[ul:ur, ll:lr]
            i = index % (self.num_squares)
            j = math.floor(index / self.num_squares)
            self.square_index += 1
            if self.debug:
                print("indices = ", ll, lr, ul, ur)
                cv2.imshow("current square", cropped)
            yield (i, j, cropped)

    def show(self):
        if self.debug:
            cv2.imshow("Processing Image", self.raw_img)

class GreenBoardProcessor:
    """
    The QR Board Processor Maintains an Internal State of the Board, and
    can update it, given an image
    """
    board_width = 8

    def __init__(self, cell_radius = None, debug = False):
        self.debug = debug
        self.cell_radius = cell_radius

    def update(self, captured_img):
        img = BoardImg(captured_img, self.cell_radius, self.debug)
        img.get_circle_positions()
        img.show()
        print("got all qr codes:", self.scan_qr_code(captured_img))
        return self.get_board_state(img)

    @staticmethod
    def empty_state():
        return [ [None for x in range(GreenBoardProcessor.board_width)]
                 for x in range(GreenBoardProcessor.board_width) ]

    @staticmethod
    def scan_qr_code(img):
        """Get codes from image object

        :param img: a numpy array, that must be converted to PIL.Image for
                    zbarlight
        :return: result of zbarlight scan_code (list of text scanned from
                 qrcode)
        """
        return pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])

    def get_board_state(self, img):
        """Looks at each square, using the "center" hints, and reads QR codes.

        NOTE: This is embarrassingly parallelizable, if we needed to optimize
        Returns the board state
        """
        board = self.empty_state()
        for (i, j, square) in img.next_square():

            cv2.waitKey(0)
            qr = self.scan_qr_code(square)
            if qr is not None:
                if self.debug:
                    print("Got QR code: ", qr, " for [", i, ", ", j, "]")
                board[i][j] = qr

        return board