
FROM python:3.7.6

ENV SRC_DIR /Users/alinahazirah/Desktop/mercari_projects/mercari-build-training-2022/python
WORKDIR ${SRC_DIR}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt ${SRC_DIR}/
#COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt

COPY python/* ${SRC_DIR}/

CMD ["python3","-m","uvicorn", "main:app", "--reload", "--host", "0.0.0.0","--port", "9000"]
