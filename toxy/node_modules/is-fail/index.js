var errors = require('./lib/errors')
var status = require('./lib/status')
var nativeStrategies = [].concat(errors).concat(status)

module.exports = exports = function (strategies) {
  var stack = Array.isArray(strategies)
    ? nativeStrategies.concat(strategies)
    : nativeStrategies

  return function isFail(err, res) {
    return check(stack, err || {}, res || {})
  }
}

exports.check      = check
exports.errors     = errors
exports.status     = status
exports.strategies = nativeStrategies

function check(strategies, err, res) {
  return strategies.some(function (strategy) {
   return strategy(err, res)
  })
}
