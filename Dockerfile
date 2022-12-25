# Pull ubuntu python image
FROM python:3.10.7

# Current work directory
WORKDIR /app

# Copy project file to /app/
COPY . /app/

# Install requirements
RUN pip install -r requirements.txt

# Expose backend & frontend ports
EXPOSE 8000 3000

# Install npm
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y npm

# Run the startup script
CMD ["sh", "start.sh"]
