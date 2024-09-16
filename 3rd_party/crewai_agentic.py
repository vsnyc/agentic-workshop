import sys
from textwrap import dedent
import streamlit as st
from PIL.ImageOps import expand
from dotenv import load_dotenv
import secrets
import time
import random
import re
load_dotenv()

from crewai import Agent, Crew, Task
from langchain_aws import ChatBedrock

# Load Claude from Amazon Bedrock
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs=dict(temperature=0.7),
    region_name="us-west-2",
)

def streamlit_callback(step_output):
    # This function will be called after each step of the agent's execution
    st.markdown("---")
    for step in step_output:
        # st.markdown(step)
        if isinstance(step, tuple) and len(step) == 2:
            action, observation = step
            if isinstance(action, dict) and "tool" in action and "tool_input" in action and "log" in action:
                st.markdown(f"# Action")
                st.markdown(f"**Tool:** {action['tool']}")
                st.markdown(f"**Tool Input** {action['tool_input']}")
                st.markdown(f"**Log:** {action['log']}")
                st.markdown(f"**Action:** {action['Action']}")
                st.markdown(
                    f"**Action Input:** ```json\n{action['tool_input']}\n```")
            elif isinstance(action, str):
                st.markdown(f"**Action:** {action}")
            else:
                st.markdown(f"**Action:** {str(action)}")

            st.markdown(f"**Observation**")
            if isinstance(observation, str):
                observation_lines = observation.split('\n')
                for line in observation_lines:
                    if line.startswith('Title: '):
                        st.markdown(f"**Title:** {line[7:]}")
                    elif line.startswith('Link: '):
                        st.markdown(f"**Link:** {line[6:]}")
                    elif line.startswith('Snippet: '):
                        st.markdown(f"**Snippet:** {line[9:]}")
                    elif line.startswith('-'):
                        st.markdown(line)
                    else:
                        st.markdown(line)
            else:
                st.markdown(str(observation))
        else:
            st.markdown(step)

class TravelListicleAgents:
    def travel_researcher_agent(self):
        return Agent(
            role="Travel Researcher",
            goal="Research and compile interesting activities and attractions for a given location",
            backstory=dedent(
                """You are an experienced travel researcher with a knack for 
                discovering both popular attractions and hidden gems in any 
                location. Your expertise lies in gathering comprehensive 
                information about various activities, their historical 
                significance, and practical details for visitors."""
            ),
            allow_delegation=False,
            verbose=True,
            llm=llm,
            step_callback=streamlit_callback
        )

    def content_writer_agent(self):
        return Agent(
            role="Travel Content Writer",
            goal="Create engaging and informative content for the top 10 listicle",
            backstory=dedent(
                """You are a skilled travel writer with a flair for creating 
                captivating content. Your writing style is engaging, 
                informative, and tailored to inspire readers to explore new 
                destinations. You excel at crafting concise yet compelling 
                descriptions of attractions and activities."""
            ),
            allow_delegation=False,
            verbose=True,
            llm=llm,
            step_callback=streamlit_callback
        )

    def editor_agent(self):
        return Agent(
            role="Content Editor",
            goal="Ensure the listicle is well-structured, engaging, and error-free",
            backstory=dedent(
                """You are a meticulous editor with years of experience in 
                travel content. Your keen eye for detail helps polish articles 
                to perfection. You focus on improving flow, maintaining 
                consistency, and enhancing the overall readability of the 
                content while ensuring it appeals to the target audience."""
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,
            step_callback=streamlit_callback
        )

#display the console processing on streamlit UI
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Market Research Analyst" in cleaned_data:
            # Apply different color
            cleaned_data = cleaned_data.replace("Market Research Analyst", f":{self.colors[self.color_index]}[Market Research Analyst]")
        if "Business Development Consultant" in cleaned_data:
            cleaned_data = cleaned_data.replace("Business Development Consultant", f":{self.colors[self.color_index]}[Business Development Consultant]")
        if "Technology Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("Technology Expert", f":{self.colors[self.color_index]}[Technology Expert]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

class TravelListicleTasks:
    def research_task(self, agent, location):
        return Task(
            description=dedent(
                f"""Research and compile a list of at least 15 interesting 
                activities and attractions in {location}. Include a mix of 
                popular tourist spots and lesser-known local favorites. For 
                each item, provide:
                1. Name of the attraction/activity
                2. Brief description (2-3 sentences)
                3. Why it's worth visiting
                4. Any practical information (e.g., best time to visit, cost)

                Your final answer should be a structured list of these items.
                """
            ),
            agent=agent,
            expected_output="Structured list of 15+ attractions/activities",
        )

    def write_listicle_task(self, agent, location):
        return Task(
            description=dedent(
                f"""Create an engaging top 10 listicle article about things to 
                do in {location}. Use the research provided to:
                1. Write a catchy title and introduction (100-150 words)
                2. Select and write about the top 10 activities/attractions
                3. For each item, write 2-3 paragraphs (100-150 words total)
                4. Include a brief conclusion (50-75 words)

                Ensure the content is engaging, informative, and inspiring. 
                Your final answer should be the complete listicle article.
                """
            ),
            agent=agent,
            expected_output="Complete top 10 listicle article",
        )

    def edit_listicle_task(self, agent, location):
        return Task(
            description=dedent(
                f"""Review and edit the top 10 listicle article about things to 
                do in {location}. Focus on:
                1. Improving the overall structure and flow
                2. Enhancing the engagement factor of the content
                3. Ensuring consistency in tone and style
                4. Correcting any grammatical or spelling errors
                5. Optimizing for SEO (if possible, suggest relevant keywords)

                Your final answer should be the polished, publication-ready 
                version of the article.
                """
            ),
            agent=agent,
            expected_output="Edited and polished listicle article",
        )


def run_crewai_app(location):
    tasks = TravelListicleTasks()
    agents = TravelListicleAgents()

    #print("## Welcome to the Travel Listicle Crew")
    #print("--------------------------------------")
    #location = input("What location would you like to create a top 10 listicle for?\n")

    # Create Agents
    travel_researcher = agents.travel_researcher_agent()
    content_writer = agents.content_writer_agent()
    editor = agents.editor_agent()

    # Create Tasks
    research_location = tasks.research_task(travel_researcher, location)
    write_listicle = tasks.write_listicle_task(content_writer, location)
    edit_listicle = tasks.edit_listicle_task(editor, location)

    # Create Crew for Listicle Production
    crew = Crew(
        agents=[travel_researcher, content_writer, editor],
        tasks=[research_location, write_listicle, edit_listicle],
        verbose=True,
    )

    listicle_result = crew.kickoff()

    # Print results
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print(f"Top 10 Things to Do in {location}:")
    print(listicle_result)
    return listicle_result

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

if __name__ == '__main__':
    st.title("Amazon Bedrock Agentic Chatbot")
    st.sidebar.markdown(
        "This app shows an Agentic Chatbot powered by Amazon Bedrock to generate travel listicles."
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown("Type a city in the chat bar to get started.")
    # React to user input
    if prompt := st.chat_input("What location would you like to create a top 10 listicle for?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.status("Agents at work...", state="running", expanded=True) as status:
            with st.container(height=500, border=False):
                sys.stdout = StreamToExpander(st)
                # response = run_crewai_app(location=prompt)
                response = "Dummy"
            status.update(label="Trip plan Ready!", state="complete", expanded=False)
            # Display assistant response in chat message container

        with st.chat_message("assistant"):
            st.subheader("Here is your Travel Listicle", anchor=False, divider="rainbow")
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
