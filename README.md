## Bunyaan Instructions

1. Install the latest version of Python (3.11.0) and pip
   https://www.python.org/doc/versions/

2. Once you have Python and pip installed create a virtual environment

```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

3. Install django

```
pip install Django==4.1.3
```

4. Clone the Bunyaan repo:

```
git clone https://github.com/alkalaminstitute/bunyaan_poc.git
```

3. In the bunyaan folder you will see multiple folders and files. To run the blockchain do the following:

Open two terminals (your starting point should be the main folder):

in terminal 1 run:

```
python manage.py runserver {port}

```

terminal 2:

```
cd frontend
rm -r node_modules
nmp install
npm start
```

After running npm start you should see a widnows open which will have the UI for interacting with the blockchain which you started using python manage.py runserver

4. To start multiple nodes you will have to repeat the steps above in a new folder. Make sure you start the blockchain and react on different ports for the additional nodes. For example if you have three nodes you will run:

```
python manage.py runserver 8000
python manage.py runserver 8001
python manage.py runserver 8002
```

There is an additonal step when it comes to react. You will have to make sure the frontend code is point to the corresponding blockchain instance. To do that make sure to chaing the following ling the /frontend/package.json to point to the right blockchin instance:

```
"proxy": "http://127.0.0.1:8000"
```

The frontend running on 3000 should point to 8000
The frontend running on 3001 should point to 8001
The frontend running on 3002 should point to 8002

Now you can start the frontend for all the nodes in their respective folders as such:

```
npm start --port 3000
npm start --port 3001
npm start --port 3002
```

Once everything is running, you can start adding transactions and smartcontracts. After mining transactions in one node, you should see them in all of the other nodes as well.

<!---
Please let me know if you find any bugs, there are a few I already know about :)
--->
