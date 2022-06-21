
FROM python:3.7.6


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt ./
#COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt

COPY ./python ./

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0","--port", "9000"]
