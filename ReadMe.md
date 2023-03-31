# Instructions

## nginx Setup

First make sure you place ```nginx.conf``` file in the corresponding directory based on your OS. This directory typically is ```/usr/local/nginx/conf```, ```/etc/nginx```, or ```/usr/local/etc/nginx```

## Run python servers

Make sure you're in the root directory and run the following command:

```sh
python3 server.py --id 1 --port 5001
```

Then open another terminal window and run this command:

```sh
python3 server.py --id 2 --port 5002
```

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
