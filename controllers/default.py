# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import os
import sys

path = os.path.join(request.folder,'modules')
if not path in sys.path: sys.path.append(path)

from datetime import datetime

from gluon.tools import prettydate
from gluon import current

from oauth2client import client
from apiclient import errors
from oauth2client.client import OAuth2Credentials
from apiclient.discovery import build
import httplib2

try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json
import pickle


ROOT = 'http://'+request.env.http_host+'/'

ANALYTICS_SCOPE = "https://www.googleapis.com/auth/analytics"
ANALYTICS_SCOPE_USERS = "https://www.googleapis.com/auth/analytics.manage.users"
DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive'
SHEET_SCOPE = 'https://spreadsheets.google.com/feeds'
DOC_SCOPE = 'https://docs.google.com/feeds'

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    if auth.is_logged_in():
        redirect(URL('default', 'recent_activity'))

    fields_to_hide = ['last_name', 'company', 'site', 'avatar']

    for fieldname in fields_to_hide:
        field = db.auth_user[fieldname]
        field.readable = field.writable = False

    form_register = auth.register()

    form_login = auth.login()

    return dict(form_register=form_register, form_login=form_login,url_linkedin=current.url_linkedin)

def em_construcao():
    return dict(navbar_disable=True)

def welcome():
    return dict()

@auth.requires_login()
def enterprising():
    if request.args(0) == 'allow_request':
        db(db.request.id == request.args(1)).update(is_active=False, accepted=True)
        company = db(db.company.id == request.args(2)).select().first()
        investors_list = []
        if company.investors:
            investors = company.investors.split('|')
            for user in investors:
                investors_list.append(user)
            if request.args(3) not in investors:
                investors_list.append(request.args(3))
        else:
            investors = []

        team_list = []
        if company.team:
            team = company.team.split('|')
            for user in team:
                if user != request.args(3):
                    team_list.append(user)
        else:
            team = []

        db(db.company.id == request.args(2)).update(investors=investors_list, team=team_list)

        redirect(URL('recent_activity'))

    elif request.args(0) == 'deny_request':
        db(db.request.id == request.args(1)).update(is_active=False, accepted=False)
        redirect(URL('recent_activity'))

@auth.requires_login()
def companies():
    from random import choice

    if auth.is_logged_in():
        user = db(db.auth_user.id == auth.user.id).select().first()
    else:
        user = None


    #my_companies = db(db.company.created_by == auth.user.id).select()
    companies = db((db.company_team.user_id == auth.user.id) & (db.company_team.role == "owner")).select()

    my_companies = list()
    for comp in companies:

        c = db(db.company.id == comp.company_id).select().first()
        my_companies.append(c)

    # Team companies
    team_companies = list()
    companies = db((db.company_team.user_id == auth.user.id) & (db.company_team.role == "member")).select()
    for comp in companies:
        c = db(db.company.id == comp.company_id).select().first()
        team_companies.append(c)
    # New company form
    new_company = SQLFORM.factory(db.company,Field("avatar_upload","string",requires=IS_LENGTH(999999999999999999)))

    if new_company.process().accepted:
        image_converter()
        company_id = db.company.insert(
                name = new_company.vars.name,
                description = new_company.vars.description,
                site = new_company.vars.site,
                created_by = auth.user.id,
                avatar = img_name
                )

        db.company_team.insert(company_id = company_id, user_id = auth.user.id, role = "owner")


        tags = ['Administração','Financeiro','Recursos Humanos']

        for t in tags:
            dados_cat = db(db.tag.tag == t).select().first()

            if dados_cat:
                db.tag.insert(tag = t, company = company_id, is_active = True,color = dados_cat.color)
            else:
                cor = choice(cores_disponiveis())
                db.tag.insert(tag = t, company = company_id, is_active = True,color = cor.id)

                # Atualizando status para cor utilizada
                db(db.colors.id == cor.id).update(used=True)



        session.flash = T('added company')
        redirect(URL('companies'))

    elif new_company.errors:
        session.flash = T('Company already registered')
        redirect(URL('companies'))


    return dict(my_companies=my_companies, team_companies=team_companies, new_company=new_company)

@auth.requires_login()
def investments():
    """
    Empresas da qual estão aguardando aprovação para ser um investidor
    """
    companaies_waiting_for_approval = db((db.request.created_by == auth.user.id) &
            (db.request.accepted == False) &
            (db.request.is_active == True)).select()
    print 'Debugando: Empresas esperando aprovação -------------'
    print companaies_waiting_for_approval

    """
    Empresas da qual o usuário é investidor
    """
    companies = db((db.company_team.user_id == auth.user.id) & (db.company_team.role == 'investor')).select()

    """
    Formulário de solicitação para ser um investidor
    """
    form_request_to_invest = SQLFORM(db.request, _id="form_invest")
    if form_request_to_invest.process().accepted:
        # Verificando se o usuário já efetuou a solicitação
        company = db(db.company.id == request.vars.company_id).select().first()
        solicitacao=db((db.request.company_id == company) &
            (db.request.created_by == auth.user.id) &
            (db.request.is_active == True)).select().first()
        if solicitacao:
            response.flash = T('Você já enviou uma solicitação para esta empresa.')
            print response.flash
            redirect(URL('investments'))
        else:
            company = db(db.company.id == request.vars.company_id).select().first()
            if company.id != 0:
                db.request.insert(company_id = company.id, accepted = False, is_active = True)
                response.flash = T('Request sent!')
                print response.flash
            redirect(URL('investments'))
    elif form_request_to_invest.errors:
        response.flash = T('You have to select a company to make a request.')
        redirect(URL('investments'))

    return dict(companies=companies, form=form_request_to_invest, companies_waiting = companaies_waiting_for_approval)

