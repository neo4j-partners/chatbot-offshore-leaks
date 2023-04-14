import os
import openai
import logging, sys
import time
from langchain.llms import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import streamlit as st
from streamlit_chat import message

from driver import read_query
from train_cypher import template, schema, instr_template, examples

st.title("Offshore Leaks Chatbot - Powered by Neo4j & GenAI")
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

cypher_prefix = ["ALTER","CALL","CREATE","DEALLOCATE","DELETE","DENY","DETACH","DROP","DRYRUN","ENABLE","FOREACH","GRANT","LOAD","MATCH","MERGE","OPTIONAL","REALLOCATE","REMOVE","RENAME","RETURN","REVOKE","SET","SHOW","START","STOP","TERMINATE","UNWIND","USE","USING","WITH"]


def extract_cypher(s):
    print(s)
    if s.startswith(tuple(cypher_prefix)):
        return s
    else:
        arr = s.split('\n', 1)
        if len(arr) == 1:
            return 'MATCH (e:Nothing) return e.name'
        return extract_cypher(arr[1])
    

def createPrompt():
    sys_tpl="You are an assistant that translates english to Neo4j cypher"
    system_message_prompt = SystemMessagePromptTemplate.from_template(sys_tpl)
    instr_human = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=instr_template,
            input_variables=[]   
        )
    )
    instr_ai = AIMessage(content='Roger that')
    prompt = [system_message_prompt, instr_human, instr_ai]
    prompt = prompt + getExamplePrompts()
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)
    prompt.append(human_message_prompt)
    return ChatPromptTemplate.from_messages(prompt)

def getExamplePrompts():
    eg_prompt = []
    for eg in examples:
        for k, v in eg.items():
            if k == "q": 
                eg_human = HumanMessagePromptTemplate(
                    prompt=PromptTemplate(
                        template=v,
                        input_variables=[] 
                    )
                )
                eg_prompt.append(eg_human)
            else:
                eg_ai = AIMessage(content=v)
                eg_prompt.append(eg_ai)
    return eg_prompt


def generate_response(prompt):
    try:
        chat = AzureChatOpenAI(temperature=0, 
                               openai_api_version="2023-03-15-preview",
                               deployment_name="gpt-35-turbo", 
                               model_name="gpt-35-turbo")
        chat_prompt = createPrompt()
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        cypher_query = chain.run(schema + "\nQuestion: "+ prompt)
        logging.debug(cypher_query)
        message = read_query(extract_cypher(cypher_query))
        logging.debug(message)
        return message, cypher_query
    except:
        return prompt, "LLM Token Limit Exceeded. Please try again"

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


col1, col2 = st.columns([2, 1])


with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    output, cypher_query = generate_response(user_input)
    # store the output
    st.session_state.past.append(user_input)
    st.session_state.generated.append((output, cypher_query))
        

# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        message(st.session_state['past'][-1],
                is_user=True, key=str(-1) + '_user')
        for j, text in enumerate(st.session_state['generated'][-1][0]):
            message(text, key=str(-1) + str(time.time()))

# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['generated']:
        st.text_area("Generated Cypher / Suggestion",
                     st.session_state['generated'][-1][1], height=240)
