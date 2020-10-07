module.exports = [
  server,
  gateway
]

function server(err, res) {
  return !!~[500, 501].indexOf(res.statusCode)
}

function gateway(err, res) {
  return !!~[502, 503, 504].indexOf(res.statusCode)
}