@auth.requires_login()
def recent_activity():

    """
    Variáveis necessárias
    """
    my_companies = db((db.company_team.user_id == auth.user.id) & (db.company_team.role == 'owner')).select()

    """
    Formulário de busca
    """
    search = SQLFORM.factory(Field('search'), submit_button=T("Search"), formstyle='divs')
    search.attributes['_action'] = URL('search')
    search.attributes['_name'] = 'search'
    search.attributes['_method'] = 'get'

    search.custom.submit['_class'] = 'form-btn form btn-success form-btn-search'
    search.custom.widget.search['_placeholder'] = T('Search for...')
    search.custom.widget.search['_name'] = 'q'

    for i in search.elements('label'):
        i['_style'] = 'display: none;'
    if search.process().accepted:
        query = request.vars.search
        redirect(URL('search', vars={'q':query}, extension=False), client_side=True)

    """
    Timeline
    # TODO: Implementar posteriormente o "carregar mais posts"
    Motivo: Para evitar o BDUF(Big design up front), pois não há a necesisdade de implementar isto ainda
    """
    timeline = list()
    # Empresas que o usuario faz parte.
    empresas = db(db.company_team.user_id == auth.user.id).select()
    # Postagens das empresas que o usuario faz parte.
    for empresa in empresas:
        topics = db(db.topic.company == empresa.company_id).select(orderby = ~db.topic.created_on)
        for topic in topics:
            # Tags
            # topic.tp_content = nl2br(topic.tp_content)
            if topic.tags is not None:
                tags_list = list()
                for t in topic.tags.split('|'):
                    tag = db(db.tag.id == t).select().first()
                    tags_list.append(tag)
                topic.tags = tags_list
            # Comentários
            tp_replies = db(db.reply.topic == topic.id).select()
            topic['replies'] = tp_replies
            timeline.append(topic)
    # Ordenando a timeline
    order_t = sorted(timeline, key=lambda topic: topic.created_on, reverse=True)
    timeline = order_t

    """
    Solicitações de investimento
    """
    requests = list()
    for company in my_companies:
        request_for_me = db((db.request.company_id == company.company_id) & (db.request.is_active == True)).select().first()
        if request_for_me is not None:
            requests.append(request_for_me)

    print 'Debugando'
    for r in requests:
        print r
        print '--------'

    """
    Formulário de ediçã de resposta
    """
    form_reply_edit = SQLFORM(db.reply)
    if form_reply_edit.validate():
        db(db.reply.id == request.vars.reply_id).update( rp_content = form_reply_edit.vars.rp_content )
        response.flash = T('Comment edited!')
        redirect(URL('recent_activity'))

    '''
    Verificacao da Validade do token de acesso as informacoes do google
    '''
    userCredential = db(db.google_token.user_id == auth.user.id).select(db.google_token.token).first()
    if(userCredential is not None):
        session.saveCredential = False
        credentials = OAuth2Credentials.from_json(userCredential.token)
        if(credentials.access_token_expired):
            session.credentials = None
            session.token_expired = True
        else:
            session.credentials = userCredential.token
            http_auth = credentials.authorize(httplib2.Http())
            driver_service = build('drive', 'v2', http=http_auth)
            #files = driver_service.files().list().execute()
            #print(files)
            print("Auhorized")
            session.token_expired = False
    else:
        session.saveCredential = True

    return dict(requests = requests,
            search = search,
            timeline = timeline,
            my_companies = my_companies,
            form_reply_edit = form_reply_edit)

