examples = [{
    "question": "Is Officer 'Ilham Alyev' is connected to any other Officer named 'Aliyeva'?",
    "answer": """MATCH (a:Officer{name:'Ilham Aliyev'})-[:officer_of*1..3]-(b:Officer) WHERE b.name CONTAINS 'Aliyeva' RETURN DISTINCT b.name"""
}, {
    "question": 'Where is "Mehriban Aliyeva" located?',
    "answer": """MATCH (n:Officer{name:"Mehriban Aliyeva"})-[:registered_address]->(a:Address) RETURN a.address"""
}, {
    "question": 'which is the most connected Intermediary?',
    "answer": """MATCH (i:Intermediary) RETURN i.name, SIZE([(i)-[]-(o:Officer) | o]) AS officer_connections, SIZE([(i)-[]-(e:Entity) | e]) AS entity_connections ORDER BY officer_connections DESC, entity_connections DESC LIMIT 1"""
}, {
    "question": 'What is the address of Mossack Fonseca & Co. Ecuador S.A.?',
    "answer": """MATCH (e:Entity{name: "Mossack Fonseca & Co. Ecuador S.A."}) RETURN e.address"""
}, {
    "question": 'Where do most Officers come from?',
    "answer": """MATCH (o:Officer)-[]->(a:Address) WHERE a.countries is not null RETURN a.countries, COUNT(o) ORDER BY COUNT(o) DESC LIMIT 1"""
}, {
    "question": 'Name top 5 countries has the most number of Entities',
    "answer": """MATCH (e:Entity)-->(a:Address) WHERE a.countries is not null WITH a.countries AS country, count(DISTINCT e) AS numEntities RETURN country, numEntities ORDER BY numEntities DESC LIMIT 5"""
}, {
    "question": 'Name two similar officers located in UAE?',
    "answer": """MATCH (a:Officer)-[:officer_of]->(:Entity)-[:registered_address]->(:Address{countries:"United Arab Emirates"})<-[:registered_address]-(:Entity)<-[:officer_of]-(b:Officer) WHERE (a)-[:similar]-(b) RETURN DISTINCT a.name, b.name LIMIT 2"""
}, {
    "question": "Fetch all the Officers associated with another Officer named 'GORYUKHIN'",
    "answer": """MATCH (o:Officer)-[:officer_of*1..3]-(b:Officer) WHERE o.name CONTAINS 'GORYUKHIN' RETURN DISTINCT b.name"""
}, {
    "question": 'What are all the companies that Neelie Kroes has direct links to?',
    "answer": """MATCH (o:Officer{name:"Neelie Kroes"})-[:officer_of]->(c:Entity) RETURN DISTINCT c.name"""
}, {
    "question": "Which leaks was 'MINT HOLDINGS LTD.' associated?",
    "answer": """MATCH (e:Entity) WHERE e.name =~ 'MINT HOLDINGS LTD.' RETURN e.sourceID"""
}, {
    "question": "what is the shortest path between 'Ilham Aliyev' & 'Mehriban Aliyeva'?",
    "answer": """MATCH (a:Officer),(b:Officer)
        WHERE a.name CONTAINS 'Ilham Aliyev' 
          AND b.name CONTAINS 'Mehriban Aliyeva'
        MATCH p=allShortestPaths((a)-[:officer_of|intermediary_of|registered_address*..10]-(b))
        return distinct reduce(s=head(nodes(p)).name, n in tail(nodes(p)) | s+"->"+n.name) as path
        LIMIT 50"""
}, {
    "question": "What is the relationship between 'Ilham Aliyev' & 'Mehriban Aliyeva'?",
    "answer": """MATCH (a:Officer),(b:Officer)
        WHERE a.name CONTAINS 'Ilham Aliyev' 
          AND b.name CONTAINS 'Mehriban Aliyeva'
        MATCH p=allShortestPaths((a)-[:officer_of|intermediary_of|registered_address*..10]-(b))
        return distinct reduce(s=head(nodes(p)).name, n in tail(nodes(p)) | s+"->"+n.name) as path
        LIMIT 50"""
}, {
    "question": 'what are the Entities that are named "Mossack Fonseca"',
    "answer": """MATCH (e:Entity) WHERE e.name CONTAINS "Mossack Fonseca" RETURN e.name"""
}, {
    "question": 'Name 5 companies from Taiwan that have high degree centrality.',
    "answer": """MATCH (e:Entity)-[:registered_address]->(a:Address{countries:"Taiwan"}) WITH e, COUNT(*) AS degree_centrality RETURN e.name, degree_centrality ORDER BY degree_centrality DESC LIMIT 5"""
}, {
    "question": "How many Shell companies are owned by Taiwanese?",
    "answer": """
    MATCH (o:Officer)-[:officer_of]->(e:Entity), (o)-[:registered_address]->(a:Address{countries:"Taiwan"}) RETURN COUNT(DISTINCT e)
    """
}]

