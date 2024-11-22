# self.dna

Browse your source code.

## Setup

Quickly deploy `self.dna` on your own host.

### 1. Build the Docker image

```bash
docker build -t self.dna .
```

### 2. Choose the local storage directories and port

```bash
UPLOADS_DIR="$(pwd)/uploads"
DB_DIR="$(pwd)/databases"
SELF_DNA_PORT="8050"
```

### 3. Run the container

```bash
docker run -p ${SELF_DNA_PORT}:8050 -v ${UPLOADS_DIR}:/app/uploads -v ${DB_DIR}:/app/databases self.dna
```

### 4. Connect

Your `self.dna` instance is reachable at [http://localhost:8050](http://localhost:8050).

## Licence

This work is distributed under the [Apache-2.0 license](https://www.apache.org/licenses/LICENSE-2.0.txt).

Copyright 2024 Alessandro Lussana