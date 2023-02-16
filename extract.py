import sys
from PIL import Image

import utils

def get_answer(m, n):
    ans = 'A'
    if injected_form_img.getpixel((m, n + 5)) <= 100:
        ans = 'B'  
    elif injected_form_img.getpixel((m + 5, n)) <= 100:
        if injected_form_img.getpixel((m + 5, n + 5)) <= 100:
            ans = 'D'
        else:
            ans = 'C'
    elif injected_form_img.getpixel((m + 5, n + 5)) <= 100:
        ans = 'E'
    return ans


if __name__ == "__main__":
    # Get the injected form image
    injected_form_path = sys.argv[1]
    injected_form_img = Image.open(injected_form_path)
    injected_form_img = injected_form_img.convert('L')

    # Get starting position
    _, start_point, _ = utils.find_rows(injected_form_img)

    x, y = start_point

    extracted = list()
    while len(extracted) < 85:
        answer = ''
        for _ in range(5):
            if injected_form_img.getpixel((x, y)) <= 100:
                answer += get_answer(x, y) 
                x += 10  # Gap between options of the same question
                
        extracted.append(answer)
        x += 5  # Gap between questions
        if len(extracted) != 0 and len(extracted) % 10 == 0:  # 10 answers per line
            x = start_point[0]
            y += 10

    # Write extracted answers to file
    with open(sys.argv[2], 'w') as out_file:
        for i, extracted_ans in enumerate(extracted):
            out_file.write(f"{i + 1} {extracted_ans}\n")
