from wtforms import SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask import render_template, redirect, request, make_response, send_file
from webapp.pageLogic.login import cookieIDs

class GradingHubLogout(FlaskForm):
    logoutButton = SubmitField("Logout")


class GradingHubLogic(GradingHubLogout, cookieIDs):

    def logoutUser(self):
        resp = make_response(redirect("/"))
        resp.delete_cookie(self.passwordCookie)
        resp.delete_cookie(self.netIDCookie)
        return resp