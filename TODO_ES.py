from pyes import *
es = ES("localhost:9200")
es.indices.create_index_if_missing("meguz")

meguz_mapping = {
    'id': {
        'boost': 1.0,
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'integer',
    },
    'title': {
        'boost': 1.0,
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'url': {
        'boost': 1.0,
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'description': {
        'boost': 1.0,
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'video_thumb': {
        'boost': 1.0,
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'publish_date': {
        'store': 'yes',
        'type': 'date',
        "format" : "YYYY-MM-dd"
    },
    'status': {
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',        
    }
}
es.indices.put_mapping("meguz", {'properties':meguz_mapping}, ["meguz"])

doc = {
    "title": "Meguz de prueba",
    "url": "http://meguz.dev",
    "description": "este es un meguz de prueba",
    "video_thumb": "http://img.youtube.com/vi/Jyghg1_g0Ic/1.jpg",
    "publish_date": "2013-11-27",
    "status": "publicado"
}

es.index(doc,"meguz","meguz",1)

obj = es.factory_object("meguz","meguz",{"title":"lala","description":"lala","publish_date":"2013-11-28","status":"publicado","url":"http://www.gig.cl"})
docId = obj.save()
q = TermQuery("title", "prueba")
results = es.search(query=q)
for r in results:
    print r