# track-finance

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

## Flask Run Debug
flask run --debug

## DB Init
flask db init

## DB Migrate
flask db migrate -m "users table"

## DB Upgrade
flask db upgrade