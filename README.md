100 Check Ins
=============

This is a check-in\to-do site for couples.

## How To Setup

1. Migrate & Sync DB
```
python checkin/manage.py migrate --run-syncdb
```

2. Create Super User
```
python checkin/manage.py createsuperuser
```

3. Run Server
```
python checkin/manage.py runserver <IP>:<Port>
```

4. Manage Users and Events
```
1. go to <IP>:<Port>/admin
2. login with your super user
3. update related table
```