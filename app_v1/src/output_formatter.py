# output_formatter.py

def format_MCQ(List):
    output = ""
    for i in range (0, len(List)):
        mcq = List[i]
        output += "Q" + str(i + 1) + ". "
        output += mcq[0][0] + "\n"
        for option in mcq[1]:
            output += "    " + option + "\n"
        output += "\n"

    return output

def format_MCQ_with_correct_answer(List):
    output = ""
    for i in range (0, len(List)):
        mcq = List[i]
        output += "Q" + str(i + 1) + ". "
        output += mcq[0][0] + "\n"
        correct_answer = mcq[2][0]
        for j in range (0, len(mcq[1])):
            temp = "    " + mcq[1][j] 
            if j + 1 == correct_answer:
                temp +=  " (Correct answer)"
            output += temp + "\n"
        output += "\n"

    return output