@auth.requires_login()
def company():

    if session.flash:
        print 'Session na página company'
        print session.flash
        response.flash = session.flash
    else:
        response.flash = ''

    owner=''
    search = SQLFORM.factory(Field('search'), submit_button=T("Search"), formstyle='divs')
    search.attributes['_action'] = URL('search')
    search.attributes['_name'] = 'search'
    search.attributes['_method'] = 'get'

    search.custom.submit['_class'] = 'form-btn form btn-success form-btn-search'
    search.custom.widget.search['_placeholder'] = T('Search for...')
    search.custom.widget.search['_name'] = 'q'

    for i in search.elements('label'):
        i['_style'] = 'display: none;'
    if search.process().accepted:
        query = request.vars.search
        redirect(URL('search', vars={'q':query}, extension=False), client_side=True)

    if request.args(0) == 'new':
        form = SQLFORM(db.company)
        if form.process().accepted:
            session.flash = T("You started a new company!")
            redirect(URL('companies'))
        elif form.errors:
            response.flash = T("Form has errors!")
        return dict(form=form, search=search)

    if request.args(0) == 'edit' and request.args(1):
        form = SQLFORM(db.company, db.company(request.args(1)), showid=False)
        company = db(db.company.id == request.args(1)).select().first()
        if company.team:
            team = company.team.split('|')
        else:
            team =[]

        form_topic = SQLFORM(db.topic)

        topics = db(db.topic.company == request.args(1)).select(orderby=~db.topic.created_on)
        replies = []

        for topic in topics:
            tp_replies = db(db.reply.topic == topic.id).select()
            for reply in tp_replies:
                replies.append(dict(reply=reply, topic=topic.id))
        form_reply = SQLFORM(db.reply)

        tags = db(db.tag.company == company.id).select()

        if form.process().accepted:
            session.flash = T("Company edited!")
            redirect(URL('company', vars={'company':request.args(1)}))
        elif form.errors:
            response.flash = T("Form has errors!")
        return dict(
            form=form,
            search=search,
            company=company,
            form_topic=form_topic,

            topics=topics,
            team=team,
            tags=tags,
            replies=replies,
            form_reply=form_reply)

    if request.args(0) == 'remove':
        company = db(db.company.id == request.args(1)).select().first()

        if company.team:
            team = company.team.split('|')
            if request.args(2) in company.team:
                team_list = [person for person in team if person != request.args(2)]
                db(db.company.id == company.id).update(team=team_list)
        else:
            team = []

        if company.investors:
            investors = company.investors.split('|')
            if request.args(2) in company.investors:
                investors_list = [investor for investor in investors if investor != request.args(2)]
                db(db.company.id == company.id).update(investors=investors_list)
        else:
            investors = []

        redirect(URL('company', vars={'company':request.args(1)}))
    else:
        """
        Página da empresa.
        """
        company = db(db.company.id == request.vars.company).select().first()
        # company.description = nl2br(company.description)

        if company:
            # Verificando se o usuário é membro, investidor ou dono de uma empresa.
            # Caso não, ele é redirecionado para a página inicial
            company['team'] = db(db.company_team.company_id == company.id).select()
            ids = list()
            for u in company.team:
                ids.append(u.user_id)
            if not auth.user.id in ids:
                response.flash = T("Você não pode ver esta empresa.")
                return redirect(URL('companies'))

            form = SQLFORM.factory(Field('user_invite', requires=[IS_NOT_EMPTY(error_message=not_empty),IS_IN_DB(db, 'auth_user.first_name', '%(first_name)s'),IS_NOT_IN_DB(db, 'company.team')]),_id="user_member")
            if form.validate():
                user_invite = db(db.auth_user.first_name == form.vars.user_invite).select().first()

                team_list = [user for user in team if user != '']
                if not str(user_invite.id) in team and not str(user_invite.id) in investors:
                    team_list.append(user_invite.id)
                else:
                    session.flash = T('User already on team!')



                db(db.company.id == company.id).update(team=team_list)
                redirect(URL('company', vars={'company':request.vars.company}))
            elif form.errors:
                response.flash = T('Form has errors!')

            """
            Formulário para edição da empresa
            """
            record = db.company(request.vars.company)
            form_company_edit = SQLFORM(db.company, record)
            form_company_edit.attributes["_class"] = ""
            form_company_edit.attributes["_method"] = "post"
            form_company_edit.attributes["_id"] = "form_company_edit"

            if form_company_edit.process().accepted:
                response.flash = T("Edição efetuada com sucesso.")
                redirect(URL('company', vars=dict(company=request.vars.company)))


            """
            INFO: Porque não estu usando joins para montar a query.
            Para montar um json que será tratado no front-end e por acreditar
            que o código ficará mais pythonico.
            """

            # TODO - Descobrir para o que serve o participate.
            participate = False

            # Time da empresa
            c_team = []
            team = db(db.company_team.company_id == company.id).select()
            for person in team:
                p = db(db.auth_user.id == person.user_id).select().first()
                p['role'] = person.role
                c_team.append(p)
                # Definindo o dono da empresa
                if p.role == 'owner':
                    owner = p

            form_tags = SQLFORM(db.tag)
            db.tag.company.default = request.vars.company
            if form_tags.process().accepted:
                response.flash = T('Added a tag!')
            elif form_tags.errors:
                response.flash = T('Form has errors!')
            tags = db(db.tag.company == company.id).select()

            db.topic.tags.requires = IS_IN_DB(db(db.tag.company == request.vars.company), 'tag.tag', '%(tag)s', multiple=True)

            # Formulário de postagem de tópico.
            form_topic = SQLFORM(db.topic)
            form_topic.attributes['_id'] = 'form_topic'
            form_topic.attributes['_method'] = 'post'

            db.topic.company.default = request.vars.company

            if 'edit' in request.vars:
                if form_topic.validate():
                    if 'categoria' in request.vars:
                        # Transforma o request.vars.categoria em uma lista.
                        if type(request.vars.categoria) is not list:
                            topic_tags = list()
                            topic_tags.append(request.vars.categoria)
                        else:
                            topic_tags = request.vars.categoria

                        tag_list = list()

                        id_empresa = int(request.vars.company)

                        for tag in topic_tags:
                            tag_row = db( (db.tag.tag == tag) & (db.tag.company == id_empresa) ).select(db.tag.id).first()

                            tag_list.append(str(tag_row.id))

                        tag_list = "|".join(tag_list)

                    else:
                        tag_list = None

                    db(db.topic.id == request.vars.edit).update(
                        title = request.vars.title,
                        tp_content = request.vars.tp_content,
                        tags = tag_list)
                    response.flash = T('You edited a topic')
                    redirect(URL('company', vars={'company':request.vars.company}))

            # Salvando um novo tópico
            if not 'edit' in request.vars:

                if form_topic.validate():
                    # Adicionando as tags
                    if 'categoria' in request.vars:
                        # Transforma o request.vars.categoria em uma lista.
                        if type(request.vars.categoria) is not list:
                            topic_tags = list()
                            topic_tags.append(request.vars.categoria)
                        else:
                            topic_tags = request.vars.categoria

                        tag_list = list() # lista com as categorias do post
                        id_empresa = int(request.vars.company)

                        for tag in topic_tags:

                            tag_row = db((db.tag.tag == tag) & (db.tag.company == id_empresa)).select(db.tag.id).first()

                            tag_list.append(str(tag_row.id))

                        #Fazer um join no caracter | no final de todas as categorias
                        tag_list = '|'.join(tag_list)

                    else:
                        tag_list = None

                    db.topic.insert(
                        title = request.vars.title,
                        tp_content = request.vars.tp_content,
                        company = request.vars.company,
                        tags = tag_list)

                    response.flash = T('You posted a new topic!')
                elif form_topic.errors:
                    response.flash = T('Form has errors!')

            # Tópicos
            if 'tag' in request.vars:

                # id_empresa = request.vars.company
                # tag_search = request.vars.tag

                tag = db((db.tag.tag == request.vars.tag) & (db.tag.company == request.vars.company)).select().first()

                all_topics = db(db.topic.company == request.vars.company).select(orderby=~db.topic.created_on)

                topics = list()
                for topic in all_topics:
                    if topic.tags is not None and str(tag.id) in topic.tags.split('|'):
                        topics.append(topic)
            else:
                topics = db(db.topic.company == request.vars.company).select(orderby=~db.topic.created_on)

            for topic in topics:
                if topic.tags is not None:
                    tags_list = list()
                    for t in topic.tags.split('|'):
                        tag = db(db.tag.id == t).select().first()
                        tags_list.append(tag)
                    topic.tags = tags_list

            # Comentários nos tópicos
            replies = []
            for topic in topics:
                tp_replies = db(db.reply.topic == topic.id).select()
                for reply in tp_replies:
                    replies.append(dict(reply=reply, topic=topic.id))

            # Formulário de comentário e de edição de comentário
            form_reply = SQLFORM(db.reply)
            if form_reply.validate():
                if request.vars.reply_id:
                    print 'Edição de resposta'
                    print form_reply.vars
                    db(db.reply.id == request.vars.reply_id).update(rp_content = request.vars.rp_content)
                    response.flash = T('Comment edited!')
                    redirect(URL('company', vars={'company':company.id}))
                else:
                    db.reply.insert(rp_content = request.vars.rp_content, topic = request.vars.topic)
                    response.flash = T('Reply sent!')
                    redirect(URL('company', vars={'company':company.id}))
            elif form_reply.errors:
                response.flash = T('Form has errors!')

            # Edição de tópico
            if 'edit' in request.vars:
                topic_to_edit = db(db.topic.id == request.vars.edit).select().first()
                topic_to_edit.tp_content = nlascii(topic_to_edit.tp_content)
                print topic_to_edit
            else:
                topic_to_edit = None

            return dict(form=form, team=c_team, company=company,
            form_topic=form_topic, topics=topics, participate=participate,
            form_tags=form_tags, tags=tags, search=search, replies=replies,
            form_reply=form_reply,
            topic_to_edit = topic_to_edit,
            owner = owner,
            form_company_edit = form_company_edit)

        return dict(company=company, search=search)

