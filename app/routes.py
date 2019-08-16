from app import app
from flask import render_template, url_for
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
from func_pack import get_api_info
from config import Config
import requests


# ------------ Auth routing -------------- #
# reset password request template
@app.route('/reset-password-request', methods=['GET'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    return render_template('auth/reset_password_request.html', form=form)


# reset password request Post
@app.route('/reset-password-request', methods=['POST'])
def reset_password_request_recevie_form():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        account_email = form.email.data
        dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/reset-password/email-sending-by-account-email'
        result = requests.post(dest_url, data={'account_email': account_email})
        account_to_reset = get_api_info(result)
        return render_template('auth/inform_reset_email.html', account_email=account_email)


# receiving password token
@app.route('/reset-password/<string:token>', methods=['GET'])
def reset_password_receiving_token(token):
    form = ResetPasswordForm()
    dest_url = 'http://' + Config.MAIL_SENDING_SERVICE_URL + '/api/reset-password/token-receiving/' +\
               str(token)
    result = requests.get(dest_url)
    if result.status_code == 200:
        account_to_reset = get_api_info(result)[0]
        return render_template('auth/reset_password.html', form=form, account_email=account_to_reset['account_email'])


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
        return render_template('auth/inform_reset_success.html', form=form, account_email=account_to_reset['account_email'])


# register email sending inform
@app.route('/register-email-sending', methods=['GET'])
def register_email_inform():
    return render_template('auth/inform_register_email.html')


# register confirmation
@app.route('/register-confirmation', methods=['GET'])
def register_confirmation():
    return render_template('auth/register_confirmation.html')


