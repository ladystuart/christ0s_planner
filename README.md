# Christ0$ Server

This repository contains the server-side application for Christ0$. The server utilizes FastAPI, PostgreSQL, Docker, and Nginx.

> **Public static IP has been used.**  
> **Raspberry Pi 4 has been used as the server.**  
> **All folders in /home/your-user-folder/server.**

## Port Forwarding on Router

To ensure the server is accessible externally, you need to forward the following ports on your router:

- Port 8080: Used for HTTP traffic, accessible via the Nginx proxy.
- Port 8443: Used for HTTPS traffic (SSL/TLS), providing secure communication.
- Port 8000: Used for application health checks or other services (if required).
- Port 22: The SSH port, used for remote access to the server's shell.
- Port 5900: The default VNC port, used for remote desktop access to the server.

### How to Forward Ports on Your Router

1. Log in to your router's administration page (typically http://192.168.1.1 or http://192.168.0.1).
2. Locate the Port Forwarding or NAT (Network Address Translation) section in the settings.
3. Add the following port forwarding rules:

   - Port 8080: Forward to the internal IP address of your server (e.g., 192.168.x.x:8080).
   - Port 8443: Forward to the internal IP address of your server (e.g., 192.168.x.x:8443).
   - Port 8000: Forward to the internal IP address of your server (e.g., 192.168.x.x:8000).
   - Port 22: Forward to the internal IP address of your server (e.g., 192.168.x.x:22).
   - Port 5900: Forward to the internal IP address of your server (e.g., 192.168.x.x:5900).

4. Save the changes and restart your router if necessary.

Once the ports are forwarded, the server should be accessible externally at your public IP address on the specified ports.

## Project Structure

```bash
├── app
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── src
│   │   └── .py files
│   └── config
│       ├── habit_tracker_data.py
│       ├── months_data.py
│       ├── review_data.py
│       ├── get_db_connection.py
│       └── .env
├── nginx
│   └── default.conf
├── ssl
│   ├── auto-renew-cert.sh
│   ├── fullchain.pem
│   └── privkey.pem
├── db_data [excluded from git]
├── uploads
│   └── assets
│       └── (image files)
├── .gitignore
├── docker-compose.yml
├── LICENSE.txt
└── README.md
```

## Server Setup from Scratch

### 1. Install Required Packages

Ensure that the following packages are installed on the server:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker docker-compose nginx openssl realvnc-vnc-server
```
### 2. Clone the Repository

```bash
git clone https://github.com/ladystuart/christ0s_planner.git
cd christ0s-planner
```

### 3. Configure Environment Variables

Create a .env file inside app/config/ and add the database connection parameters:

```bash
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432
```

### 4. Configure SSL if needed

The server can use self-signed SSL certificates, which are managed by an auto-renewal script. To ensure that the script runs automatically, add it to the system's cron jobs:

```bash
chmod +x ssl/auto-renew-cert.sh
(crontab -l 2>/dev/null; echo "0 0 * * * /home/your-user-folder/server/ssl/auto-renew-cert.sh") | crontab -
```

This command schedules the script to run daily at midnight.

### 5. Start the Server

```bash
cd server
docker-compose up -d --build
```
The server will start and be accessible at https://yourdomain.com:8443 (https://your-ip:8443.).

## Database Setup

### 1. Connect to PostgreSQL Container

You can connect to your PostgreSQL database using one of the following methods:

#### With Password Prompt

```bash
docker exec -it postgres_db psql -U your-db-user -d your-db-name
```
This will prompt you to enter the password manually.

#### Without Password Prompt

```bash
PGPASSWORD="your-db-password" docker exec -it postgres_db psql -U your-db-user -d your-db-name
```
This will authenticate automatically using the provided password.

### 2. Tables (automatically created)

```bash
CREATE TABLE reading (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    language VARCHAR(100),
    status VARCHAR(50),
    link VARCHAR(255),
    series VARCHAR(255),
    banner_path VARCHAR(255),
    icon_path VARCHAR(255),
    cover_path VARCHAR(255)
);

CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE reading_authors (
    reading_id INTEGER REFERENCES reading(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (reading_id, author_id)
);

CREATE TABLE wishlist (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    image_path TEXT NOT NULL
);

CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(225) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE years (
       id SERIAL PRIMARY KEY,
       year INTEGER NOT NULL UNIQUE
   );

CREATE TABLE calendar (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       date DATE NOT NULL,
       event VARCHAR(255)
   );

CREATE TABLE yearly_plans (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    task VARCHAR(255) NOT NULL,
completed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE habit_tracker (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    week_starting DATE,
    day_of_week VARCHAR(9),
    task VARCHAR(255),
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE gratitude_diary (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       entry_date DATE,
       content TEXT
   );

CREATE TABLE review (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       question VARCHAR(255),
       answer TEXT
   );

CREATE TABLE best_in_months (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month VARCHAR(20), 
    image_path TEXT
);

CREATE TABLE months (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month_name VARCHAR(20) NOT NULL,
    icon_path VARCHAR(255),
    banner VARCHAR(255),
    reading_link VARCHAR(255),
    month_icon_path VARCHAR(255)
);

CREATE TABLE monthly_plans (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month VARCHAR(20),     
    task TEXT,        
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE monthly_diary (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month VARCHAR(20),       
    date DATE NOT NULL,       
    task TEXT,            
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE task_colours (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month VARCHAR(20),
    date DATE NOT NULL,  
    colour_code VARCHAR(7)
);

CREATE TABLE task_popups (
    id SERIAL PRIMARY KEY,
    year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
    month VARCHAR(20),    
    date DATE NOT NULL,      
    popup_message TEXT
);

CREATE TABLE work (
    id SERIAL PRIMARY KEY, 
    work_name VARCHAR(255) NOT NULL 
);

CREATE TABLE work_place (
    id SERIAL PRIMARY KEY,
    work_id INTEGER REFERENCES work(id) ON DELETE CASCADE,  
    note_text TEXT,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```
## Accessing Server Shell from Windows

To access your server's shell from a Windows machine, follow these steps:

### 1. Install an SSH Client

If you don't have an SSH client installed, you can use PuTTY or use the built-in Windows PowerShell.

#### Using PuTTY:

- Download and install PuTTY from [here](https://www.putty.org/).
- Launch PuTTY after installation.

#### Using PowerShell:

- PowerShell in Windows 10 and later includes the ssh command by default.

### 2. Get Your Server's IP Address

To connect to your server, you need to know its public IP address or hostname. If your server is behind a router, use the public IP provided by your internet service provider (ISP).

### 3. Open PuTTY or PowerShell and Connect

#### Using PuTTY:

1. Open PuTTY and enter the server's public IP address in the Host Name (or IP address) field.
2. Set the Port to 22 (default for SSH).
3. Set Connection type to SSH.
4. Click Open to start the connection.
5. You will be prompted to log in. Enter your username and password to authenticate.

#### Using PowerShell:

1. Open PowerShell.
2. Run the following command, replacing your-server-ip with the server's IP address or hostname:

```bash
ssh your-username@your-server-ip
```

## Service Descriptions

### PostgreSQL

Uses the postgres:15 image. Data is stored in ./db_data.

### Backend (FastAPI)

The Dockerfile configures the environment for running the application, which is launched using uvicorn.

### Nginx

Configuration is stored in nginx/default.conf. The server redirects traffic from 8080 to 8443.

## Attention

When setting up the server, make sure to replace the paths in the Nginx and Docker configurations with your own paths.
Follow the comments in highlighted files.

- In the **Nginx configuration file** (`nginx/default.conf`), update the paths to match your server's directory structure.
- In the **Docker configuration** (especially in the `docker-compose.yml` and Dockerfile), make sure that any references to file paths (e.g., volumes, assets, and configuration files) are correctly pointing to the actual directories on your system.
- In the **.env file** update db connection data.

Additionally, ensure that the necessary ports are properly forwarded on your router and that your server is accessible via a public IP address (white IP). Without proper port forwarding or a valid public IP, your server will not be accessible externally.

Failure to update these paths or configure the network settings may result in misconfigurations or the application failing to load the necessary resources correctly.

## Useful Docker Commands

### Restart the Server

```bash
docker-compose restart
```

### Stop the Server

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```
### Rebuild and Restart Services

```bash
docker-compose up -d --build
```

### List Running Containers

```bash
docker-compose ps
```

### Remove All Containers and Volumes

```bash
docker-compose down -v
```

## License
This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
Created by Lady Stuart.

You may use, share, and modify the code under the terms of the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).