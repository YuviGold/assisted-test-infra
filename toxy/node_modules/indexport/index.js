var fs = require('fs')

module.exports = function indexport (dir) {
  if (typeof dir !== 'string') {
    throw new TypeError('first argument must be a string')
  }

  return fs.readdirSync(dir)
  .filter(function (file) { return /\.js$/i.test(file) })
  .filter(function (file) { return file !== 'index.js' })
  .reduce(function (hash, file) {
    hash[normalize(file)] = require(dir + '/' + file)
    return hash
  }, {})
}

function normalize (str) {
  return str
  .replace(/-([a-z])/ig, function (g) { return g[1].toUpperCase() })
  .replace(/\.js$/, '')
}
