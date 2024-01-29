# For Linux Image
# docker build -t thraxbot_linux .

FROM python:3.11.4

WORKDIR /app

COPY . .

RUN pip install virtualenv

RUN python setup_script.py

CMD ["python","-u","main.py"]

# For Windows Image
# docker build -t thraxbot_windows .

# FROM python:3

# WORKDIR /app

# COPY . /app

# RUN pip install virtualenv

# RUN python setup_script.py

# CMD ["python","-u","main.py"]