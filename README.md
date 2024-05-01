# Flask on Docker

## Description

For this project, I built a Flask web app using Docker, Nginx, and Gunicorn with the purpose of uploading images and/or .gifs. It can also handle static files. I used a tutorial from TestDriven.io, which can be found at this [link](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/#project-setup).

## File uploading process

This is what the file uploading process looks like when using the webapp:

![GIF](CSCI143-flaskgif.gif)

## Instructions

### Database credentials

Ensure you have created your own `.env.prod` and `.env.prod.db` files with appropriate database credentials. You can find more information on how to do this in the TestDriven.io tutorial linked in the description. 

### Running the programs and getting images and containers up

To get this webapp running, remember to run from the root.

1. Build the image and run the containers in a development environment in order to test it:
```
$ docker-compose up -d --build
```
* Check if your container is running and working with
```
$ curl http://localhost:1362
```
* This should return
```
{
    "hello": "world"
}
```

2. If the check worked, test by visiting [http://localhost:1362/upload](http://localhost:1362/upload).

3. Once tested, bring down the containers and volumes with
```
$ docker-compose down -v
```

4. Next, try out production by first building the image and running the containers with
```
$ docker-compose -f docker-compose.prod.yml up -d --build
```
* Check if your container is running and working with
```
$ curl http://localhost:40651
```

5. Create the table using
```
$ docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
```

6. Visit [http://localhost:1362/upload](http://localhost:1362/upload) and attempt the upload process again.

7. Visit [http://localhost:1362/media/MEDIA_FILE_NAME](http://localhost:1362/media/MEDIA_FILE_NAME) to see the image or gif you just uploaded.
 
8. Once done, bring down the process with
```
$ docker-compose -f docker-compose.prod.yml down -v
``` 
