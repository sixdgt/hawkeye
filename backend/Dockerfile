# Use the official Python image as a base
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies needed for psycopg2 AND netcat-openbsd (for the wait-for-db script)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       netcat-openbsd \
       build-essential \
       python3-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements.txt file
COPY django_requirements.txt /app/
RUN pip install --no-cache-dir -r django_requirements.txt

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy the entire Django project
COPY . /app/

# Expose the port Django will run on
EXPOSE 8001

# Specify the entrypoint script to run first
ENTRYPOINT ["entrypoint.sh"]

# The command to execute after the entrypoint script completes successfully
# This is what "$@" in entrypoint.sh refers to
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
