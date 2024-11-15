import random
import re
import json
import os
import asyncio
import huggingface_hub
from huggingface_hub import InferenceClient

val_minutes_prompt = """
"i need help to creating meeting minutes.  Using the list of 5 employees in the same organisation provided below, generate 5 coherent and realistic meeting minutes of varying complexity - simple, moderate, detailed. Write them in bullet point forms, with the date formatted as DD-MMM-YYYY. The employees’ responsibilities should align with their role and seniority, and the duration of meetings should align with the complexity of the meetings. The minutes should include:
Date and Time: When the meeting took place, start and end time of meeting.
Attendees: Who was present, who took notes, and absentees.
Agenda: A list of topics that were planned for discussion, such as project updates, strategy discussions, or problem-solving sessions can take in more agenda if any.
Discussion Points: Summaries of key discussions, decisions made, and any actions assigned. Consider including potential outcomes or challenges even proposed solutions and how departments can help one another.
Next Steps: Follow-up actions, responsibilities, and deadlines with specific dates 

Sort the minutes from earliest to latest.


Here is the list of internal people:
{names}


The purpose and scenario of the meeting should include but not be limited to:

Purpose: {purpose}

Scenario: {scenario}

 In some of the minutes, optionally:
 1. involve other non-attendee colleagues and teams in the organisation. 
 2. include external entities such as: {external_organizations}
When there are additional attendees, include their names, organisations, and roles.
Afterwards, generate the correct people and relationships present in the synthetic minutes data in the JSON format below. Include these relationship types (grouped together): employee-organisation, employee-role, employee-product/service, employee-location. Do not repeat, these will be used as the ground truth for further LLM inference.

JSON Example: 
{{  
  "data": {{  
    "entities": {{  
      "persons": [  
        {{  
          "name": "John Doe"  
        }}  
      ],  
      "organizations": [  
        {{  
          "name": "Acme Corp"  
        }}  
      ],  
      "roles": [  
        {{  
          "title": "CEO"  
        }}  
      ],  
      "locations": [  
        {{  
          "name": "New York"  
        }}  
      ],  
      "products_services": [  
        {{  
          "name": "Widget X"  
        }}  
      ]  
    }},  
    "relationships": [  
      {{  
        "type": "AFFILIATED_WITH",  
        "person": "John Doe",  
        "organization": "Acme Corp"  
      }},  
      {{  
        "type": "HAS_ROLE",  
        "person": "John Doe",  
        "role": "CEO"  
      }},  
      {{  
        "type": "INVOLVED_WITH",  
        "person": "John Doe",  
        "product_service": "Widget X"  
      }},  
      {{  
        "type": "LOCATED_AT",  
        "organization": "Acme Corp",  
        "location": "New York"  
      }}  
    ]  
  }}  
}}  


"""

minutes_prompt = """Generate 5 coherent and realistic meeting minutes of varying complexity - simple, moderate, detailed - using this list of employees :

{names}

The topics and lengths of points of discussion should vary. Ensure that their responsibilities align with their roles and seniorities and that the durations of meetings align with the complexity. Attendees can be in different countries and cities (even if employed by the same company), ensure that the companies exist in those cities and the timezones make sense. Formatting-wise, write the minutes in bullet points, with the dates formatted as DD-MMM-YYYY, and sort the minutes from earliest to latest.
The meeting minutes should include:
 • Date and Time: When the meeting took place, start and end time of meeting.
 • Attendees: Who was present (their roles and departments), who took notes, and absentees.
 • Agenda: A list of topics that were planned for discussion, such as project updates, strategy discussions, or problem-solving sessions.
 • Discussion Points: Summaries of key discussions, decisions made, and any actions assigned. Consider including potential outcomes or challenges.
 • Next Steps: Follow-up actions involving the attendees teams, responsibilities, and deadlines with specific dates - arrange from earliest to latest

 In some of the minutes,
 1. involve other non-attendee colleagues and teams in the organisation. The attendees might need further discussion and approval before proceeding with the next step.
 2. include external entities such as: {external_organizations}
When there are additional attendees, include their names, organisations, and roles.
Afterwards, generate the correct people and relationships present in the synthetic minutes data in the JSON format below. Include these relationship types (grouped together): employee-organisation, employee-role, employee-product/service, employee-location. Do not repeat, these will be used as the ground truth for further LLM inference.

JSON Example: 
{{  
  "data": {{  
    "entities": {{  
      "persons": [  
        {{  
          "name": "John Doe"  
        }}  
      ],  
      "organizations": [  
        {{  
          "name": "Acme Corp"  
        }}  
      ],  
      "roles": [  
        {{  
          "title": "CEO"  
        }}  
      ],  
      "locations": [  
        {{  
          "name": "New York"  
        }}  
      ],  
      "products_services": [  
        {{  
          "name": "Widget X"  
        }}  
      ]  
    }},  
    "relationships": [  
      {{  
        "type": "AFFILIATED_WITH",  
        "person": "John Doe",  
        "organization": "Acme Corp"  
      }},  
      {{  
        "type": "HAS_ROLE",  
        "person": "John Doe",  
        "role": "CEO"  
      }},  
      {{  
        "type": "INVOLVED_WITH",  
        "person": "John Doe",  
        "product_service": "Widget X"  
      }},  
      {{  
        "type": "LOCATED_AT",  
        "organization": "Acme Corp",  
        "location": "New York"  
      }}  
    ]  
  }}  
}}  


"""

