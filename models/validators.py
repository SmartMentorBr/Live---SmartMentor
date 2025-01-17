# -*- coding: utf-8 -*-

# general config
not_empty = T("Field can't be empty!")
url_error = T("Needs to be a valid URL!")

# social network
# db.network.user_id.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s')
# db.network.network_type.requires = IS_IN_SET(
#     [
#         'Skype',
#         'Facebook',
#         'Google',
#         'LinkedIn',
#         'Twitter',
#         'E-mail'
#     ]
# )



# company
db.company.name.requires = [
    IS_NOT_EMPTY(error_message=T('Company already registered')), IS_NOT_IN_DB(db, 'company.name')]
db.company.avatar.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))
db.company.site.requires = IS_EMPTY_OR(IS_URL(error_message=url_error))
db.company.team.requires = IS_IN_DB(
    db, 'auth_user.id', '%(first_name)s', multiple=True)
db.company.team.writable = db.company.team.readable = False
db.company.investors.writable = db.company.investors.readable = False

# request
# db.request.company_id.requires = [IS_IN_DB(db, 'company.name', '%(name)s')]

# role
db.role.role.requires = IS_NOT_EMPTY(error_message=not_empty)
db.role.company.requires = IS_IN_DB(db, 'company.id', '%(name)s')
db.role.user_id.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s')
db.role.company.writable = db.role.company.readable = False
db.role.user_id.writable = db.role.user_id.readable = False

# tag
db.tag.tag.requires = IS_NOT_EMPTY(error_message=not_empty)
db.tag.company.writable = db.tag.company.readable = False

# topic
db.topic.title.requires = IS_NOT_EMPTY(error_message=not_empty)
db.topic.company.requires = IS_IN_DB(db, 'company.id', '%(name)s')
db.topic.company.writable = db.topic.company.readable = False

# reply
db.reply.rp_content.requires = IS_NOT_EMPTY(error_message=not_empty)
db.reply.reply.writable = db.reply.reply.readable = False

#Google Token
db.google_token.user_id.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s')