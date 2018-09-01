import json

from flask import jsonify, request

from app import app, BmgnError

templ_header = "<html><head><title>Bestaat mijn gemeente nog?</title></head><body><h1>Bestaat mijn gemeente nog?</h1>"
templ_footer = "</body></html>"
@app.route("/")
def index():
    return "%s<form action=\"/zoeken\"><input name=\"q\" /><input type=\"submit\" /></form>%s" % (
        templ_header, templ_footer,)


@app.route("/zoeken")
def zoeken():
    with open('result.json') as in_file:
        data = json.load(in_file)
    gemeenten = {g['Title'].lower(): g for g in data.values()}
    if request.args['q'].lower() in gemeenten.keys():
        was_found = True
        gem = gemeenten[request.args['q'].lower()]
        if 'merges' in gem:
            result = 'NEE! De gemeente %s was gefuseerd in %s tot %s' % (
                request.args['q'], gem['merges'][0]['year'],
                data[gem['merges'][0]['code']]['Title'])
        else:
            result = 'JA!'
    else:
        was_found = False
        result = 'NEE!'
    return "%s<div>%s</div>%s" % (
        templ_header, result, templ_footer,)