instr_template = """
Here are the instructions to follow:
1. Use the Neo4j schema to generate cypher compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher.
3. Use only Nodes and relationships mentioned in the schema while generating the reponse
4. Reply ONLY in Cypher when it makes sense.
5. Whenever you search for an Officer name or an Entity name or an Intermediary name, always do case-insensitive and fuzzy search
6. Officer node is synonymous to Person
7. Entity nodes are synonymous to Shell Companies
"""


template = """
Using this Neo4j schema and Reply ONLY in Cypher when it makes sense.

Schema: {text}
"""

schema = """[{"keys":["nodes","relationships"],"_fields":[[{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"connected_to"},"elementId":"-34"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\",\"start_date\",\"end_date\",\"lastEditTimestamp\"]","id":"intermediary_of"},"elementId":"-38"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"status\",\"valid_until\",\"link\",\"start_date\",\"end_date\",\"lastEditTimestamp\"]","id":"officer_of"},"elementId":"-42"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"probably_same_officer_as"},"elementId":"-46"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\",\"lastEditTimestamp\"]","id":"registered_address"},"elementId":"-50"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"same_address_as"},"elementId":"-54"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"link\"]","id":"same_as"},"elementId":"-58"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"same_company_as"},"elementId":"-62"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"same_id_as"},"elementId":"-66"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"same_intermediary_as"},"elementId":"-70"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\"]","id":"same_name_as"},"elementId":"-74"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\"]","id":"same_name_as_1"},"elementId":"-78"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"link\",\"lastEditTimestamp\"]","id":"same_name_as_2"},"elementId":"-82"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"link\"]","id":"similar"},"elementId":"-86"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"similar_company_as"},"elementId":"-90"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"valid_until\",\"link\"]","id":"underlying"},"elementId":"-94"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"valid_until\",\"link\"]","id":"underlying_1"},"elementId":"-98"},{"labels":["RelationshipTypes"],"properties":{"properties":"[\"link\",\"lastEditTimestamp\"]","id":"underlying_2"},"elementId":"-102"},{"labels":["NodeLabel","Token"],"properties":{"value":"Officer","id":"nl:Officer"},"elementId":"-5"},{"labels":["NodeLabel","Token"],"properties":{"value":"Address","id":"nl:Address"},"elementId":"-4"},{"labels":["NodeLabel","Token"],"properties":{"value":"Entity","id":"nl:Entity"},"elementId":"-2"},{"labels":["NodeLabel","Token"],"properties":{"value":"Intermediary","id":"nl:Intermediary"},"elementId":"-3"},{"labels":["NodeLabel","Token"],"properties":{"value":"Other","id":"nl:Other"},"elementId":"-6"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_intermediary_as","id":"rt:same_intermediary_as"},"elementId":"-10"},{"labels":["RelationshipType","Token"],"properties":{"value":"similar_company_as","id":"rt:similar_company_as"},"elementId":"-15"},{"labels":["RelationshipType","Token"],"properties":{"value":"officer_of","id":"rt:officer_of"},"elementId":"-18"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_id_as","id":"rt:same_id_as"},"elementId":"-13"},{"labels":["RelationshipType","Token"],"properties":{"value":"underlying","id":"rt:underlying"},"elementId":"-14"},{"labels":["RelationshipType","Token"],"properties":{"value":"intermediary_of","id":"rt:intermediary_of"},"elementId":"-9"},{"labels":["RelationshipType","Token"],"properties":{"value":"registered_address","id":"rt:registered_address"},"elementId":"-11"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_as","id":"rt:same_as"},"elementId":"-12"},{"labels":["RelationshipType","Token"],"properties":{"value":"connected_to","id":"rt:connected_to"},"elementId":"-17"},{"labels":["RelationshipType","Token"],"properties":{"value":"probably_same_officer_as","id":"rt:probably_same_officer_as"},"elementId":"-19"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_name_as","id":"rt:same_name_as"},"elementId":"-8"},{"labels":["RelationshipType","Token"],"properties":{"value":"similar","id":"rt:similar"},"elementId":"-7"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_company_as","id":"rt:same_company_as"},"elementId":"-20"},{"labels":["RelationshipType","Token"],"properties":{"value":"same_address_as","id":"rt:same_address_as"},"elementId":"-16"},{"labels":["NodeObjectType"],"properties":{"properties":"[\"name\",\"valid_until\",\"countries\",\"country_codes\",\"lastEditTimestamp\"]","id":"n:Intermediary:Officer"},"elementId":"-27"},{"labels":["NodeObjectType"],"properties":{"properties":"[\"name\",\"original_name\",\"jurisdiction\",\"jurisdiction_description\",\"incorporation_date\",\"inactivation_date\",\"struck_off_date\",\"status\",\"service_provider\",\"address\",\"ibcRUC\",\"valid_until\",\"former_name\",\"note\",\"dorm_date\",\"company_type\",\"tax_stat_description\",\"countries\",\"country_codes\",\"company_number\",\"type\",\"registration_date\",\"closed_date\",\"comments\",\"lastEditTimestamp\",\"entity_number\"]","id":"n:Entity"},"elementId":"-23"},{"labels":["NodeObjectType"],"properties":{"properties":"[\"name\",\"status\",\"address\",\"valid_until\",\"note\",\"countries\",\"country_codes\",\"registered_office\",\"lastEditTimestamp\"]","id":"n:Intermediary"},"elementId":"-25"},{"labels":["NodeObjectType"],"properties":{"properties":"[\"name\",\"jurisdiction\",\"jurisdiction_description\",\"incorporation_date\",\"struck_off_date\",\"valid_until\",\"note\",\"countries\",\"country_codes\",\"closed_date\",\"type\",\"lastEditTimestamp\"]","id":"n:Other"},"elementId":"-32"},{"labels":["NodeObjectType"],"properties":{"properties":"[\"name\",\"status\",\"address\",\"valid_until\",\"icij_id\",\"note\",\"countries\",\"country_codes\",\"original_address\",\"addressID\",\"country\",\"country_code\",\"lastEditTimestamp\"]","id":"n:Address"},"elementId":"-21"},{"labels":["NodeObjectType"],"properties":{"properties":"[{\"type\":\"integer\"}]},\"name\",\"status\",\"address\",\"valid_until\",\"icij_id\",\"note\",\"end_date\",\"countries\",\"country_codes\",\"lastEditTimestamp\"]","id":"n:Officer"},"elementId":"-30"}],[{"type":"HAS_LABEL","elementId":"-22","startNodeElementId":"-21","endNodeElementId":"-4"},{"type":"HAS_LABEL","elementId":"-24","startNodeElementId":"-23","endNodeElementId":"-2"},{"type":"HAS_LABEL","elementId":"-26","startNodeElementId":"-25","endNodeElementId":"-3"},{"type":"HAS_LABEL","elementId":"-28","startNodeElementId":"-27","endNodeElementId":"-3"},{"type":"HAS_LABEL","elementId":"-29","startNodeElementId":"-27","endNodeElementId":"-5"},{"type":"HAS_LABEL","elementId":"-31","startNodeElementId":"-30","endNodeElementId":"-5"},{"type":"HAS_LABEL","elementId":"-33","startNodeElementId":"-32","endNodeElementId":"-6"},{"type":"HAS_TYPE","elementId":"-35","startNodeElementId":"-34","endNodeElementId":"-17"},{"type":"FROM","elementId":"-36","startNodeElementId":"-34","endNodeElementId":"-32"},{"type":"TO","elementId":"-37","startNodeElementId":"-34","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-39","startNodeElementId":"-38","endNodeElementId":"-9"},{"type":"FROM","elementId":"-40","startNodeElementId":"-38","endNodeElementId":"-25"},{"type":"TO","elementId":"-41","startNodeElementId":"-38","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-43","startNodeElementId":"-42","endNodeElementId":"-18"},{"type":"FROM","elementId":"-44","startNodeElementId":"-42","endNodeElementId":"-30"},{"type":"TO","elementId":"-45","startNodeElementId":"-42","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-47","startNodeElementId":"-46","endNodeElementId":"-19"},{"type":"FROM","elementId":"-48","startNodeElementId":"-46","endNodeElementId":"-30"},{"type":"TO","elementId":"-49","startNodeElementId":"-46","endNodeElementId":"-30"},{"type":"HAS_TYPE","elementId":"-51","startNodeElementId":"-50","endNodeElementId":"-11"},{"type":"FROM","elementId":"-52","startNodeElementId":"-50","endNodeElementId":"-23"},{"type":"TO","elementId":"-53","startNodeElementId":"-50","endNodeElementId":"-21"},{"type":"HAS_TYPE","elementId":"-55","startNodeElementId":"-54","endNodeElementId":"-16"},{"type":"FROM","elementId":"-56","startNodeElementId":"-54","endNodeElementId":"-21"},{"type":"TO","elementId":"-57","startNodeElementId":"-54","endNodeElementId":"-21"},{"type":"HAS_TYPE","elementId":"-59","startNodeElementId":"-58","endNodeElementId":"-12"},{"type":"FROM","elementId":"-60","startNodeElementId":"-58","endNodeElementId":"-23"},{"type":"TO","elementId":"-61","startNodeElementId":"-58","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-63","startNodeElementId":"-62","endNodeElementId":"-20"},{"type":"FROM","elementId":"-64","startNodeElementId":"-62","endNodeElementId":"-23"},{"type":"TO","elementId":"-65","startNodeElementId":"-62","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-67","startNodeElementId":"-66","endNodeElementId":"-13"},{"type":"FROM","elementId":"-68","startNodeElementId":"-66","endNodeElementId":"-30"},{"type":"TO","elementId":"-69","startNodeElementId":"-66","endNodeElementId":"-30"},{"type":"HAS_TYPE","elementId":"-71","startNodeElementId":"-70","endNodeElementId":"-10"},{"type":"FROM","elementId":"-72","startNodeElementId":"-70","endNodeElementId":"-25"},{"type":"TO","elementId":"-73","startNodeElementId":"-70","endNodeElementId":"-25"},{"type":"HAS_TYPE","elementId":"-75","startNodeElementId":"-74","endNodeElementId":"-8"},{"type":"FROM","elementId":"-76","startNodeElementId":"-74","endNodeElementId":"-25"},{"type":"TO","elementId":"-77","startNodeElementId":"-74","endNodeElementId":"-25"},{"type":"HAS_TYPE","elementId":"-79","startNodeElementId":"-78","endNodeElementId":"-8"},{"type":"FROM","elementId":"-80","startNodeElementId":"-78","endNodeElementId":"-30"},{"type":"TO","elementId":"-81","startNodeElementId":"-78","endNodeElementId":"-30"},{"type":"HAS_TYPE","elementId":"-83","startNodeElementId":"-82","endNodeElementId":"-8"},{"type":"FROM","elementId":"-84","startNodeElementId":"-82","endNodeElementId":"-23"},{"type":"TO","elementId":"-85","startNodeElementId":"-82","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-87","startNodeElementId":"-86","endNodeElementId":"-7"},{"type":"FROM","elementId":"-88","startNodeElementId":"-86","endNodeElementId":"-30"},{"type":"TO","elementId":"-89","startNodeElementId":"-86","endNodeElementId":"-30"},{"type":"HAS_TYPE","elementId":"-91","startNodeElementId":"-90","endNodeElementId":"-15"},{"type":"FROM","elementId":"-92","startNodeElementId":"-90","endNodeElementId":"-23"},{"type":"TO","elementId":"-93","startNodeElementId":"-90","endNodeElementId":"-23"},{"type":"HAS_TYPE","elementId":"-95","startNodeElementId":"-94","endNodeElementId":"-14"},{"type":"FROM","elementId":"-96","startNodeElementId":"-94","endNodeElementId":"-30"},{"type":"TO","elementId":"-97","startNodeElementId":"-94","endNodeElementId":"-30"},{"type":"HAS_TYPE","elementId":"-99","startNodeElementId":"-98","endNodeElementId":"-14"},{"type":"FROM","elementId":"-100","startNodeElementId":"-98","endNodeElementId":"-30"},{"type":"TO","elementId":"-101","startNodeElementId":"-98","endNodeElementId":"-27"},{"type":"HAS_TYPE","elementId":"-103","startNodeElementId":"-102","endNodeElementId":"-14"},{"type":"FROM","elementId":"-104","startNodeElementId":"-102","endNodeElementId":"-32"},{"type":"TO","elementId":"-105","startNodeElementId":"-102","endNodeElementId":"-23"}]]}]"""

output_fmt = """
---------------
The output should be in this JSON format:
{
  "cypher": ".."
}"""
