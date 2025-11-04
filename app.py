import streamlit_authenticator as stauth
hashes = stauth.Hasher(['pass', 'admin123']).generate()
print(hashes)
