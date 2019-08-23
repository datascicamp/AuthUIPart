from app import app
from flask import render_template, url_for, redirect
from app.forms import ResetPasswordRequestForm, ResetPasswordForm, RegisterRequestForm, LoginForm, RegisterForm
from func_pack import get_api_info
from config import Config
import requests


# ------------ Auth routing -------------- #
# reset password request template
@app.route('/reset-password-request', methods=['GET'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    return render_template('email/reset_password_request.html', form=form)


# reset password request Post
@app.route('/reset-password-request', methods=['POST'])
def reset_password_request_recevie_form():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        account_email = form.email.data
        dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/reset-password/email-sending-by-account-email'
        result = requests.post(dest_url, data={'account_email': account_email})
        account_to_reset = get_api_info(result)
        return render_template('email/inform_reset_email.html', account_email=account_email)


# receiving password token
@app.route('/reset-password/<string:token>', methods=['GET'])
def reset_password_receiving_token(token):
    form = ResetPasswordForm()
    dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/reset-password/token-receiving/' +\
               str(token)
    result = requests.get(dest_url)
    if result.status_code == 200:
        account_to_reset = get_api_info(result)[0]
        return render_template('email/reset_password.html', form=form, account_email=account_to_reset['account_email'])


# reset password
@app.route('/reset-password/<string:token>', methods=['POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/reset-password/token-receiving/' +\
                   str(token)
        new_password = str(form.re_new_password.data)
        result = requests.get(dest_url)
        account_to_reset = get_api_info(result)[0]
        account_to_reset['password'] = new_password
        update_account_url = 'http://' + Config.ACCOUNT_SERVICE_URL + '/api/account/account-updating'
        requests.put(update_account_url, data=account_to_reset)
        return render_template('email/inform_reset_success.html', form=form, account_email=account_to_reset['account_email'])


# register confirmation
@app.route('/register-confirmation/<string:token>', methods=['GET'])
def register_confirmation(token):
    dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/registration/token-receiving/' +\
               token
    result = requests.get(dest_url)
    if result.status_code == 200:
        return render_template('email/register_confirmation.html')


# register request page
@app.route('/register-email-request/<string:account_email>', methods=['GET'])
def register_email_request(account_email):
    form = RegisterRequestForm()
    return render_template('email/register_request.html', form=form, account_email=account_email)


# sending register verification email
@app.route('/register-email-request/<string:account_email>', methods=['POST'])
def register_email_sending(account_email):
    form = RegisterRequestForm()
    if form.validate_on_submit():
        dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/registration/email-sending-by-account-email'
        result = requests.post(dest_url, data={'account_email': account_email})
        if result.status_code == 200:
            return render_template('email/inform_register_email.html')


# -------------- Login View --------------- #
# Login View
@app.route('/login', methods=['GET'])
def login_view():
    form = LoginForm()
    return render_template('login/login.html', form=form)


# Login verify
@app.route('/login', methods=['POST'])
def login_verify():
    form = LoginForm()
    if form.validate_on_submit():
        account_email = form.email.data
        password = form.password.data
        dest_url = 'http://' + Config.ACCOUNT_SERVICE_URL + '/api/account/validate-password'
        result = requests.post(dest_url, data={'account_email': account_email, 'password': password})
        if result.status_code == 200:
            account = get_api_info(result)[0]
            if account['account_id'] != -1:
                return render_template('individual/home_page.html', account_email=account['account_email'])
            else:
                return render_template('login/login.html', form=form)


# -------------- Register View --------------- #
# register view
@app.route('/register', methods=['GET'])
def register_view():
    form = RegisterForm()
    return render_template('register/register.html', form=form)


# register post
@app.route('/register', methods=['POST'])
def register_account():
    form = RegisterForm()
    if form.validate_on_submit():
        # account info
        account_info = dict()
        account_info['account_email'] = form.email.data
        account_info['password'] = form.re_password.data
        register_url = 'http://' + Config.ACCOUNT_SERVICE_URL + '/api/account/account-creating'
        result = requests.post(register_url, data=account_info)
        if result.status_code == 200:
            return redirect(url_for('register_email_request', account_email=form.email.data))
        else:
            return redirect(url_for('register_view'))




