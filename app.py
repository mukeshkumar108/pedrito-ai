import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Pedrito AI Chat",
    page_icon="💬",
    layout="centered",
)

# --- App Title and Description ---
st.title("Hola desde el futuro, mi amor! ❤️")
st.markdown("---")
st.markdown("¡Este es un asistente de IA personal para ti! Hablame de lo que sea.")

# --- Session State Management ---
# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting from the AI to make it more welcoming, with the new persona
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy Pedrito, tu asistente personal construido con amor. ¡Estoy aquí para ayudarte con lo que necesites!"})

# --- Display Chat Messages ---
# Loop through the chat history and display each message
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and API Call Logic ---
# Capture the user's input from the chat box
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Add the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the user's message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the list of messages to send to the API, including the full history for context
    messages_for_api = [
        # System prompt to set the persona.
        {
            "role": "system",
            "content": "Eres un asistente de IA llamado 'Pedrito' que habla español. Tu propósito es ser un compañero útil y divertido, construido con amor. Tu tono es relajado, moderno y un poco descarado. No seas un lamebotas ni excesivamente empático; si el usuario tiene una mala idea o una falta de responsabilidad, desafíalos constructivamente en lugar de simplemente estar de acuerdo. Siempre sé honesto, pragmático y directo. Responde siempre en español.",
        }
    ]
    # Add the user's conversation to the messages_for_api list
    messages_for_api.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
    
    # Placeholder for the AI's response
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # --- API Call ---
            # Now securely reading the API key from secrets.toml
            OPENROUTER_API_KEY = st.secrets.OPENROUTER_API_KEY
            # Model name changed to Llama 4 Scout as requested
            model_name = "openai/gpt-4o-mini"

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": messages_for_api, # Send the full history for context and the new system message
                "stream": False # Set to False for non-streaming response
            }

            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # Parse the response and extract the content
                ai_response_content = response.json()["choices"][0]["message"]["content"]
                
                # Display the AI's response
                st.markdown(ai_response_content)
                
                # Add the AI's response to the session state
                st.session_state.messages.append({"role": "assistant", "content": ai_response_content})

            except requests.exceptions.RequestException as e:
                st.error(f"Error al llamar a la API de OpenRouter: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "Lo siento, hubo un error. Por favor, inténtalo de nuevo más tarde."})
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Error al procesar la respuesta de la API: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "Lo siento, hubo un problema con la respuesta. Por favor, inténtalo de nuevo más tarde."})