@auth.requires_login()
def portfolio():
    my_requests = db((db.request.created_by == auth.user.id)&(db.request.is_active == True)).select()
    form = SQLFORM(db.request)
    if form.process().accepted:
        response.flash = T('Request sent!')
        redirect(URL('portfolio'))
    elif form.errors:
        reponse.flash = T('You have to select a company to make a request.')
    return dict(my_requests=my_requests, form=form)

@auth.requires_login()
def topic():
    if request.args(0) == 'edit':
        topic = db(db.topic.id == request.args(1)).select().first()
        company = db(db.company.id == topic.company).select().first()
        form = SQLFORM(db.topic, request.args(1), showid=False)
        if form.process().accepted:
            session.flash = T("Sucess!")
            redirect(URL('company', vars={'company':topic.company}))
        elif form.errors:
            response.flash = T("Form has errors!")
        return dict(form=form, topic=topic, company_topic=company )
    elif request.args(0) == 'delete':
        topic = db(db.topic.id == request.args(1)).select().first()
        company = db(db.company.id == topic.company).select().first()
        # Verificando se o tópico foi criado pelo usuário
        if topic.created_by == auth.user.id:
            # TODO - Apagar os comentários do tópico também
            db(db.topic.id == request.args(1)).delete()
            response.flash = T("Tópico apagado com sucesso.")
            redirect(URL('company', vars = {'company':company.id}))
        else:
            response.flash = T("Você não tem permissão para apagar este tópico.")
            redirect(URL('company', vars = {'company':company.id}))


    else:
        topic = db(db.topic.id == request.args(0)).select().first()
        # tags do tópico.
        if topic.tags != None:
            tags = list()
            for t in topic.tags.split('|'):
                tags.append(db(db.tag.id == t).select().first())
            topic.tags = tags

        company = db(db.company.id == topic.company).select().first()
        user = db(db.auth_user.id == topic.created_by).select().first()
        owner = db((db.company_team.company_id == company) & (db.company_team.role == 'owner')).select().first()
        # Respostas do tópico
        replies = db(db.reply.topic == topic).select()

        # Formulário para resposta do tópico
        form_reply = SQLFORM(db.reply)
        if form_reply.validate():
            if request.vars.reply_id:
                print 'Edição de resposta'
                print form_reply.vars
                db(db.reply.id == request.vars.reply_id).update(rp_content = request.vars.rp_content)
                response.flash = T('Comment edited!')
                redirect(URL('topic', args=[topic.id]))
            else:
                db.reply.insert(rp_content = request.vars.rp_content, topic = request.vars.topic)
                response.flash = T('Reply sent!')
                redirect(URL('topic', args=[topic.id]))
        elif form_reply.errors:
            response.flash = T('Form has errors!')

        return dict(topic=topic,
                company = company,
                replies = replies,
                user = user,
                owner = owner,
                company_topic = company,
                form_reply = form_reply)

@service.json
@auth.requires_login()
def reply():
    """
    Exposes:
        defaut/reply/edit/[reply id] - Retorna os dados de uma resposta em JSON
    """
    #
    # Expose: default/reply/edit/[reply id]
    #
    if request.args(0) == 'edit':
        reply_id = request.args(1)
        print reply_id
        reply = db(db.reply.id == reply_id).select().first()
        #reply.created_by = db(db.auth_user.id == reply.created_by).select().first()
        return response.json(reply)
    else:
        if request.vars.topic:
            db.reply.topic.default = request.vars.topic
        if request.vars.reply:
            db.reply.reply.default = request.vars.reply

        form = SQLFORM(db.reply)
        if form.process().accepted:
            response.flash = T('Reply sent!')
        elif form.errors:
            response.flash = T('Form has errors!')
        return dict(form=form)

@auth.requires_login()
def define_role():
    if request.vars.user_id:
        db.role.user_id.default = request.vars.user_id
    else:
        response.flash = T('Failed on load! Try again later.')
    if request.vars.company:
        db.role.company.default = request.vars.company
    else:
        response.flash = T('Failed on load! Try again later.')

    role = db((db.role.company == request.vars.company)&(db.role.user_id == request.vars.user_id)).select().first()
    if role:
        form = SQLFORM(db.role, role.id, showid=False)
    else:
        form = SQLFORM(db.role)
    if form.process().accepted:
        response.flash = T('Sucess!')
    elif form.errors:
        response.flash = T('Form has errors!')
    return dict(form=form)

@auth.requires_login()
def search():
    if 'q' in request.vars:
        query = request.vars.q

        # Buscando empresas que o usuário é membro.
        companies = db(db.company_team.user_id == auth.user.id).select()
        # Buscando termo pesquisado nos tópicos de cada empresa que o usuário faz parte.
        topics = list()
        replies = list()
        for company in companies:
            #
            # Resultado de busca pelos tópicos
            #
            tps_for_company = db(
                    (db.topic.title.like('%'+query+'%')) |
                    (db.topic.tp_content.like('%'+query+'%')) &
                    (db.topic.company == company.company_id)
                    ).select()
            if tps_for_company is not None:
                for tps in tps_for_company:
                    # Adicionando as tags aos tópicos.
                    if tps.tags is not None:
                        tags = list()
                        for tag in tps.tags.split('|'):
                            tags.append(db(db.tag.id == tag).select().first())
                        tps.tags = tags
                    # Adicionando o resultado final
                    topics.append(tps)
            #
            # Resultado de busca pelos comentários
            #
            all_topics_for_company = db(db.topic.company == company.company_id).select()
            for topic in all_topics_for_company:
                if topic.tags is not None:
                    tags = list()
                    for tag in topic.tags.split('|'):
                        tags.append(db(db.tag.id == tag).select().first())
                    topic.tags = tags

                replies_with_query = db(
                    (db.reply.rp_content.like('%'+query+'%')) &
                    (db.reply.topic == topic)).select()
                # Adicionando o nl2br aos cmentários
                for reply in replies_with_query:
                    reply.tags = topic.tags
                    replies.append(reply)

        # TODO: Retirar o debug posteriormente
        print 'Debungando a pesquisa ----------------'
        print '---- Tópicos ----'
        print topics
        for t in topics:
            print t.title
        print '---- Respostas ----'
        for r in replies:
            print r
            print r.created_by.first_name


        search = SQLFORM.factory(Field('search'), submit_button=T("Search"), formstyle='divs')
        search.attributes['_action'] = URL('search')
        search.attributes['_name'] = 'search'
        search.attributes['_method'] = 'get'

        search.custom.submit['_class'] = 'form-btn form btn-success form-btn-search'
        search.custom.widget.search['_placeholder'] = T('Search for...')
        search.custom.widget.search['_name'] = 'q'

        for i in search.elements('label'):
            i['_style'] = 'display: none;'
        if search.process().accepted:
            query = request.vars.search
            redirect(URL('search', vars={'q':query}, extension=False), client_side=True)

        return dict(topics=topics, replies=replies, search=search)
    else:
        redirect('companies')


