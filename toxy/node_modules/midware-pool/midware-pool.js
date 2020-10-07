(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.midwarePool = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
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

},{"midware":2}],2:[function(require,module,exports){
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports'], factory)
  } else if (typeof exports === 'object') {
    factory(exports)
    if (typeof module === 'object' && module !== null) {
      module.exports = exports = exports.midware
    }
  } else {
    factory(root)
  }
}(this, function (exports) {
  'use strict'

  function midware(ctx) {
    var calls = use.stack = []
    ctx = ctx || null
       
    function use() {
      toArray(arguments)
      .filter(function (fn) {
        return typeof fn === 'function'
      })
      .forEach(function (fn) {
        calls.push(fn)
      })
      return ctx
    }

    use.run = function run() {
      var done, args = toArray(arguments)
      
      if (typeof args[args.length - 1] === 'function') {
        done = args.pop()
      }
      
      if (!calls.length) {
        if (done) done.call(ctx)
        return
      }
      
      var stack = calls.slice()
      args.push(next)
      
      function runNext() {
        var fn = stack.shift()
        fn.apply(ctx, args)
      }

      function next(err, end) {
        if (err || end || !stack.length) {
          stack = null
          if (done) done.call(ctx, err, end)
        } else {
          runNext()
        }
      }

      runNext()
    }

    use.remove = function (name) {
      for (var i = 0, l = calls.length; i < l; i += 1) {
        var fn = calls[i]
        if (fn === name || fn.name === name) {
          calls.splice(i, 1)
          break
        }
      }
    }

    use.flush = function () {
      calls.splice(0)
    }

    return use
  }

  function toArray(nargs) {
    var args = new Array(nargs.length)
    for (var i = 0, l = args.length; i < l; i += 1) {
      args[i] = nargs[i]
    }
    return args
  }
  
  midware.VERSION = '0.1.7'
  exports.midware = midware
}))

},{}]},{},[1])(1)
});