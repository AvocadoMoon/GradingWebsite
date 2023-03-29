from wtforms import StringField, PasswordField, SubmitField, Field, FileField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms.form import Form
from flask import render_template, redirect, request, make_response, send_file
from webapp.autograding.autograde import autoGrade


class InputTypes():
    STRING_SOLUTION = "string"
    SCRIPT_SOLUTION = "script"
    INTEGER_SOLUTION = "int"
    NO_SUBMISSION = "empty"
    AUTOGRADE = "autoValidate"

class NameGeneration():
    inputLabel = lambda self, qN, qLetter: f"Question {qN}.{qLetter}" if qLetter != "" else f"Question {qN}"
    inputKey = lambda self, qN, qLetter: f"{qN}-{qLetter}"

#https://wtforms.readthedocs.io/en/2.3.x/fields/
#https://wtforms.readthedocs.io/en/2.3.x/_modules/wtforms/fields/core/
class AnswerInput(InputTypes, NameGeneration):
    def __init__(self, formdata=None, obj=None, prefix="", data=None, meta=None, **kwargs):
        # self.form = Form(formdata, obj, prefix, data, meta, **kwargs)
        self.form = FlaskForm()

        self.submitButton = SubmitField("Submit")
        self.testButton = SubmitField("Test")

        self.submitButton = self.submitButton.bind(self.form, "submitButton")
        self.testButton = self.testButton.bind(self.form, "testButton")

    #Need to do this because of bug otherwise class global variable 'data' wont be initiated
    def bindInput(self, initData, input, name):
        input = input.bind(self.form, name)
        input.process_data(initData)
        return input
    
    def inputMakerForAQuestion(self, qN, question):
        for part in question:
            qLetter = part["part"]
            inputLabel = self.inputLabel(qN, qLetter)
            solutionType = part["inputType"]

            questionInput = None
            if(self.STRING_SOLUTION == solutionType):
                questionInput = StringField(inputLabel, validators=[Length(max=1000)])
                questionInput = self.bindInput("", questionInput, inputLabel)

            elif(self.SCRIPT_SOLUTION == solutionType):
                questionInput = FileField(inputLabel, validators=[])
                questionInput = self.bindInput(0, questionInput, inputLabel)

            elif(self.INTEGER_SOLUTION == solutionType):
                questionInput = IntegerField(inputLabel, validators=[])
                questionInput = self.bindInput(0, questionInput, inputLabel)

            elif(self.NO_SUBMISSION == solutionType or self.AUTOGRADE):
                questionInput = f"{inputLabel} requires no submission"

            part["input"] = questionInput

class LabPage(InputTypes, NameGeneration):
    def __init__(self, labNumber):
        self.labNumber = labNumber
        self.solutionInput = []
        self.answerInput = AnswerInput()

    def splitQuestionsAndMakeInput(self, questions):
        for key in questions.keys():
            self.answerInput.inputMakerForAQuestion(key[1:], questions[key])
    
    def gradeSubmissions(self, form, labTemplate):
        for question in labTemplate["questions"].keys():
            for part in range(len(labTemplate["questions"][question])):
                qNumber = question[1:]
                qLetter = labTemplate["questions"][question][part]["part"]
                key = self.inputLabel(qNumber, qLetter)

                if (key in form):
                    labTemplate["questions"][question][part]["studentSolution"] = form[key]
        
        ## Use grading script with loaded labTemplate ##
        labTemplate = autoGrade(labTemplate)

        ## Return labTemplate with feedback and scoring completed

        return labTemplate

    def renderLabPage(self, labTemplate, labNumber):
        self.splitQuestionsAndMakeInput(labTemplate["questions"])
        return render_template("labPages.html", labNumber=labNumber, labDescription= labTemplate["labDescription"], questions=labTemplate["questions"], submitButton= self.answerInput.submitButton, testButton=self.answerInput.testButton)
    
    