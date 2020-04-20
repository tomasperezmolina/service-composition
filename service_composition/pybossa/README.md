# PyBossa in Docker
Quick and dirty docker-compose script for testing my PyBossa containers.

**Database data will be lost when the container is removed!!**

# Quick Start

```
docker-compose up
```

Then, open your browser and check if it is working at: `<docker-ip>:8080`

You can find your docker-ip with:
```
docker-machine ip
```

Sign up and get your API key

# Containers
See the [PyBossa](https://github.com/jvstein/docker-pybossa) container for more details.

# Wrapper
The wrapper facilitates projects and tasks creation for tweets.
Check out the test to see its usage.
