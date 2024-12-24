FROM python:3.12.4
WORKDIR /app


# Install system dependencies including FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Create and activate a virtual environment
RUN python -m venv myenv
RUN . myenv/bin/activate

# Install dependencies within the virtual environment
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Set the command to run your application
CMD python3 main.py
