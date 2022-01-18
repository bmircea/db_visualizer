from asyncio.log import logger
from cmath import log
from sqlite3 import DatabaseError
import sqlite3
from urllib import request
from django import template
from django.db import connection, models
from django.http import HttpResponse, response, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from visualizer.connection import create_connection, create_cursor, get_user_tables, connection_wrapper
from django.shortcuts import render, redirect
import logging

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
    pk_value = request.POST['pk_value']
    pk_name = request.POST['pk_name']
    conn, curs = connection_wrapper()
    curs.execute("SELECT * FROM {0}".format(db_name))
    curs.fetchall()
    cols = curs.column_names


    query_update_part = ""
    logger.warning(curs.description)



    i = 1
    for col in cols[1:]:
        col_val = ''
        if request.POST[col] == 'None':
            col_val = 'NULL'
        else:
            col_val = request.POST[col]
        query_update_part += col
        query_update_part += '='
        if (curs.description[i][1] == 253):
            query_update_part += ("'" + col_val + "'")
        else:
            query_update_part += col_val
        query_update_part += ','
        i += 1

    query_update_part = query_update_part[:-1]

    query = "UPDATE {0} SET {1} WHERE {2} = {3};".format(
        db_name,
        query_update_part,
        pk_name, 
        pk_value)
    
    logger.warning(query)

    try:
        curs.execute(query)
        curs.execute('commit;')
    except sqlite3.Error as e:
        msg = 'Fail : {0} -> {1}'.format(query, e) 
        raise DatabaseError(msg)
    
    redir_url = '/visualizer/db/{0}'.format(db_name)
    return redirect(redir_url)

def update_page(request):
    template = loader.get_template('visualizer/update.html')
    db_name = request.POST['db_name']    
    pk_name = request.POST['pk_name']
    pk_value = request.POST['id_to_upd']    
    data = []

    conn, curs = connection_wrapper()
    curs.execute("SELECT * FROM {0} WHERE {1} = {2}".format(db_name, pk_name, pk_value))
    resp = curs.fetchone()
    cols = curs.column_names
    
    for row in zip(cols, resp):
        data.append(row)

    data.remove(data[0])

    context = {
        'db_name': db_name,
        'pk_name': pk_name,
        'pk_value': pk_value,
        'data': data
    }


    return HttpResponse(template.render(context, request))

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