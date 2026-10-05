# Evidencias 1

## routes_healt.py

```py
from flask import flask
from src.http.routes_healt import healt_bp

def test_healt():
    app=create_app(testing=true)
    client=app.test_client()
    response=client.get('/healt')
    assert response.status_code==200
    assert response.get_json()['runtime']=='python'
```

## dev.py

```py
from src.http.app import create_app

app = create_app()

if __name__=='__main__':
    app.run(debug=True,port=8000)
```
