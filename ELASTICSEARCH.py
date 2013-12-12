from pyes import *
es = ES("localhost:9200")

# DELETE ?
es.indices.delete_index("prize")
es.indices.delete_index("meguz")

# PRIZE
# Indez
es.indices.create_index_if_missing("prize")

# Mapping
prizeMapping = {
    'id': {
        'store': 'yes',
        'type': 'integer',
    },
    'title': {
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'category': {
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'url': {
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'description': {
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'thumbnail': {
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',
    },
    'vote_limit': {
        'store': 'yes',
        'type': 'integer',
    },
    'vote_source': {
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
es.indices.put_mapping("prize", {'properties':prizeMapping}, ["prize"])

# MEGUZ
# Index
es.indices.create_index_if_missing("meguz")

# Mapping
meguzMapping = {
    'id': {
        'boost': 1.0,
        'index': 'not_analyzed',
        'store': 'yes',
        'type': 'integer',
    },
    'prize_id': {
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
es.indices.put_mapping("meguz", {'properties':meguzMapping}, ["meguz"])