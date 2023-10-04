import streamlit as st
import streamlit.components.v1 as components
import os
from dropbox_sign import \
    ApiClient, ApiException, Configuration, apis, models


st.set_page_config(page_title="ProSign - AI Powered Contract Review & Signing", page_icon="📝", layout="wide",
                   initial_sidebar_state="auto", menu_items=None)

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

st.markdown(page_bg_img, unsafe_allow_html=True)

# initialize to avoid errors
if 'file_name' not in st.session_state.keys():
    st.session_state['file_name'] = None

st.title("ProSign - AI Powered Contract Review & Signing 📝")

if st.session_state['file_name'] is not None:
    st.header('Review and Sign {}'.format(st.session_state['file_name']))
    contract_name = st.session_state['file_name'].split('.')[0]

    with st.sidebar:
        name = st.text_input('Your Full Name')
        email = st.text_input('Your Email Address')
        click = st.button('Review and Sign')

    if click and name and email:
        configuration = Configuration(
            # Configure HTTP basic authorization: api_key
            username=st.secrets["dropbox_credentials"]["username"])

        with ApiClient(configuration) as api_client:
            signature_request_api = apis.SignatureRequestApi(api_client)

            signer_1 = models.SubSignatureRequestSigner(
                email_address=email,
                name=name,
                order=0,
            )

            signing_options = models.SubSigningOptions(
                draw=True,
                type=True,
                upload=True,
                phone=True,
                default_type="draw",
            )

            data = models.SignatureRequestCreateEmbeddedRequest(
                client_id=st.secrets["dropbox_credentials"]["client_id"],
                title=contract_name,
                signers=[signer_1],
                files=[st.session_state['uploaded_file']],
                signing_options=signing_options,
                test_mode=True,
            )

            try:
                response = signature_request_api.signature_request_create_embedded(data)
                signature_id = response['signature_request']['signatures'][0]['signature_id']
                embedded_api = apis.EmbeddedApi(api_client)

                signature_id = signature_id
                response = embedded_api.embedded_sign_url(signature_id)

                sign_url = response['embedded']['sign_url']
                url = sign_url + st.secrets["dropbox_credentials"]["embedded_url"]

                # display the sign url
                components.iframe(url, width=1500, height=1000, scrolling=True)

            except ApiException as e:
                st.error("Exception when calling Dropbox Sign API: %s\n" % e)


footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #283750
;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
    </style>
        Made for Dropbox Sign AI Hackathon 2023. Powered by LlamaIndex 🦙
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
