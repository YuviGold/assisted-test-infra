var toxy = require('toxy');
const { exit } = require('process');
var poisons = toxy.poisons
var rules = toxy.rules

const PORT = 3000

var args = process.argv.slice(2);

if (args.length < 2) {
  console.log("usage: node service.js [server] [probability]")
  exit(1)
}

var server = args[0]
var probability = args[1]

// Create the toxy admin server
var admin = toxy.admin({ cors: true })
admin.listen(9000)

// Create a new toxy proxy
var proxy = toxy()
proxy.listen(PORT)

// Add the toxy instance to be managed by the admin server
admin.manage(proxy)

// Default server to forward incoming traffic
proxy.forward(server)

proxy
  .all('/*')
 .poison(toxy.poisons.inject({
   code: 500,
   body: '{"error": "toxy injected error"}',
   headers: {'Content-Type': 'application/json'}
 }))
 .rule(rules.probability(probability))

console.log(`Port ${PORT} -> ${server}. ${probability}%`)
