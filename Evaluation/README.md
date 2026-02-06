This directory contains all the material produced during the evaluation of the project results.

The `Queries` folder includes all the SPARQL queries used in the project.

**Note**: For some queries, execution times were excessively long due to large join spaces. To address this issue, intermediate results were materialized using SPARQL INSERT queries and stored in **dedicated subgraphs**, which were then used by the main queries.

All SPARQL INSERT queries and the corresponding subgraphs are also included in the folder.