email_prompt = """Using the list of 5 people provided below, generate 1 email thread. Threads should involve interactions between the listed people, their respective roles, and various organizations, products, and services. In addition to these 5 people, feel free to include external entities such as clients, partner organizations, or other related services. Occasionally include locations, but make them less frequent. After which, generate a JSON object that extracts out the relevant entities such as person, roles and relationship in the format given below. 

People List: 

{names}

Instructions: 

Structure: 
Create email threads that reflect real-life enterprise communication. Each email thread should consist of 2-5 emails, with varied participants, focusing on interactions related to enterprise-level collaboration, product development, service integration, and strategic partnerships. 

Scenario: {scenario}
Purpose: {purpose}

Relationships: 
Use Person-Role relationships: Highlight how individuals discuss responsibilities related to their roles (e.g., product development, managing teams). 
Use Person-Product/Service relationships: Include discussions about working on, providing, or using products and services. Occasionally, introduce external organizations, such as partners, clients, or suppliers, into the conversations. Include Person-Person interactions that reflect typical enterprise dynamics, such as updates, requests, or follow-ups. 


Entities: The following entities should be represented across the emails: 
Persons: Refer to the employees in the list, and, OPTIONALLY, external stakeholders organizations if the scenario and purpose of the meeting makes sense to include them. Such as: 

{external_organizations}

Products/Services: Include references to products and services occasionally, such as software tools, cloud platforms, or AI solutions.
Locations (optional): Include locations only occasionally, and only when relevant to a specific context (e.g., a mention of a regional office or a meeting location). 

JSON Example: 
{{  
  "data": {{  
    "entities": {{  
      "persons": [  
        {{  
          "name": "John Doe"  
        }}  
      ],  
      "organizations": [  
        {{  
          "name": "Acme Corp"  
        }}  
      ],  
      "roles": [  
        {{  
          "title": "CEO"  
        }}  
      ],  
      "locations": [  
        {{  
          "name": "New York"  
        }}  
      ],  
      "products_services": [  
        {{  
          "name": "Widget X"  
        }}  
      ]  
    }},  
    "relationships": [  
      {{  
        "type": "AFFILIATED_WITH",  
        "person": "John Doe",  
        "organization": "Acme Corp"  
      }},  
      {{  
        "type": "HAS_ROLE",  
        "person": "John Doe",  
        "role": "CEO"  
      }},  
      {{  
        "type": "INVOLVED_WITH",  
        "person": "John Doe",  
        "product_service": "Widget X"  
      }},  
      {{  
        "type": "LOCATED_AT",  
        "organization": "Acme Corp",  
        "location": "New York"  
      }}  
    ]  
  }}  
}}  


"""

