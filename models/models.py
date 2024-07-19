# -*- coding: utf-8 -*-

# social network
# db.define_table(
#     "network",
#     Field("user_id"),
#     Field("network", label=T('Username')),
#     Field("network_type", label=T('Network')),
# )

db.define_table(
    "network",
    Field("facebook"),
    Field("googleplus"),
    Field("linkedin"),
    Field("twitter"),
    auth.signature,
)

# company
db.define_table(
    "company",
    Field("name"),
    Field("description", 'text'),
    Field("avatar", "upload"),
    Field("site"),
    Field("team"),
    Field("investors"),
    auth.signature,
    format="%(name)s"
)

# company team
db.define_table(
    "company_team",
    Field("company_id", 'reference company'),
    Field("user_id", db.auth_user),
    Field("role"),
)

# Google Token

db.define_table(
    "google_token",
    Field("token", 'json'),
    Field("user_id", db.auth_user)
)

# request
db.define_table(
    "request",
    Field("company_id", 'reference company'),
    Field("accepted", "boolean", default=False),
    Field("is_active", "boolean", default=True, writable=True),
    auth.signature,
)

# role
db.define_table(
    "role",
    Field("role"),
    Field("company"),
    Field("user_id"),
)

db.define_table(
    'colors',
    Field('color'),
    Field('used','boolean',default=False)
)
# tag
db.define_table(
    "tag",
    Field("tag"),
    Field("color","reference colors"),
    Field("company", 'reference company'),
    auth.signature,
    format="%(tag)s"
)

# topic
db.define_table(
    "topic",
    Field("title"),
    Field("tp_content", "text"),
    Field("tags"),
    Field("company", 'reference company'),
    auth.signature,
)

# reply
db.define_table(
    "reply",
    Field("rp_content", "text"),
    Field("topic", 'reference topic'),
    Field("reply"),
    auth.signature,
)
