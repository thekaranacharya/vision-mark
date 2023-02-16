import numpy as np

def find_point(im_array, starting_y, row_threshold=0.91, box_threshold=0.75):
    # A threshold around 0.9 works best
    x = 0
    y = 0
    
    # Move through each y coordinate, starting from the bottom, until the sum of the pixels in
    # the row are less than the threshold
    for i in range(starting_y, 0, -1):
        if sum(im_array[i]) < row_threshold * im_array.shape[1] * 255:
            y = i
            break
    
    # From the selected row, move through each column until we find a pixel less than the 
    # threshold
    for j in range(im_array.shape[1] - 1, 0, -1):
        if im_array[y-3][j] < 255 * box_threshold:
            x = j
            break
            
    return (x,y)

def find_row_width(im_array, first_row, threshold):
    whitespace = 0
    
    # find whitespace
    for i in range(first_row, 0, -1):
        if sum(im_array[i]) > threshold * im_array.shape[1] * 255:
            whitespace = i
            break
    
    point = find_point(im_array, whitespace, 0.91)

    return first_row - point[1] - 1

"""
Returns an image partitioned into sections and the y coordinate of the top of a a row. The function assumes all
images are of the same scale and size (which may not always be the case but we can improve later).
"""
def find_rows(im):
    im_array = np.asarray(im)
    
    width = im_array.shape[1]
    height = im_array.shape[0]
    rows = []
    
    loc = height - 1
    initial_point = find_point(im_array, loc, 0.91)

    for i in range(28):
        point = find_point(im_array, loc, 0.91)
        row_width = find_row_width(im_array, point[1], 0.98)
        
        rows += [point[1]]
        y = point[1] - row_width
        
        loc = y
        
    avg_row_width = int(np.mean([rows[x-1] - rows[x] for x in range(1, len(rows))]))
    
    rows += [rows[-1] - avg_row_width]
    rows.reverse()
    
    start_point = initial_point[0], rows[0] - 250
        
    return rows, start_point, initial_point