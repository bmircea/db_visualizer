from django import template
from django.db import connection, models
from django.http import HttpResponse, response, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from visualizer.connection import create_connection, create_cursor, get_user_tables, connection_wrapper
from django.shortcuts import render

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
    conn, curs = connection_wrapper()
    curs.execute(query)
    resp = curs.fetchall()
    columns = curs.column_names
    template = loader.get_template('visualizer/db.html')
    context = {
        'resp': resp,
        'columns': columns,
        'db_name': db_name.capitalize()
    }
    return HttpResponse(template.render(context, request))

def query(request):
    # Procesam cererea
    query_text = request.POST['query_text']
    conn = create_connection()
    curs = create_cursor(conn)
    curs.execute(query_text)
    rows = curs.fetchall()
    resp = []
    for row in rows:
        resp.append(row)
    context = {
        'resp': resp
    }
    curs.close()
    conn.close()

    template = loader.get_template('visualizer/queryres.html')

    return HttpResponse(template.render(context, request))