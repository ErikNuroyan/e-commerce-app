# Instructions

## nginx Setup

First make sure you place ```nginx.conf``` file in the corresponding directory based on your OS. This directory typically is ```/usr/local/nginx/conf```, ```/etc/nginx```, or ```/usr/local/etc/nginx```

## Run Microservices

Make sure you're in the root directory and run the following command to start the products service:

```sh
python3 products_service.py --id 1 --port 5001
```

(Optional) Then open another terminal window and run this command:

```sh
python3 products_service.py --id 2 --port 5002
```

Open another terminal window and run the following command to start the user service:

```sh
python3 user_service.py --id 3 --port 5003
```

Open another terminal window and run the following command to start the logger service:

```sh
python3 logger_service.py --id 4 --port 5004
```


Open another terminal window and run the following command to start the orders service:

```sh
python3 orders_service.py --id 5 --port 5005
```

Note that currently the MongoDB used is run on the same port for all the services and can be easily changed to a different URL and port when deployed on the cloud.

## Run nginx server for load-balancing

Open another terminal tab and run the following command:

```sh
nginx
```

## Run Redis Cache 

Open another terminal tab and run the following command:

```sh
redis-server
```

## Run server overload test

```sh
cd tests && python3 server_overload.py --request_count <request_count>
```

## System Design Info

The system uses Redis caching mechanism and 2 DBs: MongoDB for storing product information and session data, SQLAlchemy DB for user information. The Redis cache stores user information and product information, since those are the most frequently accessed data. The pattern for caching is cache aside. In case of cache miss it will populate the cache from the DB. Below is its diagram.


<img src="https://github.com/ErikNuroyan/e-commerce-app/blob/master/system_design.png"  width="700">

The caching mechanism will increase the speed of data fetching since reading from the cache is much faster than reading from the DB. Since in most of the cases the cache is populated, the DB accesses will be much less and this will have a positive impact on the performance.