@auth.requires_login()
def get_company():
    if not request.vars.company_name:
        return ''
    pattern = request.vars.company_name.capitalize() + '%'
    selected = [row for row in db(db.company.name.like(pattern, case_sensitive=False)).select()]
    print selected
    return ''.join([DIV(k.name,
                 _onclick="addCompanyId('%(name)s', %(c_id)s)" % dict(name = k.name,c_id = k.id),
                 #_onclick="jQuery('#request_company').val('%s')" % k.name,
                 _name="sugestao"
                 # _onmouseover="this.style.backgroundColor='gray'",
                 # _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])

@auth.requires_login()
def get_user():
    if not request.vars.user_invite:
        return ''
    pattern = request.vars.user_invite.capitalize() + '%'
    #selected = [row.first_name for row in db(db.auth_user.first_name.like(pattern)).select()]
    # {'key':{'id':bla,'name':'Lukas'},'key':{}}
    selected_row = db(db.auth_user.first_name.like(pattern, case_sensitive=False)).select()
    selected = dict()
    i = 0
    for n in selected_row:
        selected[n.first_name] = {'id':n.id}
        i = i+1
    return ''.join([DIV(k,
                 _onclick="jQuery('#user_invite').val('%s')" % k,
                 _id = selected[k]['id'],
                 _name = "sugestao"
                 # _onmouseover="this.style.backgroundColor='gray'",
                 # _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])


def user():

    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    if 'register' in request.args:
        fields_to_hide = ['first_name', 'last_name', 'company', 'site', 'avatar']

        for fieldname in fields_to_hide:
            field = db.auth_user[fieldname]
            field.readable = field.writable = False
        form = auth.register(next=auth.settings.register_next)

    #Formuláriodo linkedin
    elif 'login' in request.args:

        from autenticacao import LinkedInAccount
        auth.settings.login_form = LinkedInAccount()

        session.linkedin = True

        form = auth()

    elif 'retrieve_password' in request.args:
        form = auth.retrieve_password()

    elif 'change_password' in request.args:
        form = auth.change_password()

    elif 'profile' in request.args:

        if auth.is_logged_in():
            user = db(db.auth_user.id == auth.user.id).select().first()
        else:
            user = None

        form = auth.profile()
        form.attributes['_name'] = 'form_profile'
        form_password = auth.change_password()
        form_password.attributes['_name'] = 'form_password'
        form_password.attributes['_id'] = 'form_password'

        form_password.custom.widget.old_password['_placeholder'] = T('Old password')
        form_password.custom.widget.new_password['_placeholder'] = T('New password')
        form_password.custom.widget.new_password2['_placeholder'] = T('Confirm new password')

        """
        Formulário de perfil
        """
        form_profile = auth.profile()
        form_profile.attributes['_name'] = 'form_profile'
        form_profile.attributes['_id'] = 'form_profile'
        form_profile.attributes['_class'] = 'form_profile'

        form_profile.custom.widget.first_name['_placeholder'] = T('Nome de usuário')
        form_profile.custom.widget.company['_placeholder'] = T('Nome da empresa')
        form_profile.custom.widget.email['_placeholder'] = T('Email')
        form_profile.custom.widget.site['_placeholder'] = T('http://minhaempresa.com')

        """
        Formulário networking
        """
        user_networks = db(db.network.created_by == auth.user.id).select().first()

        form_networking = SQLFORM(db.network)
        form_networking.attributes['_id'] = 'form_networking'
        form_networking.attributes['_class'] = 'input-com-sombra'
        form_networking.attributes['_method'] = 'post'

        form_networking.custom.widget.facebook['_placeholder'] = T('Facebook link')
        form_networking.custom.widget.googleplus['_placeholder'] = T('Google Plus link')
        form_networking.custom.widget.twitter['_placeholder'] = T('Twitter link')
        form_networking.custom.widget.linkedin['_placeholder'] = T('LinkedIn link')

        if user_networks is not None:
            if user_networks.facebook is not None: form_networking.custom.widget.facebook['_value'] = user_networks.facebook
            if user_networks.googleplus is not None: form_networking.custom.widget.googleplus['_value'] = user_networks.googleplus
            if user_networks.twitter is not None: form_networking.custom.widget.twitter['_value'] = user_networks.twitter
            if user_networks.linkedin is not None: form_networking.custom.widget.linkedin['_value'] = user_networks.linkedin

        if form_networking.validate():
            # Verifica se tem algum registro no banco de dados
            # Se tiver algum, faz o update um por um,
            if user_networks is not None:
                if user_networks.facebook != form_networking.vars.facebook:
                    db(db.network.created_by == auth.user.id).update(facebook = form_networking.vars.facebook)

                if user_networks.googleplus != form_networking.vars.googleplus:
                    db(db.network.created_by == auth.user.id).update(googleplus = form_networking.vars.googleplus)

                if user_networks.twitter != form_networking.vars.twitter:
                    db(db.network.created_by == auth.user.id).update(twitter = form_networking.vars.twitter)

                if user_networks.linkedin != form_networking.vars.linkedin:
                    db(db.network.created_by == auth.user.id).update(linkedin = form_networking.vars.linkedin)
            # Se não, faz o insert de tudo
            else:
                db.network.insert(
                    facebook = form_networking.vars.facebook,
                    googleplus = form_networking.vars.googleplus,
                    twitter = form_networking.vars.twitter,
                    linkedin = form_networking.vars.linkedin,
                    )
            redirect(URL('user', args='profile'))
        elif form_networking.errors:
            print form_networking.errors

        return dict(form=form, form_profile=form_profile, form_networking=form_networking, networking=user_networks, form_password=form_password, user=user)
    else:
        class_button_css = 'form-btn form btn-success full-width form-btn-reset-password'
        value_button_submit = T("Confirm")
        form = auth()
        if 'request_reset_password' in request.args:
            form.custom.submit['_class'] = class_button_css
            form.custom.submit['_value'] = value_button_submit
            form.custom.widget.email['_class'] = 'full-width'
            form.custom.widget.email['_placeholder'] = 'E-mail'
            for i in form.elements('label'):
                i['_style'] = 'display: none;'
        elif 'reset_password' in request.args:
            form.custom.submit['_class'] = class_button_css
            form.custom.submit['_value'] = value_button_submit
            form.custom.widget.new_password['_placeholder'] = T('Password')
            form.custom.widget.new_password['_class'] = 'half-width input-form-reset-password'
            form.custom.widget.new_password2['_placeholder'] = T('Confirm password')
            form.custom.widget.new_password2['_class'] = 'half-width input-form-reset-password'
            for i in form.elements('label'):
                i['_style'] = 'display: none;'
    return dict(form=form)


def delete():
    if request.args(0) == 'network':
        db(db.network.id == request.args(1)).delete()
        redirect(URL('user', args='profile'))
    if request.args(0) == 'delete_request':
        db(db.request.id == request.args(1)).delete()
        redirect(URL('portfolio'))
    if request.args(0) == 'tag':
        db(db.tag.id == request.args(1)).delete()
        redirect(URL('company', vars={'company':request.args(2)}))

@service.json
@auth.requires_login()
def notification_submit():
    '''
    Função que é chamada via ajax, para aceitar ou recusar uma solicitação.
    Requer as variavéis: company, from_user, submit (booleano, true para aceitar, false para recusar), request id.
    '''
    company = request.vars.company
    from_user= request.vars.from_user
    submit = request.vars.submit
    request_id = request.vars.id
    #request_id =  Pegar o data-id com javascript e enviar na requisição.

    print "Executado: notification_submit"
    if submit == 'true':
        investors = db(db.company.name == company).select('investors')
        investors = investors.split('|')
        investors.append(from_user)
        # Update dos investidores da empresa.
        db(db.company.name == company).update(investors = investors)
        # Retirando a notificação como ativa
        db(db.request.id == request_id).update(accepted = True, is_active = False)
    else:
        #Retirando a notificação e setando como não aceita.
        db(db.request.id == request_id).update(accepted = False, is_active = False)

@service.json
@auth.requires_login()
def image_converter():
    global img_name
    image64 = request.vars.avatar_upload
    if image64 != "valor_default":
        import subprocess
        from convertImage import convertBase64String

        base64Img = image64
        upload_folder = '%s/uploads/' % request.folder

        img_name = convertBase64String(base64Img, upload_folder)

        """if img_name:
            user = db(db.auth_user.id == auth.user.id).select().first()
            # Deleta o avatar antigo
            subprocess.call('rm %s/%s' % (upload_folder,user.avatar), shell=True)
            #Salva o avatar novo
            db(db.auth_user.id == user.id).update(avatar=img_name)
            return True
        else:
            return False """
    else:
        img_name = None

@service.json
@auth.requires_login()
def ajax_upload():
    '''Funcao que eh chamada via ajax, que trata a imagem e salvar no banco
    '''
    image64 = request.vars.image64
    if image64: # and user.id
        import subprocess
        from convertImage import convertBase64String

        base64Img = image64
        upload_folder = '%s/uploads/' % request.folder

        img_name = convertBase64String(base64Img, upload_folder)

        if request.vars.company:
            company = db(db.company.id == request.vars.company).select().first()
            # Deleta o avatar antigo
            subprocess.call('rm %s/%s' % (upload_folder, company.avatar), shell=True)
            # Salva o avatar novo
            db(db.company.id == company.id).update(avatar=img_name)

            return True
        else:
            if img_name:
                user = db(db.auth_user.id == auth.user.id).select().first()

                # Deleta o avatar antigo
                subprocess.call('rm %s/%s' % (upload_folder, user.avatar), shell=True)

                # Salva o avatar novo
                db(db.auth_user.id == user.id).update(avatar=img_name)
                return True
            else:
                return False

    else:
        return False

def validate_profile_form():
    """
    Função que é chamada via ajax para validar as informações do formulário de perfil.
    """
    if auth.is_logged_in():
        user = db(db.auth_user.id == auth.user.id).select().first()
    else:
        user = None

    print request.vars
    return True

def nl2br(str):
    """
    Função para cnverter a nova linha para <br />
    Mode de user na view: {{=XML(str)}}
    """
    str = str.encode('string_escape')
    str = str.replace('\\n','<br />')
    str = str.decode('string_escape')

    return str

def nlascii(str):
    str = str.split('\r\n')
    u = ''
    for s in str:
        if str.index(s) == 0:
            u = s
        else:
            if s == '':
                u = u+"\\r\\n%s" % s
            else:
                u = u+"\\r\\n%s" % s
    return u


@service.json
@auth.requires_login()
def get_avatar():
    '''Function that returns the name of the user avatar's file
    '''
    user = db(db.auth_user.id == auth.user.id).select().first()
    auth.user.avatar = user.avatar
    return user.avatar

def get_company_avatar():
    '''Function that returns the name of the user avatar's file
    '''
    company = db(db.company.id == request.vars.company).select().first()
    return company.avatar

def reply_to_edit():
    reply = db(db.reply.id == request.vars.id).select().first()
    return response.json(reply)

def delete_reply():
    db(db.reply.id == request.vars.id).delete()
    response.flash = T("Comentário apagado")
    if request.vars.company == 'recent':
        redirect(URL('recent_activity'))
    else:
        redirect(URL('company',vars=dict(company = request.vars.company)))

@service.json
@auth.requires_login()
def add_user_to_company():
    """
    Função que será chamada via ajax para adicionar um membro a uma organização.
    """
    user_id =  request.vars.id
    company_id = request.vars.company
    team = db(db.company_team.company_id == company_id).select()
    has_member = False
    # Verificando se o membro já está na empresa
    for member in team:
        if int(member.user_id) == int(user_id):
            has_member = True
        # Verificando se é o dono
        company = db(db.company.id == company_id).select().first()
        if company.created_by == user_id:
            has_member = True

    if has_member == False:
        db.company_team.insert(company_id = company_id, user_id = user_id, role = request.vars.role)
        response.flash = T("Membro adicionado com sucesso")
    else:
        response.flash = T("Membro já está na empresa")

    # Caso seja proveniente de uma solicitação de investimento
    if request.vars.rid:
        db(db.request.id == request.vars.rid).update(accepted = True, is_active = False)

    print response.flash
    return True

def delete_user_of_company():
    """
    Função chamda via ajax para apagar um membro de uma empresa.
    """
    user_id =  request.vars.id
    company_id = request.vars.company
    company =  db(db.company.id == company_id).select().first()

    user_to_delete = db((db.company_team.company_id == company_id) & (db.company_team.user_id == user_id)).select().first()
    owner = db((db.company_team.company_id == company_id) & (db.company_team.role == 'owner')).select().first()
    # Um usuário só pode ser excluido por ele mesmo ou pelo dono da empresa.
    if auth.user.id != user_to_delete.user_id:
        # Caso seja o dono
        if int(owner.user_id) == int(auth.user.id):
            db((db.company_team.company_id == company_id) & (db.company_team.user_id == user_id)).delete()
            session.flash = T('O membro foi removido')
            print session.flash
            redirect(URL('company', vars=dict(company=company_id)))

        else:
            session.flash = T('Você não tem autorização para excluir membros do time.')
            print session.flash
            redirect(URL('company', vars=dict(company=company_id)))
    else:
        if user_to_delete.role == 'owner':
            session.flash = T('Não se pode deletar o dono da empresa.')
            print session.flash
            redirect(URL('company', vars=dict(company=company_id)))
        else:
            db((db.company_team.company_id == company_id) & (db.company_team.user_id == user_id)).delete()
            session.flash = T('O membro foi removido')
            print session.flash
            redirect(URL('company', vars=dict(company=company_id)))
    return ()

@service.json
def get_topic_category():
    '''
    Uso: passando na url o valor topic=id_topic

    get_topic_category?topic=1

    '''

    topic = db(db.topic.id == request.vars.topic).select().first()
    tags = list()
    for tag in topic.tags.split('|'):
        t = db((db.tag.id == tag) & (db.tag.is_active == True)).select().first()
        tags.append(t.tag)
    print tags

    return response.json(tags)

@service.json
def get_category():
    '''
        Uso: passar um parâmetro company=id_empresa

        get_category?company=1
    '''


    company_id = request.vars.company
    company = db(db.company.id == company_id).select().first()
    category = db(db.tag.company == company.id).select().as_dict()

    category_json = dict(categorias='')
    category_json['categorias'] = list()

    for c in category:
        category_name = dict(nome = category[c]['tag'])
        category_json['categorias'].append(category_name)

    return response.json(category_json)

@service.json
def create_category():
    from random import choice

    tags = []
    print 'criando categoria'
    category_name = request.vars.category.capitalize()
    company = db(db.company.id == request.vars.company).select().first()

    user = db(db.auth_user.id == auth.user.id).select().first()
    categories = db(db.tag.company == company.id).select()

    for category in categories:
        tags.append(category.tag.lower())

    #Verificação se existe na própria empresa
    if category_name.lower() in tags:
        response.flash = T("Esta categoria já existe")
        return False
    else:
        if category != '':

            #Verificação se existe em toda base de dados
            data_cat = db(db.tag.tag == category_name).select().first()

            if data_cat:
                print 'existe categoria'
                cor_escolhida = data_cat.color
            else:
                print 'categoria nova'
                cor_escolhida = choice(cores_disponiveis()).id

            db.tag.insert(
                tag = category_name,
                company = company.id,
                created_by = user.id,
                modified_by = user.id,
                is_active = True,
                color=cor_escolhida
                )

            # #atualizando status usado da cor
            db(db.colors.id == cor_escolhida).update(used=True)

            response.flash = T("Categoria criada com sucesso")
        else:
            # Caso a categoria esteja vazia não cria ela.
            return False
        return True

def decline_request_to_invest():
    """
    Função chamada via ajax para rejeitar uma solicitação de investimento
    """
    #db(db.request.id == request.vars.rid).delete()
    db(db.request.id == request.vars.rid).update(accepted = False, is_active = bool(False))
    #response.flash = T('Solicitação recusada/cancelada')

    return True

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def testaAjax():

    print request.vars

    return True

@auth.requires_login()
def reports():

    from datetime import datetime,date,time
    from time import strptime

    my_companies = [company.name for company in get_companies(auth.user.id)]

    if request.post_vars['data-dia']:

        #Pega a data enviada e transforma para datetime
        dia = datetime.strptime(request.post_vars['data-dia'],"%d/%m/%Y")

        #cria um tempo zerado
        tempo = time(00,00,00)

        #combina a data fornecida com o tempo criado (para criar um datetime completo)
        dia = datetime.combine(dia,tempo)

    else:
        #Usará a data normal do sistema
        dia = utc_to_local(datetime.now())


    #Cria uma session para transferir a data de um controller para o outro
    session.dia = dia


    dict_meses = {
        1:'Janeiro',2:'Fevereiro',3:'Março',
        4:'Abril',5:'Maio',6:'Junho',7:'Julho',
        8:'Agosto',9:'Setembro',10:'Outubro',
        11:'Novembro',12:'Dezembro'
    }

    componentes_data = {
        'dia':str(dia.day),
        'mes':dict_meses[dia.month],
        'ano':str(dia.year)
    }

    return dict(empresas=my_companies,dia=componentes_data)


@auth.requires_login()
@service.json
def data_charts():

    from datetime import datetime

    colors , tags = [] , []
    cat_colors = {}
    all_data = []
    data_empresa  = {}
    data = {}

    my_companies = get_companies(auth.user.id)

    if session.dia:
        dia  = session.dia
    else:
        dia = utc_to_local(datetime.now())


    for empresa in my_companies:

        min_range = dia.replace(hour=00,minute=00,second=00)
        max_range = dia.replace(hour=23,minute=59,second=59)

        #Gera os intervalos com horários ou datas
        ranges = intervalo_datas(min_range,max_range,salto='horas')

        tags = [tag['tag'] for tag in db(db.tag.company == empresa.id).select(db.tag.tag).as_list()]

        data_empresa['labels'] = [intervalo.strftime("%Hhrs") for intervalo in ranges]

        data_empresa['datasets'] = []

        for tag in tags:
            data['label'] = tag.capitalize()
            data['fillColor'] = 'rgba(255,255,255,0)'
            data['strokeColor'] = get_color(tag)
            data['pointColor'] = get_color(tag)

            lista_quant = []
            #Para cada categoria entrar no período especificado para contar os posts.
            for interval in ranges:

                topics = get_topics(company=empresa.id,categoria=tag)

                #usa uma função que retorna os posts por data fornecida
                dados = post_to_date(topics,date=interval,max_atributo='hora')

                #Uma lista com a quantidade de posts em cada intervalo
                lista_quant.append(len(dados))

            data['data'] = lista_quant

            data_empresa['datasets'].append(data.copy())
        all_data.append(data_empresa.copy())

    return response.json(all_data)

def define_timezone():
    """Chamada ajax para requisitar o timezone do usuario"""
    tz_name = request.vars.name

    from pytz import all_timezones_set

    if tz_name in all_timezones_set:
        session.user_timezone = tz_name

def get_categories():

    if not request.vars.AddCategoria:
        return ''

    busca = request.vars.AddCategoria.capitalize()+"%"

    categorias_escolhidas = [categoria for categoria in db(db.tag.tag.like(busca,case_sensitive=False)).select(db.tag.tag,distinct=True)]

    return ''.join([DIV(categoria.tag,
                 _onclick="jQuery('#newCategoria').val('%s')" % categoria.tag,
                 _name="sugestao"
                 ).xml() for categoria in categorias_escolhidas] )
    return dict()


@auth.requires_login()
def oauth2callback():

    token = request.vars['code']

    if token is None or session.flow is None:
        redirect(URL(request.application, 'default', 'get_credentials'))

    session.token = token

    #Carrega o objeto que estava na forma de bit

    session.flow = pickle.loads(session.flow)

    #try:
    credentials = session.flow.step2_exchange(session.token)
    session.credentials = credentials.to_json()
    if(session.saveCredential):
        db.google_token.insert(user_id = auth.user.id,
                                   token=credentials.to_json()
                                   )
    else:
        db(db.google_token.user_id == auth.user.id).update(token=credentials.to_json())

    db.commit()
    #except FlowExchangeError, error:
    #    raise NameError (error)

    session.http_auth = credentials.authorize(httplib2.Http())

    if(TESTEMODE is not None):
        return dict(token=token)

    redirect(URL(request.application, 'default', 'recent_activity'))

@auth.requires_login()
def share_drive():
    pass

@auth.requires_login()
def get_driver_service():
    result = None
    if(session.credentials is None):
        redirect(URL('default', 'get_credentials'))

    service = get_service('drive', 'v2')
    if(service is not None):
        result = []
        page_token = None
        while True:
            try:
                param = {'q':"mimeType='application/vnd.google-apps.spreadsheet'"}
                if page_token:
                    param['pageToken'] = page_token
                files = service.files().list(**param).execute()

                result.extend(files['items'])
                page_token = files.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break

    return dict(result=result)

@auth.requires_login()
def sheetList():
    idSheet = request.vars['idSheet']


    if(session.credentials is None):
        redirect(URL('default', 'get_credentials'))
    sh = get_sheets(idSheet)
    form = None
    if(sh is None):
        redirect(URL('default', 'get_credentials'))

    options = sh[0].keys()
    optionsToShow = [si.encode('utf-8') for si in options]
    equivOptions = {optionsToShow[i]: options[i] for i in range(len(options))}
    form = SQLFORM.factory(
        Field('x', requires = IS_IN_SET(optionsToShow), widget=SQLFORM.widgets.radio.widget),
        #Field('y', requires = IS_IN_SET(options), widget=SQLFORM.widgets.radio.widget),
    )
    x = None
    #y = None
    if form.process().accepted:
        x = [sh[i][equivOptions[form.vars['x']]] for i in range(len(sh))]
        try:
            if(',' in x[1]):
                x = conversorListaPlanilhasNumeros(x)
        except:
            pass
        #y = [sh[i][form.vars['y']] for i in range(len(sh))]
    return dict(sheet=sh, form=form, x=x)

@auth.requires_login()
def get_analytics_service():
    result = None
    profile_id = None
    service = get_service('analytics', 'v3')
    if(service is not None):
        accounts = service.management().accounts().list().execute()
        if accounts.get('items'):
            account = accounts.get('items')[0].get('id')
            # Get a list of all the properties for the first account.
            properties = service.management().webproperties().list(
                accountId=account).execute()
            if properties.get('items'):
              # Get the first property id.
              property = properties.get('items')[0].get('id')

              # Get a list of all views (profiles) for the first property.
              profiles = service.management().profiles().list(
                  accountId=account,
                  webPropertyId=property).execute()

              if profiles.get('items'):
                # return the first view (profile) id.
                profile_id =  profiles.get('items')[0].get('id')

        if(profile_id is not None):
            outputs = service.data().ga().get(
                ids='ga:' + profile_id,
                start_date='10daysAgo',
                end_date="today",
                metrics='ga:visits',
                dimensions='ga:date',
                start_index='1',
                max_results='25'
            ).execute()
            header = []
            for hd in outputs.get('columnHeaders'):
                header.append('%30s' % hd.get('name'))
            dados = []
            for d in outputs.get('rows', []):
                dados.append([datetime.strptime(d[0], '%Y%m%d'), int(d[1])])
            result = [header, dados]
    return  dict(profile_id=outputs.get('profileInfo').get('profileName'), result=result)



@auth.requires_login()
def get_credentials():
    SCOPES = [DRIVE_SCOPE, SHEET_SCOPE, DOC_SCOPE,
              ANALYTICS_SCOPE, ANALYTICS_SCOPE_USERS]

    testLoc = URL(args=request.args, vars=request.vars, host=True)

    testLoc  = testLoc.split('/')[2]
    if('127.0.0.1' in testLoc or 'localhost' in testLoc):
        arquivo = 'private/localhost_secrets.json'
    else:
        arquivo = 'private/server_secrets.json'

    CLIENT_SECRET_FILE = os.path.join(request.folder, arquivo)
    callback = ROOT + request.application + '/default/oauth2callback'

    flow = client.flow_from_clientsecrets(
                               CLIENT_SECRET_FILE,
                               ' '.join(SCOPES),
                               redirect_uri = callback
                                )

    authorise_url = flow.step1_get_authorize_url()

    # Faz o stream de um objeto em bit
    session.flow = pickle.dumps(flow)

    if(TESTEMODE is not None):
        return dict(authorise_url=authorise_url)

    redirect(authorise_url)

def teste_email():
    msg = 'Olar'
    form = SQLFORM.factory(
            Field('nome', requires=IS_NOT_EMPTY()),
            Field('email', requires=IS_EMAIL()),
            Field('mensagem', 'text', requires=IS_NOT_EMPTY())
            )
    if form.process().accepted:
        enviado = mail.send(
            to = request.vars.email,
            reply_to = request.vars.email,
            subject = "Novo contato pelo site",
            message = "Contato de %s pelo site, dizendo: %s" % (request.vars.nome, request.vars.mensagem)
        )
        if enviado:
            msg = 'Email enviado com sucesso!'
        else:
            msg = 'Falha ao enviar email: %s' %enviado
    elif form.errors:
        msg = form.errors
    return dict(form=form, msg=msg)
