# Deployment

## Render Web Service

Recommended initial settings:
- Runtime: Python
- Branch: main
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port $PORT`
- Plan: Free for prototype evaluation
- Region: Singapore (low-latency region for Korea)

The Streamlit dashboard is a public-facing web service when deployed. Do not upload personal, confidential, or customer production data to the prototype. Before connecting real operational systems, add authentication, authorization, audit logs, data retention controls, and network restrictions.

Hugging Face base dataset access is public. The Extended NGC dataset may require a separate sign-in/download and can be uploaded as a CSV in Persona Lab. No access token is committed to this repository.
