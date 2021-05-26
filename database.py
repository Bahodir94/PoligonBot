

def array_info(connecter, data, value, aios=False):
    result = []
    for m in get_info(connecter, data):
        result.append(m[value])
    return result

def get_info(connecter, data=False):
    if data:
        return connecter.find(data)
    else:
        return connecter.find()

def update_info(connecter, where, data):
    connecter.update_many(where,{'$set' : data})


def delete_many(connecter, by_what):
    connecter.delete_many(by_what)


def delete_info(connecter, by_what):
    connecter.delete_one(by_what)

def insert_many(connecter, data):
    connecter.insert_many(data)

def insert_into(connecter, data):
    connecter.insert_one(data)

def get_count(connecter, data):
    return connecter.count_documents(data)