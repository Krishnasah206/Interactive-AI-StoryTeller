# Import necessary libraries
import streamlit as st
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import openai
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set device for computation (use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the BLIP model and processor for image captioning
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# Function to generate a caption from an image using BLIP
def generate_caption(image):
    inputs = blip_processor(image, return_tensors="pt").to(device)
    output = blip_model.generate(**inputs)
    caption = blip_processor.decode(output[0], skip_special_tokens=True)
    return caption

# Function to create a cohesive story from a series of captions
def create_cohesive_story(captions):
    prompt = "Develop a continuous story using these image captions:\n\n"
    prompt += "\n".join([f"Image {idx + 1}: {caption}" for idx, caption in enumerate(captions)])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    story = response.choices[0].message['content'].strip()
    return story

# Login validation function
def validate_login(username, password):
    valid_user = "user"
    valid_password = "pass123"
    return username == valid_user and password == valid_password

# Function to set background image
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: rgb(189,191,207);
                background: linear-gradient(90deg, rgba(189,191,207,1) 42%, rgba(213,214,219,1) 100%, rgba(46,47,45,1) 100%);
            }}
            .stHeading {{
                color: #000000;
            }}

            .st-emotion-cache-ysk9xe {{
                color: #000000;
            }}

            .st-ae {{
                background-color: rgba(255, 255, 255, 0) !important; /* Transparent background */
                color: #ffffff; /* Text color */
            }}
            /* Make the header (navigation bar) transparent */
            .stAppHeader {{
                background-color: rgba(255, 255, 255, 0) !important; /* Transparent background */
                color: #000000; /* Text color */
            }}

            /* Transparent navigation bar styling */
            .css-18ni7ap {{
                background-color: rgba(255, 255, 255, 0); /* Transparent background */
            }}
            stElementContainer {{
                background-color: rgba(255, 255, 255, 0) !important; /* Transparent background */
                color: #000000; /* Text color */
                border: 1px solid #000000; /* Button border */
            }}
            .stFileUploaderFileName {{
                color: #000000;
            }}
            .st-emotion-cache-1y5f4eg {{
                p {{
                    color: #000000;
                }}
            }}
            /* Custom styling for buttons */
            stButton {{
                background-color: #1a1aff; /* Button background color */
                color:  #ffffff; /* Button text color */
                border: 1px solid #000000; /* Button border */
            }}
            .st-emotion-cache-fis6aj st-emotion-cache-7oyrr6 st-emotion-cache-7oyrr6 st-emotion-cache-td48p3 {{
                color: #000000;

                button {{
                    svg {{
                        color: #000000;
                    }}
                }}
            }}
            /* Button hover effect */
            stButton:hover {{
                background-color: #f0f0f0;
            }}
            /* Styling for login container */
            .container {{
                padding: 20px;
                border-radius: 5px;
                color: #000000;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            }}
            /* Story display container */
            .story-container {{
                margin-top: 20px;
                background-color: #ede2e3;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                color: #333333;
            }}
            input::placeholder {{
                color: white; /* White text for placeholder */
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit Interface
def main():
    # Set the background image
    set_background("images/bg.jpg")

    st.title("Interactive AI StoryTeller")

    # Login Section
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        st.subheader("Login")

        # Add placeholders with white text styling
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Login"):
            if validate_login(username, password):
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    else:
        st.subheader("Upload Images")

        # Upload multiple images
        uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

        if st.button("Generate Story") and uploaded_files:
            captions = []
            images = []

            # Generate captions for each uploaded image
            for uploaded_file in uploaded_files:
                image = Image.open(uploaded_file).convert("RGB")
                caption = generate_caption(image)
                captions.append(caption)
                images.append(image)

            # Display images horizontally without captions
            st.write("Uploaded Images:")
            cols = st.columns(len(images))

            for idx, img in enumerate(images):
                with cols[idx]:
                    st.image(img, use_container_width=True)

            # Generate cohesive story from captions
            if captions:
                st.markdown("<div class='container'><h3>Generating cohesive story...</h3></div>", unsafe_allow_html=True)
                story = create_cohesive_story(captions)
                st.markdown("<div class='story-container'><h3>Generated Story</h3><p>{}</p></div>".format(story), unsafe_allow_html=True)

        if st.button("Logout"):
            st.session_state.clear()  # Clear all session state
            st.markdown('<meta http-equiv="refresh" content="0;url=./">', unsafe_allow_html=True)



if __name__ == "__main__":
    main()