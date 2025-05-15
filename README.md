# KeyBridge Server

The KeyBridge Server is the central backend component of the KeyBridge system. It manages licensing, authenticates users, provides application information, and facilitates secure application launching on clients.

## Features
- User authentication and authorization
- Communication with the KeyBridge Licensing Server
- Management of applications and user permissions
- Secure provision of login credentials and application paths
- Logging of all user activities for audits and troubleshooting

## Requirements
Check the requirements.txt

To install the required packages with `pip`:
```bash
pip install -r requirements.txt
```


## Setup
### 1. Clone the repository:
```bash
git clone https://github.com/eliasthecactus/keybridge-api
```

### 2. Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables:
Create a `.env` file and configure the variables:
```bash
cp .env-sample .env
# Configure the variables
```

### 4. Start the server:
```bash
python app.py
```

The KeyBridge Server is now accessible at `http://localhost:5000`.

### Docker Setup
You can also run the KeyBridge Server using Docker.

You can override the environment variables by specifying them when running the container (-e):
| Environment Variable        | Description                                          | Default Value        |
|-----------------------------|------------------------------------------------------|----------------------|
| `KEYBRIDGE_DB_USERNAME`      | The database username                                | `username`           |
| `KEYBRIDGE_DB_PASSWORD`      | The database password                                | `password`           |
| `KEYBRIDGE_DB_PORT`          | The database port                                    | `5432`               |
| `KEYBRIDGE_DB_NAME`          | The name of the database                             | `keybridge`          |
| `KEYBRIDGE_DB_HOST`          | The database host address                            | `127.0.0.1`          |
| `KEYBRIDGE_DEBUG`            | Set to `True` to enable debug mode                   | `False`              |
| `KEYBRIDGE_API_PORT`         | The port on which the API will run                   | `5000`               |
| `KEYBRIDGE_JWT_SECRET_KEY`   | Secret key for JWT authentication                   | `<your_jwt_secret_key>` |

#### Option 1: Using GitHub Container Registry (GHCR)
You can pull the prebuilt Docker image from the GitHub Container Registry:

```bash
docker pull ghcr.io/eliasthecactus/keybridge-api:latest
```

Then run the container:
```bash
docker run -d -p 5000:5000 ghcr.io/eliasthecactus/keybridge-api:latest
```

#### Option 2: Building from Dockerfile
Clone the repository and build the Docker image directly:

```bash
git clone https://github.com/eliasthecactus/keybridge-api
cd keybridge-server
docker build -t keybridge-api .
docker run -d -p 5000:5000 keybridge-api
```


## Notes
- This server provides the backend component for the KeyBridge Kiosk and the KeyBridge Frontend.
- Further customizations can be made to integrate the server into an existing infrastructure.


## License
This project is licensed under the KeyBridge License. See the [LICENSE](LICENSE) file for details.