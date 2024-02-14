# Flask on Docker

## Description

For this project, I built a Flask web app using Docker, Nginx, and Gunicorn with the purpose of uploading images and/or .gifs. It can also handle static files. I used a tutorial from TestDriven, which can be found at this [link](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/#project-setup).

## File uploading process

This is what the file uploading process looks like when using the webapp:

![GIF](CSCI143-flaskgif.gif)

## Instructions

To get this webapp running, remember to run from the root.

1. Build the image and run the containers in a development environment in order to test it:
```
$ docker-compose up -d --build
```

2. Test it out at [http://localhost:40651](http://localhost:40651).

3. Once tested, bring down the containers and volumes with
```
$ docker-compose down -v
```

4. Next, try out production by first building the image and running the containers with
```
$ docker-compose -f docker-compose.prod.yml up -d --build
```

5. Create the table using
```
$ docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
```

6. Visit [http://localhost:40651](http://localhost:40651) and attempt the upload process again.

7. Bring down the process with
```
$ docker-compose -f docker-compose.prod.yml down -v
```

### Database credentials

If you encounter any errors during the process, ensure you had created your own `.env.prod` and `.env.prod.db` files with appropriate database credentials. 
