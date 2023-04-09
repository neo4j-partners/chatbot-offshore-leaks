# Offshore-leaks-chatbot

## Pre-requisites
- A running Neo4j V5 instance with Offshore Leaks Data. Dump [here](https://drive.google.com/file/d/1Q5RiD163ke_gQM837uvFPPHG8A034a4i/view?usp=sharing).

Run the following commands to start the services:


1. Create an `.env` file and input your OPENAI API KEY as shown in `env.example`

2. Start docker services

```
docker-compose up
```

## Sample Questions to ask:
1. Who is Ilham Aliyev?
2. Is Officer 'Ilham Alyev' is connected to any other Officer named like 'Aliyeva'?
3. Where is "Ilham Aliyev" located?
4. Where is "Mehriban Aliyeva" located?
5. what is the shortest path between 'Ilham Aliyev' & 'Mehriban Aliyeva'?
6. what is the distinct shortest path between 'Ilham Aliyev' & 'Arzu Aliyeva'?
7. which is the most connected Intermediary?
8. Which countries has the most number of Entities?
9. Name two similar officers located in UAE?

# Credits
Thanks [Tomaz Bratanic](https://github.com/tomasonjo/NeoGPT-Explorer)
