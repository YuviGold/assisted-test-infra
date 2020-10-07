var midware = require('midware')
var toString = Object.prototype.toString

module.exports = MiddlewarePool

function MiddlewarePool(parent) {
  this.ctx = null
  this.pool = Object.create(null)
  if (parent) this.useParent(parent)
}

MiddlewarePool.prototype.registered = function (name) {
  return typeof this.pool[name] === 'function'
}

MiddlewarePool.prototype.flush = function (name) {
  if (this.registered(name)) {
    this.pool[name].stack.splice(0)
  }
}

MiddlewarePool.prototype.flushAll = function () {
  this.pool = Object.create(null)
}

MiddlewarePool.prototype.remove  = function (name, fn) {
  if (this.registered(name)) {
    this.pool[name].remove(fn)
  }
}

MiddlewarePool.prototype.stack = function (name) {
  if (this.registered(name)) {
    return this.pool[name].stack
  }
}

MiddlewarePool.prototype.useCtx = function (ctx) {
  this.ctx = ctx
}

MiddlewarePool.prototype.useParent = function (parent) {
  if (!(parent instanceof MiddlewarePool))
    throw new TypeError('Invalid parent middleware')

  this.parent = parent
}

MiddlewarePool.prototype.use = function (name, fn) {
  var pool = this.pool[name]
  var args = toArr(arguments, 1)

  if (!pool) {
    pool = this.pool[name] = midware(this.ctx)
  }

  if (isArgs(fn)) {
    fn = toArr(fn)
  }

  if (Array.isArray(fn)) {
    args = fn
  }

  pool.apply(null, args)
}

MiddlewarePool.prototype.runParent = function (args, done) {
  if (!this.parent) return done()
  this.parent.run.apply(this.parent, args.concat(done))
}

MiddlewarePool.prototype.run = function (name /* ...args, done */) {
  var pool = this.pool
  var args = toArr(arguments)
  var done = args.pop()

  this.runParent(args, run)

  function run(err, end) {
    if (err || end) return done(err, end)

    var middleware = pool[name]
    if (!middleware) return done()

    var cargs = args.slice(1).concat(done)
    middleware.run.apply(null, cargs)
  }
}

function toArr(args, index) {
  return [].slice.call(args, index || 0)
}

function isArgs(o) {
  return !!o && toString.call(o) === '[object Arguments]'
}
