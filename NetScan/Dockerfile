# Multi-stage build for production optimization
FROM python:3.9-slim as builder

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash netscan

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/netscan/.local

# Copy application code
COPY . .

# Change ownership to netscan user
RUN chown -R netscan:netscan /app

# Switch to non-root user
USER netscan

# Make sure scripts in .local are usable:
ENV PATH=/home/netscan/.local/bin:$PATH

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
