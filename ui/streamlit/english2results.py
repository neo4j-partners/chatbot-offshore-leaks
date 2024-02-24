from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import AzureOpenAIEmbeddings
from retry import retry
from timeit import default_timer as timer
import streamlit as st
from neo4j_driver import run_query
import json
from graphdatascience import GraphDataScience

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]
    

CYPHER_GENERATION_TEMPLATE = """You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Reply ONLY in Cypher when it makes sense.
5. Whenever you search for an Officer name or an Entity name or an Intermediary name, always do case-insensitive and fuzzy search
6. Officer node is synonymous to Person
7. Entity nodes are synonymous to Shell Companies

Strictly use this Schema for Cypher generation:
{schema}

Question: Is Officer 'Ilham Alyev' is connected to any other Officer named 'Aliyeva'?
Answer: MATCH (a:Officer{{name:'Ilham Aliyev'}})-[:officer_of*1..3]-(b:Officer) WHERE b.name CONTAINS 'Aliyeva' RETURN DISTINCT b.name

Question: Where is "Mehriban Aliyeva" located?
Answer: MATCH (n:Officer{{name:"Mehriban Aliyeva"}})-[:registered_address]->(a:Address) RETURN a.address

Question: which is the most connected Intermediary?
Answer: MATCH (i:Intermediary) RETURN i.name AS intermediary, SIZE([(i)-[]-(e:Entity) | e]) AS entity_connections ORDER BY entity_connections DESC LIMIT 1

Question: What is the address of Mossack Fonseca & Co. Ecuador S.A.?
Answer: MATCH (e:Entity{{name: "Mossack Fonseca & Co. Ecuador S.A."}}) RETURN e.address

Question: Where do most Officers come from?
Answer: MATCH (o:Officer)-[]->(a:Address) WHERE a.countries is not null RETURN a.countries, COUNT(o) ORDER BY COUNT(o) DESC LIMIT 1

Question: Name top 5 countries has the most number of Entities
Answer: MATCH (e:Entity)-->(a:Address) WHERE a.countries is not null WITH a.countries AS country, count(DISTINCT e) AS numEntities RETURN country, numEntities ORDER BY numEntities DESC LIMIT 5

Question: Name two similar officers located in UAE?
Answer: MATCH (a:Officer)-[:officer_of]->(:Entity)-[:registered_address]->(:Address{{countries:"United Arab Emirates"}})<-[:registered_address]-(:Entity)<-[:officer_of]-(b:Officer) WHERE (a)-[:similar]-(b) RETURN DISTINCT a.name, b.name LIMIT 2

Question: Fetch all the Officers associated with another Officer named 'GORYUKHIN'
Answer: MATCH (o:Officer)-[:officer_of*1..3]-(b:Officer) WHERE o.name CONTAINS 'GORYUKHIN' RETURN DISTINCT b.name

Question: What are all the companies that Neelie Kroes has direct links to?
Answer: MATCH (o:Officer{{name:"Neelie Kroes"}})-[:officer_of]->(c:Entity) RETURN DISTINCT c.name

Question: Which leaks was 'MINT HOLDINGS LTD.' associated?
Answer: MATCH (e:Entity) WHERE e.name =~ 'MINT HOLDINGS LTD.' RETURN e.sourceID

Question: what is the shortest path between 'Ilham Aliyev' & 'Mehriban Aliyeva'?
Answer: MATCH (a:Officer),(b:Officer)
        WHERE a.name CONTAINS 'Ilham Aliyev' 
          AND b.name CONTAINS 'Mehriban Aliyeva'
        MATCH p=allShortestPaths((a)-[:officer_of|intermediary_of|registered_address*..10]-(b))
        return distinct reduce(s=head(nodes(p)).name, n in tail(nodes(p)) | s+"->"+n.name) as path
        LIMIT 50

Question: What is the relationship between 'Ilham Aliyev' & 'Mehriban Aliyeva'?
Answer: MATCH (a:Officer),(b:Officer)
        WHERE a.name CONTAINS 'Ilham Aliyev' 
          AND b.name CONTAINS 'Mehriban Aliyeva'
        MATCH p=allShortestPaths((a)-[:officer_of|intermediary_of|registered_address*..10]-(b))
        return distinct reduce(s=head(nodes(p)).name, n in tail(nodes(p)) | s+"->"+n.name) as path
        LIMIT 50

Question: what are the Entities that are named "Mossack Fonseca"
Answer: MATCH (e:Entity) WHERE e.name CONTAINS "Mossack Fonseca" RETURN e.name

Question: Name 5 companies from Taiwan that have high degree centrality.
Answer: MATCH (e:Entity)-[:registered_address]->(a:Address{{countries:"Taiwan"}}) WITH e, COUNT(*) AS degree_centrality RETURN e.name, degree_centrality ORDER BY degree_centrality DESC LIMIT 5

Question: How many Shell companies are owned by Taiwanese?
Answer: MATCH (o:Officer)-[:officer_of]->(e:Entity), (o)-[:registered_address]->(a:Address{{countries:"Taiwan"}}) RETURN COUNT(DISTINCT e)

Question: {question}
Answer:"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema","question"], template=CYPHER_GENERATION_TEMPLATE
)

@retry(tries=5, delay=5)
def get_results(messages):
    start = timer()
    try:
        graph = Neo4jGraph(
            url=host, 
            username=user, 
            password=password
        )
        llm = AzureChatOpenAI(
            openai_api_version=st.secrets["AZURE_OPENAI_API_VERSION"],
            azure_deployment=st.secrets["AZURE_OPENAI_MLM_NAME"],
            temperature=0,
        )
        chain = GraphCypherQAChain.from_llm(
            llm, 
            graph=graph, verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            return_direct=True
        )
        if messages:
            question = messages.pop()
        else: 
            question = 'Who is Ilham Aliyev?'
        r = chain(question)
        result = llm.invoke(f"""Fact: {r['result']}

            * Summarise the above fact as if you are answering this question "{r['query']}"
            * When the fact is not empty, assume the question is valid and the answer is true
            * Do not return helpful or extra text or apologies
            * Just return summary to the user. DO NOT start with Here is a summary
            * List the results in rich text format if there are more than one results
            * If the facts are empty, just respond None
            Assistant:
            """)
        r['context'] = r['result']
        r['result'] = result.content
        return r
    # except Exception as ex:
    #     print(ex)
    #     return "LLM Quota Exceeded. Please try again"
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


