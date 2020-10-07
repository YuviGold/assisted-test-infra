var midware = require('midware')
var MiddlewarePool = require('./pool')

module.exports = pool

function pool(parent) {
  return new MiddlewarePool(parent)
}

pool.Pool = 
pool.MiddlewarePool = MiddlewarePool
pool.midware = midware