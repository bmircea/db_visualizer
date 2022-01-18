from asyncio.log import logger
from cmath import log
from sqlite3 import DatabaseError
from urllib import request
from django import template
from django.db import connection, models
from django.http import HttpResponse, response, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from visualizer.connection import create_connection, create_cursor, get_user_tables, connection_wrapper
from django.shortcuts import render, redirect
import logging
import mysql

def index(request):
    conn = create_connection()
    curs = create_cursor(conn)
    get_user_tables(curs)
    db_names = [db[0] for db in curs.fetchall()]
    template = loader.get_template('visualizer/index.html')
    context = {
        'db_names': db_names,
        'resp': []
    }
    curs.close()
    conn.close()
    return HttpResponse(template.render(context, request))

def db(request, db_name):
    query = "SELECT * FROM {0}".format(db_name)
    logger = logging.getLogger(__name__)
    if request.POST:
        query += " ORDER BY {0}".format(request.POST['column_to_sort'])
    logger.warning(query)
    conn, curs = connection_wrapper()
    curs.execute(query)
    resp = curs.fetchall()
    columns = curs.column_names
    template = loader.get_template('visualizer/db.html')
    context = {
        'resp': resp,
        'columns': columns,
        'db_name': db_name.capitalize(),
        'pk_name': columns[0]
    }
    return HttpResponse(template.render(context, request))

def delete(request):
    logger = logging.getLogger(__name__)
    logger.warning("DELETE")
    db_name = request.POST['db_name']
    idtd = request.POST['id_to_del']
    pk_name = request.POST['pk_name']
    
    query = "DELETE FROM {2} WHERE {0} = {1};".format(
        pk_name, 
        idtd, 
        db_name)
    logger.warning(query)
    conn, curs = connection_wrapper()
    try:
        curs.execute(query)
        curs.execute("commit;")
    except mysql.connector.errors as e:
        msg = 'Fail : {0} -> {1}'.format(query, e) 
        raise DatabaseError(msg)
    curs.close()
    conn.close()
    redir_url = '/visualizer/db/{0}'.format(db_name)
    return redirect(redir_url)

def update(request):
    logger = logging.getLogger(__name__)
    logger.warning("UPDATE")
    db_name = request.POST['db_name']
    idtu = request.POST['id_to_upd']
    logger.warning(idtu)
    
    """"
    query = "UPDATE {2} SET WHERE {0} = {1};".format(
        request.POST['pk_name'], 
        idtd, 
        db_name)
    conn, curs = connection_wrapper()
    try:
        curs.execute(query)
    except mysql.Error as e:
        msg = 'Fail : {0} -> {1}'.format(query, e) 
        raise DatabaseError(msg)
    """

    
    redir_url = '/visualizer/db/{0}'.format(db_name)
    return redirect(redir_url)

def query(request):
    # Procesam cererea
    query_text = request.POST['query_text']
    conn = create_connection()
    curs = conn.cursor(buffered=True)
    logger = logging.getLogger(__name__)
    template = loader.get_template('visualizer/queryres.html')

    curs.execute(query_text)
    resp = []
    logger.warning(query_text)
    
    if query_text.split(" ")[0] == 'SELECT':
        rows = curs.fetchall()
        for row in rows:
            resp.append(row)
    else :
        curs.execute("commit;")
        if query_text.split(" ")[0] == 'INSERT':
            logger.warning("INSERT") 
        
        
    curs.close()
    conn.close()
    context = {
            'resp': resp,
            'text' : query_text
    }
    
    logger.warning(resp)
    return HttpResponse(template.render(context, request))