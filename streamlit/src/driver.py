from neo4j import GraphDatabase

host = 'bolt://host.docker.internal:7689'
user = 'neo4j'
password = 'Foo12345678'
driver = GraphDatabase.driver(host, auth=(user, password))


def read_query(query, params={}):
    with driver.session(database='leaks') as session:
        try:
            result = session.run(query, params)
            response = [returnTextRes(r.values()[0]) for r in result]
            return response
        except Exception as e:
            print(e)
            return ["Oops! LLM Token Limit exceeded or something wrong. Please try again!"]


def returnTextRes(response):
    if(type(response).__name__ == "Node"): 
        return str(response.get('name'))
    elif(type(response).__name__ == "Relationship"): 
        return str(response.start_node.get('name') + " -> " 
                    + response.get('type') + " -> " + response.end_node.name)
    elif(type(response).__name__ == "Path"): 
        return str(response.start_node.get('name') +
                    " -> " + response.end_node.get('name'))
    elif(response == "True"): 
        return "Yes"
    elif(response == "False"): 
        return "No"
    return response


def get_article_text(title):
    text = read_query(
        "MATCH (a:Officer {name:$title}) RETURN a.bodyContent as response", {'title': title})
    return text
