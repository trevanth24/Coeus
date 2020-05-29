import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from coeus import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) #Need this for titling picture
    _, f_ext = os.path.splitext(form_picture.filename) #fname for _
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    output_size = (125,125)
    i = Image.open(form_picture) #resize image so space and lag doesn not exist when browser talks to comp
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_filename

# Can also create method that deletes old picutres (create new function that takes in old picutre and name)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external = True)}

If you did not make this request, then simply ignore this request and no changes will be made
'''
    mail.send(msg)