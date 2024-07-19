from gluon import current
import randomcolor
from datetime import *

def is_url(url):
    from urllib2 import urlopen
    try:
        urlopen(url)
    except:
        return False
    else:
        return True


def g_im_in_the_url(s):
    '''return if are in the url s.'''
    if request.args:
        url = '%s/%s/%s' % (request.controller,
                            request.function, request.args(0))
    else:
        url = '%s/%s' % (request.controller, request.function)

    return (url == s)


def g_current_page(url, x, y=''):
    '''returns x if you are in the url. Else return y '''
    if g_im_in_the_url(url):
        return x
    else:
        return y

def get_avatar():

    if session.linkedin:
        if auth.user.avatar_linkedin:
            return auth.user.avatar_linkedin
        else:
            return URL('static','images/imagemdefault.png')

    else:
        if auth.user.avatar:
            return URL('download', args=auth.user.avatar)
        else:
            return URL('static','images/imagemdefault.png')

# Breadcrumb
name_pages = {
    'recent_activity': T('Recent activity'),
    'companies': T('My companies'),
    'company': T('My companies'),
    'topic': T('Topic'),
    'edit': T('Editar'),
    'new': T('New company'),
    'investments': T('My investments'),
    'enterprising': 'essa pagina vai sumir',
    'user': T('Settings'),
    'login': T('Login'),
    'search': T('Busca'),
    'reports':T('Relatórios')
}


# Pages with search
pages_with_search_enabled = ['company', 'search', 'recent_activity']


# pages and args of pages with menu and breadcrumb disable
pages_with_menu_and_breadcrumb_disabled = ['index', 'welcome']
args_of_pages_with_breadcrumb_disabled = [
    'login', 'register', 'request_reset_password', 'reset_password']




# FUNÇÕES REFERENTES ÀS EMPRESAS 

def get_companies(user,role=None):

    '''
        Pegar as empresas por determinado nivel de integrante (owner,member,investor)
    '''

    #Porteriormente usar o created_by na table company
    todas_empresas = db(db.company_team.user_id == user).select()

    companies_into = []

    for empresa in todas_empresas:
        comp = db(db.company.id == empresa.company_id).select().first()
        companies_into.append(comp)

    return companies_into

def get_color(tag):
    
    '''
        Retorna a cor de determinada categoria, implementar se usar na busca dinâmica da categoria.
    '''

    id_tag = db(db.tag.tag.lower() == tag.lower()).select().first()

    nome_cor = db(db.colors.id == id_tag.color).select(db.colors.color).first()

    return nome_cor.color


def get_topics(company=None,categoria=None):

    '''
        Retorna os posts de determinada tag por empresa, ou todos de uma empresa

        Parâmetros: company -> id da empresa
                    tag-> nome da categoria
                    
                    get_topics(1,'Administração')

        OBS:
            Se não for fornecido o nome da tag, e for o id da empresa,é retornado
            todos os posts dessa empresa.

            get_topics(company=1) -> todos os posts da empresa 1
    '''

    company_id = int(company)

    topics_company = db(db.topic.company == company_id).select()

    if categoria != None and isinstance(categoria,str):

        categorias_empresa = [tag.id for tag in db(db.tag.company == company_id).select()]

        id_tag_procurada = db( (db.tag.tag == categoria) & (db.tag.company == company_id) ).select(db.tag.id).first()

        topics = []
        
        if id_tag_procurada != None:

            if id_tag_procurada.id in categorias_empresa:

                for topic in topics_company:
                    tags_topics = map(int,topic.tags.split("|"))

                    if id_tag_procurada.id in tags_topics:
                        topics.append(topic)

        return topics

    else:
        return topics_company


def post_to_date(topics=None,date=None,max_atributo=None):

    '''
        A função irá retornar os posts que estão na data especificada no
        parametro date, e com o parametro max_atributo verificando até qual
        parametro verificar.

        Uso do atributo max_atributo para definir o atributo datetime para
        usar na verificação da data passada.

        Ex: mes,dia,hora

        Com isso faz-se em condicionais as operações com cada tipo passado via parametro
        
        Por HORA:
            - Comparará a igualdade das datas até o atributo de dia
        Por MES:
            - Comparará a igualdade das datas até o atributo de mes
        Por DIA:
            - Comparará a igualdade das datas até o atributo de dia
        
        - Refatorar depois.

    '''


    topics_date = []

    for topic in topics:

        dia_utc_post = utc_to_local(topic['created_on'])

        if max_atributo == 'dia':
            if (dia_utc_post.year == date.year) and (dia_utc_post.month == date.month) and (dia_utc_post.day == date.day):
                topics_date.append(topic)

        elif max_atributo == 'hora':

            if (dia_utc_post.year == date.year) and (dia_utc_post.month == date.month) and (dia_utc_post.day == date.day) and (dia_utc_post.hour == date.hour):
                topics_date.append(topic)

        else:#Será usado o parametro mês

            if (dia_utc_post.year == date.year) and (dia_utc_post.month == date.month):
                topics_date.append(topic)
                
    return topics_date

def intervalo_datas(d1,d2,salto=None):

    '''
        Cria o intervalo de datas passadas como parametro, e adiciona
        um salto entre as datas.

        Ex: Mensal, por horas, ou diariamente.

        Por MES:
            - Gerará o intervalo baseado nos meses das datas, da data inicial até chegar na data final.
        Por DIA:
            - Gerará o intervalo baseado nos dias das datas, da data inicial até chegar na data final.
        Por HORA:
            - Gerará o intervalo baseado nas horas dos dias da data inicial até chegar na data final.
    '''

    from dateutil import rrule

    intervalo = list()

    if salto == 'horas':

        for data in rrule.rrule(rrule.HOURLY,dtstart=d1,until=d2):

            intervalo.append(data)
        
    elif salto == 'dias':

        for data in rrule.rrule(rrule.DAILY,dtstart=d1,until=d2):

            intervalo.append(data)

    elif salto == 'meses':
        
        for data in rrule.rrule(rrule.MONTHLY,dtstart=d1,until=d2):

            intervalo.append(data)

    return intervalo


#Função para converter de horário UTC para horario timezone local
def utc_to_local(datetime):
    if request.is_local:
        return datetime
    else:

        from pytz import timezone

        tz_utc = timezone('UTC')
        tz_local = timezone(timezone_usuario)

        data_utc = tz_utc.localize(datetime)
        
        return data_utc.astimezone(tz_local)
