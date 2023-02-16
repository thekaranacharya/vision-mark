from PIL import Image
import sys

import utils

if __name__ == '__main__':
    # Get the form image
    form_path = sys.argv[1]
    form_img = Image.open(form_path)
    form_img = form_img.convert('L')

    encodings = {}
    # Braille encoding
    encodings = {
        'A': [(0, 0)],
        'B': [(0, 0), (0, 5)],
        'C': [(0, 0), (5, 0)],
        'D': [(0, 0), (5, 0), (5, 5)],
        'E': [(0, 0), (5, 5)]
    }

    # Read ground truth file 
    answers_path = sys.argv[2]
    answers = list()
    with open(answers_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            answers.append(line.strip().split(" ")[-1])


    # Get starting position to start injecting from
    _, start_point, _ = utils.find_rows(form_img)
    
    
    injected_form_img = form_img.copy()
    x, y = start_point
    
    for i, ans in enumerate(answers):
        for j in range(len(ans)):
            locations = encodings[ans[j]]
            
            for loc in locations:
                m, n = loc
                
                for u in range(2):
                    for v in range(2):
                        injected_form_img.putpixel((x + m + u, y + n + v), (0))
            
            x += 10  # Gap between options of the same question
                
        x += 5  # Gap between questions
        if (i + 1) % 10 == 0:  # 10 answers per line
            x = start_point[0]
            y += 10

    injected_form_img.save(sys.argv[3], quality=90)
