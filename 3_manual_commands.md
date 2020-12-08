#iot_bucket
ssh root@178.128.107.247
Blockchain@2020#Peerhlf

ssh root@128.199.151.251
JWCLab@2020#Identity

#login
curl -d '{"id":"admin_stations","password":"11111111"}' -H "Content-Type: application/json" -X POST http://identity.jwclab.com:32768/login

#Token 
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Il9pZCI6Im1hdV94eHgiLCJwYXNzd29yZCI6Imp3Y2xhYiIsInJvbGUiOiJzdGF0aW9uIn0sImlhdCI6MTYwMDY2MjQ0NiwiZXhwIjoxOTE2MDIyNDQ2fQ.dMgB5QNmLXwh1E959rV2U-F941faT9a8W_OOCYZ11Jg

#add record
curl -d '{"id":"lienchieu_station","datetime":"2020-09-21T03:13:34.089375Z","range":"2020-09-21T03:13:34.089375Z--2020-09-21T04:04:12.172950Z","hash":"07ece12923a2f750d1d7e979164e8fc3"}' -H "Content-Type: application/json" -H "x-access-token: $token" -X POST http://identity.jwclab.com:32768/add

#history
curl -d '{"id":"lienchieu_station"}' -H "Content-Type: application/json" -H "x-access-token: $token" -X POST http://identity.jwclab.com:32768/history

#historybytime
curl -d '{"id":"lienchieu_station", "start":"2020-09-25T07:30:00Z", "end":"2020-09-25T07:32:06.361520Z"}' -H "Content-Type: application/json" -H "x-access-token: $token" -X POST http://identity.jwclab.com:32768/historybytime

#getrecord
curl -d '{"id":"lienchieu_station"}' -H "Content-Type: application/json" -H "x-access-token: $token" -X POST http://identity.jwclab.com:32768/getrecord

#updatestation
curl -d '{"id": "haichau_station","location":"16.0802466,108.2178086","name": "Tram Tam Ky","address": "Hue","manager": "Pham Hoa Mau","phone": "09696969696"}' -H "Content-Type: application/json" -H "x-access-token: $token" -X POST http://identity.jwclab.com:32768/updatestation


http://192.168.0.107:5000/historyData/haichau_station%202020-09-28T01:00:00Z%202020-09-28T01:30:00Z
