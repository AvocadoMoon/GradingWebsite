# Autograding script: v1.0

import json
import os

cwd = os.getcwd()
sep = os.sep
#import re

def autoGrade(dict):
    studentIP = dict["IP"] #get students IP address
    labNumber = dict["labNumber"] #get lab number
    questions = dict["questions"] #get students responses
    lfp = load_feedback_and_points(labNumber) #load feedback and points for the given requested lab

    with open(f"{cwd}{sep}webapp{sep}autograding{sep}Solutions{sep}Lab{labNumber}{sep}{studentIP}_solutions.json", "r") as f:
        actualAnswer = json.load(f)
        for qn in questions.keys():
            for part in questions[qn]: #loop through each part (e.g. Q1A, Q1B, Q2, Q3, etc)
                questionID = f"{qn}{part['part']}" if part["part"] != "" else f"{qn}" #questionID = ID of question

                if part["inputType"].strip() == "empty":
                    continue

                if actualAnswer[f"{questionID}"].strip() == part["studentSolution"].strip():
                #if re.search(r'\b' + actualAnswer[f"{questionID}"].strip() + r'\b', part["studentSolution"].strip()): #need to accomodate multiple answers per textbox
                    part["points"] = lfp[f"{questionID}"][0] #gets point value
                    part["feedback"] = "OK"
                elif part["studentSolution"].strip() == "".strip() and part["inputType"] != "empty":
                    part["points"] = 0
                    part["feedback"] = "No solution entered."
                else:
                    part["points"] = 0
                    part["feedback"] = lfp[f"{questionID}"][1] #gets feedback
    print(part)
    f.close()
    return dict

#load feedback and point values, stored as a json file as a dictionary
def load_feedback_and_points(labNumber):
    with open(f'{cwd}{sep}webapp{sep}autograding{sep}Feedback{sep}lab{labNumber}.json', "r") as f:
        lfp = json.load(f)
    f.close()
    return lfp

#---------TESTING---------#
def test():
    with open('testSolution.json', 'r') as f:
        studentAnswers = json.load(f)
    f.close()
    return studentAnswers

#test()
#autoGrade(test())

#-------------------------#