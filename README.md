# node.py

Hi there! We are node.py, group 4. Our group name is inspired by node.js and our knowledge graph. 

There are two parts to our project:
1. Backend: A REST API built with FastAPI that allows users to process text data, generate ontologies, and manage a knowledge graph using Neo4j.
2. Frontend: A React application that interacts with the backend API to process text data, generate ontologies, and manage a knowledge graph using Neo4j.

## Generation Folder
The generation folder contains the code for generating the data for the NER model. This folder was taken from a previous repository by Subgroup A, therefore the lack of commits from them. 


## Running the Project with Docker Compose

To run the entire project using Docker Compose, follow these steps:

1. Ensure Docker and Docker Compose are installed on your machine.
2. Navigate to the root directory of the project where the `docker-compose.yml` file is located.
3. Run the following command to build and start the services:

   ```bash
   docker-compose up --build
   ```

4. The backend API will be available at `http://localhost:5000`.
5. The frontend application will be available at `http://localhost:3000`.

## Additional Instructions

To run the backend, please refer to the README.md in the backend folder.

To run the frontend, please refer to the README.md in the dsa3101-ui folder.

The wiki is also updated with the latest information of the project.

Thank you for reading this short README.md!
