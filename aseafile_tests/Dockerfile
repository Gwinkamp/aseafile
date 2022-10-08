from python:3.10

WORKDIR /tests

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "pytest" ]