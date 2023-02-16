#Import the Image and ImageFilter classes from PIL (Pillow)
from re import sub
from turtle import color
from PIL import Image, ImageDraw
from PIL import ImageFilter
import sys
import random
import numpy as np
import os


def find_point(im_array, threshold):
    # A threshold around 0.9 works best
    x = 0
    y = 0
    
    # Move through each y coordinate, starting from the bottom, until the sum of the pixels in
    # the row are less than the threshold
    for i in range(im_array.shape[0] - 1, 0, -1):
        if sum(im_array[i]) < threshold * im_array.shape[1] * 255:
            x = i
            break
    
    # From the selected row, move through each column until we find a pixel less than the 
    # threshold
    for j in range(im_array.shape[1] - 1, 0, -1):
        if im_array[x][j] < 255 * threshold:
            y = j
            break
            
    return (x,y)

"""
Returns an image partitioned into sections and the y coordinate of the top of a a row. The function assumes all
images are of the same scale and size (which may not always be the case but we can improve later)
"""
def find_rows(im):
    # im = Image.open(filepath)
    im_array = np.asarray(im)
    
    width = im_array.shape[1]
    height = im_array.shape[0]
    rows = []
    
    # point = find_point(im_array, height, 0.91)
    point = find_point(im_array, 0.91)
    draw = ImageDraw.Draw(im)
    
    # get coordinates of all the rows
    for i in range(30):
        y = point[0] - 47 * i
        draw.line((0, y, width, y), fill=128)
        rows += [y]
        
    #point2 = find_point(im_array, point[0] - 1409, 0.91)
    draw.line((0, point[0] - 1704, width, point[0] - 1704))
    rows += [point[0] - 1751]
    rows.reverse()
    
    return im, rows, point


def test(output_path, gt_path):
    with open(output_path,'r') as f:
        preds = f.readlines()
    # gt_path = r'C:\Users\cvpra\Desktop\Sem2\Computer_Vision\Assignment1\karachar-marcskin-pchakila-a1 - Copy\test-images\a-27_groundtruth.txt'
    with open(gt_path,'r') as f:
        gt = f.readlines()

    #Calculate Accuracy
    correct = 0
    wrong = 0
    for index, predicted, ground_truth in zip(range(len(preds)),preds,gt):
        if predicted == ground_truth:
            correct += 1
        else:
            wrong += 1
            print('Q'+str(index+1)+'WRONG')
            print('pred:', predicted)
            print('truth:', ground_truth)

    if len(preds)==85:
        print('Acuracy: ', correct/len(preds)*100, '%')
        print(wrong, 'WRONG')
    else: print('ERRRORRR SKIPPEDDD QUESTIONSS', 85 - len(preds))

    
def grade(image_path,output_path):
    '''
    Takes the input image path and the output.txt file path.
    Sccans the Input Image and writes the detected answer to the output.txt file.
    '''
    im = Image.open(image_path)
    if im.mode != 'L':
        im = im.convert('L')
    i, rows, point= find_rows(im) 
    img = np.array(im)

    window_width = 1
    window_height = abs(rows[-1] - rows[-2])

    #Heuristic Threshold to detect boxes and answers
    threshold = 0.90
    max_box_width = 100
    general_min_inter_box_gap = 10
    single_digit_inter_box_gap = 5
    min_inter_box_gap = general_min_inter_box_gap

    general_min_box_width = 30
    single_digit_min_box_width = 17
    min_box_width = general_min_box_width
    single_digit_y = point[1]*0.22
    single_digit_row = -20
    max_inter_box_gap = 40

    answers = []
    #Iterate through the question rows detected
    for index,row in enumerate(rows[-29:]):
        answer_boxes = []
        sub_boxes = []
        sb_start_end = []
        start = False

        #Iterate throgh the columns to find the sub boxes.
        for y in range(img.shape[1]-1, -1, -1):

            #Check if the region falls in the region occupied by the first column's, first 9 questions.
            #and set thresholds accordingly.
            if y<single_digit_y and row<rows[single_digit_row]:
                min_box_width = single_digit_min_box_width
                min_inter_box_gap = single_digit_inter_box_gap
            else:
                min_box_width = general_min_box_width 
                min_inter_box_gap = general_min_inter_box_gap

            #Check if there is any content in the region
            pixel_sum = np.sum(img[row-47:row, y-window_width:y])
            if pixel_sum < (threshold * 255 * window_width * window_height):

                #start a sub box
                if not start:      
                    #check inter box gap with previous box.
                    if len(sub_boxes): #at least one box detected.

                        #Cluster the sub boxes into ones corresponding to each question in the row.                        
                        if (sub_boxes[-1][1] - y) > min_inter_box_gap:
                            if (sub_boxes[-1][1] - y) > max_inter_box_gap:
                                answer_boxes.append(sub_boxes)
                                sub_boxes = []
                            start = True
                            sb_start_end.append(y)
                            img[row-47:row, y] = 0

                    else:
                        start = True
                        sb_start_end.append(y)
                        img[row-47:row, y] = 0

            else:
                #End the sub box
                if start:
                    #check if the width is too small
                    if sb_start_end[0]-y > min_box_width:
                        # print('Ended')
                        start = False
                        sb_start_end.append(y)
                        sub_boxes.append(sb_start_end)
                        sb_start_end = []
                        img[row-47:row, y] = 0
                    
                    # Don't detect boxes that are too small or ones that cover noise.
                    else:
                        if y<single_digit_y-20 and row<rows[single_digit_row]:
                            start = False
                            sb_start_end = []                

        #Check the boxes for each question to detect which one is filled            
        filled_threshold = 0.7
        options_dic = {0:'E',1:'D',2:'C',3:'B',4:'A'}
        row_answers = []
        answer_boxes.reverse()
        for ab in answer_boxes:
            q_answer =  ''
            for count, sub_box in enumerate(ab[:5]):
                if np.sum(img[row-47:row, sub_box[1]:sub_box[0]]) < filled_threshold*255*window_height*(sub_box[0]-sub_box[1]):
                    q_answer += options_dic[count]

            q_answer = q_answer[::-1]
            #check if there is any writing in front of the question.
            if len(ab)>6:
                q_answer += ' x'

            row_answers.append(q_answer)

        answers.append(row_answers)

    # write answers to the output.txt file
    with open(output_path, 'w+') as f:
        for column in range(3):
            if column==2:
                for row in range(27):
                    if row == 26:
                        try:
                            ans = answers[row][column]
                        except: ans = ''
                        f.write(str((29*2) + row + 1) + ' ' + ans )
                    else:
                        try:
                            ans = answers[row][column]
                        except: ans = ''
                        f.write(str((29*2) + row + 1) + ' ' + ans + '\n')

            else:
                for row in range(29):
                    try:
                        ans = answers[row][column]
                    except: ans = ''
                    f.write(str((29*column) + row + 1) + ' ' + ans + '\n') 


if __name__ == '__main__':
    # Get the form image paht
    image_path = sys.argv[1]
    output_path = sys.argv[2]
    grade(image_path, output_path)