ibm_employees = [
    "Alice Smith - Chief Data Officer at R&D Department at IBM - oversees the development of Microsoft Azure and Symantec Endpoint Security.",
    "Brian Taylor - Senior Data Scientist at R&D Department at IBM - works on Microsoft Azure in the R&D Department.",
    "Carol Nguyen - Junior Data Scientist in the R&D Department at IBM - assists in analyzing data for Microsoft Azure.",
    "David Patel - Cloud Architect in the IT Department at IBM - architects infrastructure for Amazon Web Services (AWS).",
    "Emma Lee - Product Manager in the IT Department at IBM - manages the product strategy for Google Cloud AI Platform.",
    "Franklin Moore - Senior Software Engineer in the AI Department at IBM - develops APIs for IBM Watson Assistant.",
    "Gina Lopez - UX Designer in the Product Development Department at IBM - designs user interfaces for IBM Cloud Pak for Data.",
    "Henry Zhou - DevOps Engineer in the Operations Department at IBM - automates CI/CD pipelines for IBM Kubernetes Service.",
    "Ivy Bennett - Data Engineer in the Data Management Department at IBM - builds ETL pipelines for IBM Db2 Database.",
    "Jackie Lin - Cybersecurity Analyst in the Security Department at IBM - focuses on threat detection for IBM Security Guardium.",
    "Kevin O'Reilly - Machine Learning Engineer in the AI Research Department at IBM - develops models for IBM Watson Studio.",
    "Lily Garcia - Marketing Analyst in the Business Strategy Department at IBM - analyzes customer trends for IBM Cloud Satellite.",
    "Michael Turner - Cloud Security Architect in the Cybersecurity Department at IBM - designs security protocols for Microsoft Azure.",
    "Natalie Wu - Product Marketing Manager in the Marketing Department at IBM - promotes IBM Watson Discovery to enterprise clients.",
    "Oliver James - AI Research Scientist in the Research & Development Department at IBM - works on natural language processing for IBM Watson Language Translator.",
    "Paul Hernandez - Systems Engineer in the IT Support Department at IBM - maintains IBM Z systems infrastructure.",
    "Quinn Parker - Data Analyst in the Data Science Department at IBM - provides analytics insights for IBM Cognos Analytics.",
    "Rachel Singh - Software Engineer in the Cloud Solutions Department at IBM - works on backend development for IBM Cloud Functions.",
    "Samuel Davis - Blockchain Developer in the Innovation Department at IBM - works on Hyperledger Fabric for IBM Blockchain Platform.",
    "Tina Foster - IT Support Specialist in the Technical Services Department at IBM - supports IBM QRadar SIEM implementation for clients.",
    "Uma Patel - Senior Solutions Architect in the Solutions Engineering Department at IBM - architects hybrid cloud solutions for IBM Cloud Private.",
    "Victor Ramos - Robotics Process Automation (RPA) Developer in the Automation Department at IBM - develops bots using IBM Robotic Process Automation.",
    "Wendy Chen - AI Solutions Architect in the AI Department at IBM - designs AI solutions for IBM Maximo Asset Management.",
    "Xander Williams - Mobile App Developer in the Digital Solutions Department at IBM - develops applications for IBM MobileFirst Platform.",
    "Yasmine Ali - Data Scientist in the Research & Analytics Department at IBM - builds predictive models for IBM Planning Analytics.",
    "Zachary Brooks - Solutions Engineer in the Customer Success Department at IBM - implements solutions for IBM Cloud Pak for Integration.",
    "Abigail Carter - Business Intelligence Analyst in the Data Analytics Department at IBM - focuses on reporting and dashboards for IBM Cognos Analytics.",
    "Benji Martinez - IT Operations Manager in the Infrastructure Department at IBM - oversees infrastructure for IBM Cloud Object Storage.",
    "Clara Diaz - AI Policy Researcher in the Ethics Department at IBM - conducts research on AI ethics for IBM AI OpenScale.",
    "Derek Hill - QA Engineer in the Quality Assurance Department at IBM - tests software for IBM Aspera."
]

ext_organizations = [
    "DigitalOcean - Cloud computing tailored for small and medium-sized businesses and developers",
    "Snowflake - Data warehousing platform specialized in handling complex data sets and analytics",
    "HashiCorp - Infrastructure automation for multi-cloud environments",
    "Cloudera - Enterprise data platform focused on machine learning and AI for big data",
    "Databricks - Data engineering and AI platform leveraging Apache Spark",
    "C3.ai - Enterprise AI platform for industrial-scale AI solutions, particularly in energy and defense",
    "Illumio - Zero-trust segmentation and cybersecurity for enterprise systems",
    "Splunk - Specializes in machine data analysis and monitoring of IT operations and security",
    "Veeva Systems - Cloud solutions for the life sciences industry (pharmaceuticals, biotech)",
    "ServiceTitan - Software for managing and automating the operations of home service external_organizations",
    "Zscaler - Cloud-based security solutions focused on secure internet access for enterprises",
    "Cognex - Machine vision systems used in automation for manufacturing and logistics",
    "Elastic - Search and analytics engine for real-time insights from large datasets",
    "Nutanix - Hybrid and multi-cloud computing infrastructure for enterprise IT environments",
    "Alteryx - Data analytics and automation platform aimed at simplifying complex data processes"
]

