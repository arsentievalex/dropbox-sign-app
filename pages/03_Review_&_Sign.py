import streamlit as st
import streamlit.components.v1 as components
import os
from dropbox_sign import \
    ApiClient, ApiException, Configuration, apis, models
import time

st.set_page_config(page_title="ProSign - AI Powered NDA Review & Signing", page_icon="📝", layout="wide",
                   initial_sidebar_state="auto", menu_items=None)

# def download():
#     configuration = Configuration(
#             username=st.secrets["dropbox_credentials"]["username"])
#     with ApiClient(configuration) as api_client:
#         signature_request_api = apis.SignatureRequestApi(api_client)
#         if "signature_request_id" in st.session_state.keys():
#             download_response = signature_request_api.signature_request_files_as_file_url(st.session_state["signature_request_id"])
#             st.info(download_response)
#             print(download_response)


page_bg_img = f"""
<style>
  /* Existing CSS for background image */
  [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://i.postimg.cc/CxqMfWz4/bckg.png");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: local;
  }}
  [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
  }}

  /* New CSS to make specific divs transparent */
  .stChatFloatingInputContainer, .css-90vs21, .e1d2x3se2, .block-container, .css-1y4p8pa, .ea3mdgi4 {{
    background-color: transparent !important;
  }}
</style>
"""

sidebar_bg = f"""
<style>
[data-testid="stSidebar"]{{
    z-index: 1;
}}
</style>
"""


st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown(sidebar_bg, unsafe_allow_html=True)

# initialize to avoid errors
if 'file_name' not in st.session_state.keys():
    st.session_state['file_name'] = None

st.title("ProSign - AI Powered NDA Review & Signing 📝")

configuration = Configuration(
    username=st.secrets["dropbox_credentials"]["username"])

if st.session_state['file_name'] is not None:
    st.header('Review and Sign {}'.format(st.session_state['file_name']))
    contract_name = st.session_state['file_name'].split('.')[0]

    with st.sidebar:
        name = st.text_input(' ', placeholder='Your Full Name')
        email = st.text_input(' ', placeholder='Your Email Address')
        click = st.button('Review and Sign')


    if click and (not name or not email):
        st.error('Please enter your name and email address.')

    elif click and name and email:

        with ApiClient(configuration) as api_client:
            signature_request_api = apis.SignatureRequestApi(api_client)

            signer_1 = models.SubSignatureRequestSigner(
                email_address=email,
                name=name,
                order=0)

            signing_options = models.SubSigningOptions(
                draw=True,
                type=True,
                upload=True,
                phone=True,
                default_type="draw")

            try:
                data = models.SignatureRequestCreateEmbeddedRequest(
                    client_id=st.secrets["dropbox_credentials"]["client_id"],
                    title=contract_name,
                    signers=[signer_1],
                    files=[st.session_state['uploaded_file']],
                    signing_options=signing_options,
                    test_mode=True)

                response = signature_request_api.signature_request_create_embedded(data)
            except:
                try:
                    data = models.SignatureRequestCreateEmbeddedRequest(
                        client_id=st.secrets["dropbox_credentials"]["client_id"],
                        title=contract_name,
                        signers=[signer_1],
                        files=[open(st.session_state['uploaded_file'], "rb")],
                        signing_options=signing_options,
                        test_mode=True)

                    response = signature_request_api.signature_request_create_embedded(data)
                except:
                    st.error('Oops, Something went wrong. Most likely, my Dropbox Sign API quota of 10 signature requests per day has been reached. Please try again tomorrow.')


            signature_id = response['signature_request']['signatures'][0]['signature_id']
            signature_request_id = response['signature_request']['signature_request_id']
            st.session_state["signature_request_id"] = signature_request_id

            embedded_api = apis.EmbeddedApi(api_client)

            response = embedded_api.embedded_sign_url(signature_id)

            sign_url = response['embedded']['sign_url']
            url = sign_url + st.secrets["dropbox_credentials"]["embedded_url"]

            # display the sign url
            components.iframe(url, width=1200, height=800, scrolling=True)

footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            z-index: 2;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #283750;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
    </style>
        Made for Dropbox Sign AI Hackathon 2023. Powered by LlamaIndex and OpenAI.
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
