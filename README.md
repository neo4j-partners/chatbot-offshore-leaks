# neo4j-generative-ai-demo
This is a web application which shows how GenAI can be used with Neo4j. We will explore how to leverage generative AI to consume a knowledge graph in Neo4j.

The dataset we're using is from the ICIJ Offhsore Leaks.  It can be downloaded and dumped to a Neo4j DB from [here](https://drive.google.com/file/d/1Q5RiD163ke_gQM837uvFPPHG8A034a4i/view?usp=sharing).

The dataflow in this demo consists of:
- RAG using Natural Language to Cypher - A user inputs natural language into a chat UI.  Azure OpenAI LLM converts that to Neo4j Cypher which is run against the database.  This flow allows non technical users to query the database.

## Setup Azure OpenAI Environment
To get started setting up the demo, follow the instructions [here](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-azure/tree/main/Lab%205%20-%20Parsing%20Data) to setup an Azure OpenAI environemment.

## Deploy Neo4j AuraDS Professional
This demo requires a Neo4j instance.

## UI
The UI application is based on Streamlit. In this example we're going to show how to run it on an Azure VM.  First, deploy a VM. You can use [this guide to spin off an Azure VM](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/quick-create-portal)        

Next, login to the new VM instance using CLI.

We're going to be running the application on port 80.  That requires root access, so first:

    sudo su

Then you'll need to install git and clone this repo:

    yum install -y git
    mkdir -p /app
    cd /app
    git clone https://github.com/neo4j-partners/chatbot-offshore-leaks.git
    cd chatbot-offshore-leaks

Let's install python & pip first:

    yum install -y python
    yum install -y pip

Now, let's create a Virtual Environment to isolate our Python environment and activate it

    yum install -y virtualenv
    python3 -m venv /app/venv/genai-demo
    source /app/venv/genai-demo/bin/activate

To install Streamlit and other dependencies:

    cd ui
    pip install -r requirements.txt

Check if `streamlit` command is accessible from PATH by running this command:

    streamlit --version

If not, you need to add the `streamlit` binary to PATH variable like below:

    export PATH="/app/venv/genai-demo/bin:$PATH"

Next up you'll need to create a secrets file for the app to use.  Open the file and edit it:

    cd streamlit
    cd .streamlit
    cp secrets.toml.example secrets.toml
    vi secrets.toml

You will now need to edit that file to reflect your credentials. The file has the following variables:

    AZURE_OPENAI_API_KEY = "" 
    AZURE_OPENAI_ENDPOINT = ""
    AZURE_OPENAI_API_VERSION = ""
    AZURE_OPENAI_MLM_NAME = ""
    NEO4J_HOST = "" #NEO4J_AURA_DS_URL
    NEO4J_PORT = "7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "" #Neo4j password
    NEO4J_DB = "neo4j"

Now we can run the app with the commands:

    cd ..
    streamlit run Home.py --server.port=80

Optionally, you can run the app in another screen session to ensure the app continues to run even if you disconnect from the VM instance:

    screen -S run_app
    cd ..
    streamlit run Home.py --server.port=80    

You can use `Ctrl+a` `d` to exit the screen with the app still running and enter back into the screen with `screen -r`. To kill the screen session, use the command `screen -XS run_app quit`.

On the VM to run on port 80:
- Ensure you are a root or has access to run on port 80
- Ensure that the VM has port 80 open for HTTP access. You might need to open that port or any other via firewall rules. 

Once deployed, you will be able to see the Dashboard and Chat UI.

From the Chat UI, you can ask questions like:
1. Who is Ilham Aliyev?
2. Is Officer 'Ilham Alyev' is connected to any other Officer named like 'Aliyeva'?
3. Where is "Ilham Aliyev" located?
4. Where is "Mehriban Aliyeva" located?
5. what is the shortest path between 'Ilham Aliyev' & 'Mehriban Aliyeva'?
6. what is the distinct shortest path between 'Ilham Aliyev' & 'Arzu Aliyeva'?
7. which is the most connected Intermediary?
8. Which countries has the most number of Entities?
9. Name two similar officers located in UAE?

