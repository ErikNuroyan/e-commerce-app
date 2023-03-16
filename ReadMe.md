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

## Run server overload test

```sh
cd tests && python3 server_overload.py --request_count <request_count>
```


