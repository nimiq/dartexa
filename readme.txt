- create a virtual environment
- install requirements:
pip install -r requirements.txt
- run the backend:
./manage.py runserver

To get a public HTTPS url, register at https://ngrok.com/ and install ngrock.
Then login with ngrock and start it:
ngrok authtoken [yourkey]
ngrok http -subdomain=kpnexa 8000
