FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
WORKDIR /app
ADD requirements.txt /app
ADD creds /creds
# COPY . /app
# add files to Docker environment
ADD app/main.py /app
ADD app/API_data_models.py /app

# config directory
ADD app/config /app/config

# elastic_helpers directory
ADD app/elastic_helpers /app/elastic_helpers

# helpers directory
ADD app/helpers /app/helpers

# preform_requests directory
ADD app/preform_requests /app/preform_requests

# add html & css for support page
ADD app/templates /app/templates
ADD app/static /app/static

# run app
RUN mkdir -p logs
RUN pip install -r requirements.txt
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
