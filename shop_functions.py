from flask import session, request
from models import User

'''
@doc return User or None
'''
def check_login():
    if 'email'  in session and 'p_hash' in session:
        profile = User.query.filter(User.email == session['email']).first()
        return profile
    else:
        user_id = request.cookies.get('id')
        p_hash = request.cookies.get('p_hash')
        if user_id and p_hash:
            profile = User.query.filter(User.id == int(user_id)).filter(
                User.password_hash == p_hash
            ).first()
            return profile
        else:
            return None
    
    return None
