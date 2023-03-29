from flask_wtf import Form
from flask_wtf.csrf import CSRFError
from flask import render_template, redirect, request, flash, make_response, send_file
from webapp import app, csrf
from webapp.pageLogic import labPageLogic, login, gradingHub
from webapp.pageLogic.login import cookieIDs
import os
import json
from threading import Lock
from webapp import studentPasswordsLock, sep, cwd


#check hash releases the lock, otherwise have to do it manually
def isAuthenticaCookie():
    loginLogic = login.loginLogic()
    netID, password = request.cookies.get(loginLogic.netIDCookie), request.cookies.get(loginLogic.passwordCookie)
    studentPasswordsLock.acquire()
    if netID != None and password != None: 
        if(loginLogic.checkHash(netID, password)):
            return False
        return render_template("corruptCookie.html")

    studentPasswordsLock.release()
    return redirect("/")

################
## Login Page ##
################

@app.route("/", methods=["POST", "GET"])
def loginPage():
    loginLogic = login.loginLogic()

    netID, password = request.cookies.get(loginLogic.netIDCookie), request.cookies.get(loginLogic.passwordCookie)
    if netID != None and password != None: 
        studentPasswordsLock.acquire()
        return loginLogic.validateCookie(netID, password)

    if request.method == "POST":
        if "submit" in request.form:
            if loginLogic.loginInput.validate():
                return loginLogic.validateLogin()
                
            return loginLogic.renderLoginPage("toLong")
        
        elif "createAccount" in request.form:
            if "confirmPassword" in request.form:
                return loginLogic.createAccount()
            return loginLogic.renderLoginPage(createAccount=True)
        
        return loginLogic.renderLoginPage()

    return loginLogic.renderLoginPage()

#################
## Grading Hub ##
#################


@app.route("/GradingHub", methods=["GET", "POST"])
def gradingHubPage():
    notAuthenticate = isAuthenticaCookie()
    if(notAuthenticate):
        return notAuthenticate

    hubLogic = gradingHub.GradingHubLogic()
    if request.method == "POST" and "logoutButton" in request.form:
        return hubLogic.logoutUser()
    return render_template("gradingHub.html", hubLogic=hubLogic)


##############
## Lab Page ##
##############

@app.route("/Lab-<labNumber>", methods=["POST", "GET"])
def labQuestionsPage(labNumber):
    notAuthenticate = isAuthenticaCookie()
    if(notAuthenticate):
        return notAuthenticate

    lPage = labPageLogic.LabPage(labNumber)

    jsonPath = f'{cwd}{sep}webapp{sep}JSONs{sep}lab-{labNumber}.json'
    exists = os.path.exists(jsonPath)
    if (exists):
        #create copy of lab template in memory stored within labTemplate file, then key the specific lab number questions
        labTemplate = None

        with open(jsonPath, "r") as js:
            labTemplate = json.load(js)
        
        with open(f"{cwd}{sep}webapp{sep}JSONs{sep}NetID-IP.json", "r") as IPmap:
            IPmap = json.load(IPmap)
            labTemplate["IP"] = IPmap[request.cookies[cookieIDs.netIDCookie]]

        #Grade the sent items, and if submitted then save it
        if (request.method == "POST"):
            labTemplate = lPage.gradeSubmissions(request.form, labTemplate)

            if ("submitButton" in request.form):
                submissionPath = f"{cwd}{sep}StudentSubmissions{sep}{labTemplate['IP']}{sep}Lab-{labTemplate['labNumber']}"

                with open(f'{submissionPath}{sep}submissionStructure.json', "w") as js:
                    json.dump(labTemplate, js, indent=4)
                
                for fileQuestionNumber in request.files.keys():
                    f= request.files[fileQuestionNumber]
                    f.save(f'{submissionPath}{sep}{fileQuestionNumber}')  


        return lPage.renderLabPage(labTemplate, labNumber)
    
    else:
        return redirect("/NoLab")


#####################
## Unreachable Lab ##
#####################

@app.route("/NoLab")
def noLab():
    return render_template("noLab.html")









