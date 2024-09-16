import agent_tools
import streamlit as st
from PIL import Image
import os

st.title("Amazon Bedrock Agentic Chatbot")  # Title of the application


st.sidebar.markdown(
    "This app shows an Agentic Chatbot powered by Amazon Bedrock to answer questions."
)
clear_button = st.sidebar.button("Clear Conversation", key="clear")
# reset sessions state on clear
if clear_button:
    st.session_state.messages = []
    st.session_state.session_id = agent_tools.generate_random_15digit()


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = agent_tools.generate_random_15digit()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):

        if "traces" in message:
            trace_container = st.container()
            for trace in message["traces"]:
                # Show an expander for each trace type
                with trace_container.expander(trace["trace_type"]):
                    # If trace_type is codeInterpreter use st.code, else use st.markdown
                    if trace["trace_type"] == "codeInterpreter":
                        st.code(trace["text"], language="python")
                    else:
                        st.markdown(trace["text"])

        st.markdown(message["content"][0]["text"])
        if "images" in message:
            for image in message["images"]:
                image_data = Image.open(image)
                st.image(image_data, use_column_width=True)

if prompt := st.chat_input("How can I help??"):
    st.session_state.messages.append({"role": "user", "content": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        trace_container = st.container()

        result = agent_tools.invoke_bedrock_agent(
            prompt, st.session_state.session_id, trace_container
        )

        message_placeholder.markdown(result["text"])

        if "images" in result:
            for image in result["images"]:
                image_data = Image.open(image)
                st.image(image_data, use_column_width=True)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": [{"text": f"{full_response}"}],
            "images": result["images"],
            "traces": result["traces"],
        }
    )
