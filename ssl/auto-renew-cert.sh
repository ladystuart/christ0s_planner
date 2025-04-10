#!/bin/bash

# RENAME your-user-folder
SSL_DIR="/home/your-user-folder/server/ssl"
CERT_FILE="$SSL_DIR/fullchain.pem"
KEY_FILE="$SSL_DIR/privkey.pem"
DAYS_THRESHOLD=1  

if [ -f "$CERT_FILE" ]; then
  EXPIRATION_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | sed 's/^.*=//')
  
  EXPIRATION_TIMESTAMP=$(date -d "$EXPIRATION_DATE" +%s)
  CURRENT_TIMESTAMP=$(date +%s)

  DIFF_DAYS=$(( (EXPIRATION_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

  if [ "$DIFF_DAYS" -le "$DAYS_THRESHOLD" ]; then
    echo "Sertificate expires in $DIFF_DAYS generating new..."

# RENAME your-country-code, your-city, YOUR-IP
    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=your-country-code/ST=your-city/L=your-city/O=MyCompany/OU=IT/CN=YOUR-IP"

    echo "Success!"

    sudo systemctl restart nginx
  else
    echo "Days til exp $DIFF_DAYS."
  fi
else
  echo "Cert not found. Generating new..."

# RENAME your-country-code, your-city, YOUR-IP
  openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
  -keyout "$KEY_FILE" \
  -out "$CERT_FILE" \
  -subj "/C=your-country-code/ST=your-city/L=your-city/O=MyCompany/OU=IT/CN=YOUR-IP"

  echo "Success!"

  sudo systemctl restart nginx
fi