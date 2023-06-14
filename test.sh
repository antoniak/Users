curl -i -X POST -H "Content-Type: application/json" -d '{"username":"antonia","password":"pass","email":"antonia@antonia.com"}' http://127.0.0.1:5000/api/register
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"john","password":"passs","email":"john@smith.com"}' http://127.0.0.1:5000/api/register
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"joe","password":"password","email":"joe@doe.com"}' http://127.0.0.1:5000/api/register

curl -i -X GET http://127.0.0.1:5000/api/users
curl -u antonia:pass -i -X GET http://127.0.0.1:5000/api/token

curl -u antonia:pass -i -X DELETE http://127.0.0.1:5000/api/delete/joe
curl -u antonia:pass -i -X PUT http://127.0.0.1:5000/api/activate/john
curl -u antonia:pass -i -X PUT http://127.0.0.1:5000/api/deactivate/john

