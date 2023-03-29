from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.form import Form
from flask import render_template, redirect, request, make_response, send_file
import os
import json
from threading import Lock
from webapp import studentPasswordsLock, cwd, sep
import hashlib
import base64

class LoginInput(FlaskForm):
    username = StringField('NetID', validators=[Length(max=50)])
    password = PasswordField('Password', validators=[Length(max=20, min=4)])
    confirmPassword = PasswordField('Confirm Password')

    submit = SubmitField('Sign In')
    createAccount = SubmitField('Create Account')
    returnToSignIn = SubmitField('Return To Sign In')


class cookieIDs():
    passwordCookie = "LOGIN_INFO"
    netIDCookie = "NET_ID"
    

#====[Hashing and salting scheme]====#
#!-- Salt is byte array randomly generated, encoded using base 64 into another bytearray, then that is converted to a string, inverse happens when using salt again
# Hash is a hexidecimal number in sting format --!#


class loginLogic(cookieIDs):
    def __init__(self):
        self.loginInput = LoginInput()
        self.studentAccountsPath = f"{cwd}{sep}webapp{sep}JSONs{sep}studentAccounts.json"


    def hashWithSalt(self, salt:bytes, password:str):
        hasher = hashlib.sha256()
        hasher.update(salt + bytes(password, "utf-8"))
        return hasher.hexdigest()


    def renderLoginPage(self, alert="", createAccount=False):
        return render_template("loginPage.html", login=self.loginInput, alert=alert, createAccount=createAccount)


    ################
    ## Set Values ##
    ################
  
    def setCookie(self, netID:str, hash:str):
        resp = make_response(redirect("/GradingHub"))
        resp.set_cookie(self.netIDCookie, netID, httponly=True)
        resp.set_cookie(self.passwordCookie, hash, httponly=True)
        return resp

    def setPassword(self, dataBase, netID, password, dataBasePath):

        #128 bit salt
        salt = os.urandom(16)
        hash = self.hashWithSalt(salt, password)

        salt = base64.standard_b64encode(salt).decode()
        dataBase[netID]["salt"] = salt
        dataBase[netID]["hash"] = hash

        with open(dataBasePath, "w") as js:
            json.dump(dataBase, js, indent=4)
        
        studentPasswordsLock.release()
        return hash


    
    ################
    ## Validation ##
    ################

    #assume lock is already taken for checking
    def checkHash(self, netID:str, hash:str):
        with open(self.studentAccountsPath, "r") as js:
            dataBase = json.load(js)
            if (dataBase[netID]["hash"] == hash):
                studentPasswordsLock.release()
                return True
            else:
                studentPasswordsLock.release()
                return False
    
    def validateCookie(self, netIDCookie, passwordCookie):
        result = self.checkHash(netIDCookie, passwordCookie)
        if result:
            return redirect("/GradingHub")
        return render_template("corruptCookie.html")
        

    def validateLogin(self):
        netID = self.loginInput.username.data
        password = self.loginInput.password.data

        studentPasswordsLock.acquire()

        with open(self.studentAccountsPath, "r") as js:
            dataBase = json.load(js)
            if netID in dataBase:

                #there is an account in database, check if it equals what is expected
                salt = base64.standard_b64decode(dataBase[netID]["salt"].encode())
                hashResult = self.hashWithSalt(salt, password)
                result = self.checkHash(netID, hashResult)
                if (result):
                    return self.setCookie(netID, hashResult)
                return self.renderLoginPage("wrongInput")
            
            #there is no netID
            else:
                studentPasswordsLock.release()
                return self.renderLoginPage("No netID")


    ######################
    ## Account Creation ##
    ######################

    #1). Validate the input
    #2). There is a netID
    #3). Make sure no account exists
    #4). Make sure both passwords equal each other
    #5). Create new account
    def createAccount(self):
        if self.loginInput.validate():
            netID = self.loginInput.username.data
            password = self.loginInput.password.data
            confirmPassword = self.loginInput.confirmPassword.data

            studentPasswordsLock.acquire()
            with open(self.studentAccountsPath, "r") as db:
                db = json.load(db)
                if netID in db:
                    if (db[netID]["hash"] == ""):
                        if(confirmPassword == password):
                            hash = self.setPassword(db, netID, password, self.studentAccountsPath)
                            return self.setCookie(netID, hash)
                        

                        studentPasswordsLock.release()
                        return self.renderLoginPage("notEqual", True)
                    studentPasswordsLock.release()
                    return self.renderLoginPage("Account already exits", True)
                studentPasswordsLock.release()
                return self.renderLoginPage("No netID", True)
        return self.renderLoginPage("toLong", True)


    