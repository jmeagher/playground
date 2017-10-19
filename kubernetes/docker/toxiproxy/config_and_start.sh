HOST_IP=$(hostname -i)

# Generate the toxiproxy config
echo "[
  {
    \"name\": \"es_http\",
    \"listen\": \"${HOST_IP}:9200\",
    \"upstream\": \"127.0.0.1:9200\"
  },
  {
    \"name\": \"es_transport\",
    \"listen\": \"${HOST_IP}:9300\",
    \"upstream\": \"127.0.0.1:9300\"
  }
]
" > toxi.json
cat toxi.json
exec /go/bin/toxiproxy -config toxi.json
