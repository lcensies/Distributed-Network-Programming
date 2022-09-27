

## Activate virtualenv

`source venv/bin/activate`

- If for some reason it won't work, execute `pip install -r requirements.txt` additionally


## Run binaries with Docker

- **You should run scripts in the project root directory**

### Bad server

```bash
# Build image
docker build -t badserver -f ./Server/Dockerfile.badserver ./Server

# Run container
docker run --rm -it -v "${PWD}/Server/Files:/app/Files" --name badserver badserver 12300
```

### Good server


### Bad client

### Good client


## Project structure