scenario_list = ["product development", "team management", "client interactions", 
                 "project updates", "inter-deparment collaboration proposals", 
                 "enterprise-level collaboration",
                 "service integration", "strategic partnerships", "cross-functional collaboration", 
                 "innovation initiatives", "product launches", "market analysis",]

purpose_list = ["formal updates on project status", "informal requests", "collaboration proposals", 
                "team management discussions", "client interactions", "project updates", "simple greetings", 
                "follow-ups", "feedback requests", "meeting scheduling"]



client = InferenceClient(api_key="")

def create_openai_completion(prompt):
    """
    Shortcut function to create a completion using the GPT-4o model
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=4096,
        top_p=0.7,
        stream=False
    )
    return completion.choices[0].message.content
    

def extract_json_from_response(response_text):
    """
    Extracts JSON from response text, handling code blocks and multiline content.
    """
    # First try to find JSON within code blocks
    code_block_pattern = r'```json\s*([\s\S]*?)\s*```'
    code_block_match = re.search(code_block_pattern, response_text)
    
    if code_block_match:
        try:
            json_str = code_block_match.group(1)
            json_object = json.loads(json_str)
            text_without_json = response_text[:code_block_match.start()].strip()
            return text_without_json, json_object
        except json.JSONDecodeError:
            pass
    
    # If no code block or invalid JSON, try general JSON pattern
    json_pattern = r'(?s)\{.*?\}(?=\s*$)'  # (?s) enables dot to match newlines
    json_match = re.search(json_pattern, response_text)
    
    if json_match:
        try:
            json_str = json_match.group(0)
            json_object = json.loads(json_str)
            text_without_json = response_text[:json_match.start()].strip()
            return text_without_json, json_object
        except json.JSONDecodeError:
            pass
    
    return response_text, {}


async def run_queries(prompt, external_organizations, names, n, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Determine the highest index currently present in the output folder
    existing_files = os.listdir(output_folder)
    existing_indices = [int(re.search(r'response_(\d+)', f).group(1)) for f in existing_files if re.search(r'response_(\d+)', f)]
    start_index = max(existing_indices, default=0) + 1

    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent calls
    tasks = []

    async def process_query(i):
        async with semaphore:
            selected_orgs = random.sample(external_organizations, 1)
            selected_names = random.sample(names, 4)
            scenario = random.choice(scenario_list)
            purpose = random.choice(purpose_list)

            modified_prompt = prompt.format(
                external_organizations="\n ".join(selected_orgs),
                names="\n ".join(selected_names),
                scenario=scenario,
                purpose=purpose
            )
            print(modified_prompt)

            response = await create_openai_completion(modified_prompt)
            response_text = response.choices[0].message.content

            # Use the new extraction function
            text_without_json, json_object = extract_json_from_response(response_text)

            file_base_name = f"response_{start_index + i}"
            text_file_path = os.path.join(output_folder, f"{file_base_name}.txt")
            json_file_path = os.path.join(output_folder, f"{file_base_name}.json")

            with open(text_file_path, 'w') as text_file:
                text_file.write(text_without_json)

            with open(json_file_path, 'w') as json_file:
                json.dump(json_object, json_file, indent=1)

    # Add tasks for each query
    for i in range(n):
        tasks.append(process_query(i))

    await asyncio.gather(*tasks)  # Run all tasks concurrently, respecting the semaphore limit

async def main():
    prompt = email_prompt
    external_organizations = ext_organizations
    names = ibm_employees
    n = 15
    output_folder = "email_ground_truth"
    await run_queries(prompt, external_organizations, names, n, output_folder)

if __name__ == "__main__":
    asyncio.run(main())
