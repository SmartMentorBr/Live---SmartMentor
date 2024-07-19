# -*- coding: utf-8 -*-
# import email's data

# Para recarregar os modules por causa do módulo do Linkedin
from gluon.custom_import import track_changes;
track_changes(True)

import os
import sys
path = os.path.join(request.folder,'modules')
if not path in sys.path: sys.path.append(path)

from gluon import current

from data_config import EMAIL_SERVER, CLIENT_EMAIL, CLIENT_LOGIN
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate

#db = DAL('sqlite://relatto.sqlite', pool_size=1,
#        check_reserved=['all'], adapter_args={'foreign_keys': False})

db = DAL('mysql://reportolive:Z3}a$}>EoJ9{@reportolive.mysql.pythonanywhere-services.com/reportolive$reportolive',
	 pool_size=1, check_reserved=['all'], adapter_args={'foreign_keys': False})
#
# if not db:
#     db = DAL(
#         'postgres://root:relattorocks@relattodb'
#         '.cztmxwqonc5r.sa-east-1.rds.amazonaws.com:5432/relatto',
#         adapter_args={'foreign_keys': False}
#     )


# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
# (optional) static assets folder versioning
# response.static_version = '0.0.0'

auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

auth.settings.extra_fields["auth_user"] = [
    Field("company"),

    Field("first_name", requires=IS_NOT_EMPTY(
        error_message=auth.messages.is_empty)),

    Field("site", requires=IS_EMPTY_OR(
        IS_URL(error_message=T("Needs to be a valid URL!")))),

    Field("avatar", "upload", requires=IS_EMPTY_OR(
        IS_IMAGE(extensions=('jpeg', 'png')))),

    Field("avatar_linkedin",'string'),
]


# db.auth_user.first_name.requires = IS_NOT_EMPTY(
#    error_message=auth.messages.is_empty
# )
# create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

# configure email


mail = auth.settings.mailer
mail.settings.server = EMAIL_SERVER
mail.settings.sender = CLIENT_EMAIL
mail.settings.login = CLIENT_LOGIN
mail.settings.tls = True
mail.settings.ssl = False

# configure auth policy
auth.settings.login_url = URL('index')
auth.settings.formstyle = 'divs'
auth.settings.reset_password_requires_verification = True
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.login_after_registration = False
auth.settings.login_next = URL('recent_activity')
auth.settings.profile_next = URL('user/profile')
auth.settings.change_password_next = URL('user/profile')
auth.settings.request_reset_password_next = URL('index')
auth.settings.reset_password_next = URL('index')
auth.settings.verify_email_next = URL(c='default', f='index')
auth.settings.register_next = URL('welcome')
auth.messages.verify_email = str(T("""<html>Hello, welcome to Reportolive plataform! <br />
                                    Now you can use the application to make easy the communication between
                                    you and the stakeholders or shareholders of a company.<br>
                                    Use the link below to confirm your registration, so we can activate your account.</br>
                                    It is only needed for you to do this one time, then you can login with your email and password.</br> http://""")) + request.env.http_host + URL(r=request, c='default', f='user', args=['verify_email']) + '/%(key)s <br />' + str(T("<br />Thank you,<br /> Reportolive Team - www.reportolive.com</html>"))
auth.messages.reset_password = str(T("""<html>Hello, you are receiving this message because you forgot your password and asked to reset it.
                                    You just need to click the link below and follow the instructions in your browser. <br />
                                    In case you did not make this request, please ignore this email.<br /> http://""")) + request.env.http_host + URL(r=request, c='default', f='user', args=['reset_password']) + '/?key=%(key)s <br />' + str(T("<br />Thank you,<br /> Reportolive Team - www.reportolive.com</html>"))

# auth default attributes rename
db.auth_user.first_name.label = T("Name")
db.auth_user.last_name.writable = db.auth_user.last_name.readable = False

#Tornar o campo do avatar linkedin do profile não legível na atualização de formulários.
db.auth_user.avatar_linkedin.writable = db.auth_user.avatar_linkedin.readable = False


#Define timezone user
from pytz import timezone

timezone_usuario = session.user_timezone or timezone('UTC')
timezone_e_desconhecida = session.user_timezone is None

TESTEMODE = None

#URL para autenticação do linkedin
current.url_linkedin = URL(scheme="http",host=request.env.http_host,f="user",args="login")
