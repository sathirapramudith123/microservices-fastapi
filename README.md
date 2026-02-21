
<b> type terminal </b>

gateway run
```
uvicorn main:app --reload --port 8000
``` 

student server run 
```
uvicorn main:app --reload --port 8001
```

course server run 
```
uvicorn main:app --reload --port 8002
```
</br></br>

gatway openapi
``` 
http://localhost:8000/docs#/
```

student openapi 
``` 
http://localhost:8001/docs#/
```

course openapi
``` 
http://localhost:8002/docs#/
```
