# midware-pool [![Build Status](https://travis-ci.org/h2non/midware-pool.svg?branch=master)](https://travis-ci.org/h2non/midware-pool)

**midware-pool** is a **tiny module** to **create a pool** of **connect-style domain-agnostic middleware** layers for any node.js or browser application. It uses [midware](https://github.com/h2non/midware) behind the scenes.

Supports variadic arguments, stack manipulation and middleware inheritance. It's just ~180 SLOC.

To get started, see the example below or the [API usage docs](#usage).

### Example

```js
var pool = require('midware-pool')()
var message = {}

// Create foo middleware stack
pool.use('foo', function(msg, next) {
  // msg === message
  next()
})

// Create another middleware stack
pool.use('bar', function(msg, next) {
  // msg === message
  next()
})

// Run both middlewares stacks
pool.run('foo', message, function(err) {
  if (err) return console.log(err)
  
  // Run next middleware stack
  pool.run('bar', message, function(err) {
    console.log('End')
  })
})
```

## Installation

### Node.js

To install midware-pool in a Node application use npm.

```bash
npm install midware-pool
```

### Browser

Via bower:
```bash
bower install midware-pool
```

Via component:
```bash
component install h2non/midware-pool
```

Or loading the script:
```html
<script src="//cdn.rawgit.com/h2non/midware-pool/0.1.2/midware-pool.js"></script>
```

## Testing

```
$ npm install
$ npm test
```

## Usage

### Basic setup

Middleware is useful for creating a plugin system or configuring anything within an application. 
To use midware just require it and make a call to the module.

```js
var pool = require('midware-pool')()
```

This will return a `use` function which when passed a callback will add it a waterfall sequence that will be invoked one after the other whenever the middleware is run.

```js
pool.use('foo', function(next) {
  // mad science here
  next()
})
```

Callbacks are given a `next` function which will **always** be the *last* argument. Calling `next` will tell the middleware to call the next callback in the use sequence or will complete its run. To run the callback sequence call the method `run` on the `use` function.

```js
pool.run('foo', function (err, end) {
  if (err) return console.log(err)
  if (end) console.log(end)
  // all done professor
})
```

`run` takes any amount of parameters that the callbacks will passed whenever run.

```js
pool.use('foo', function (first, last, next) {
  console.log('Hello %s, %s', first, last)
  next()
})

pool.run('foo', 'Chunk', 'Norris')
```

### Stopping

Whenever a callback should throw an exception or wish to stop the middleware from running any more calls. Give `next` an error or explicitly tell it stop.

```js
pool.use('foo', function(next) {
  next(new Error()) // stops middleware and gives error
  next(null, true) // tells middleware to stop
})

pool.run('foo', function (err, ended) {
  // ...
})
```

### Apply Context

Instead of binding context to callbacks, send the context to `midware`.

```js
var context = {}
var pool = midwarePool()
pool.useCtx(context)

pool.use('foo', function (next) {
  // this === context
  next()
})

pool.run('foo', function(err) {
  // this === context
})
```

### Removing a function

You can remove registered functions in the middleware via its function name or function reference

```js
var pool = midwarePool()
pool.use('foo', function test(next) {
  next()
})
pool.remove('foo', 'test') // by function name
```

```js
var pool = midwarePool()
function test(next) {
  next()
}
pool.use('foo', test)
pool.remove('foo', test) // by function reference
```

## API

#### pool(*[parent]*) => Pool
#### Pool#use(name, ...middleware)
#### Pool#remove(name, middlewareName|function)
#### Pool#run(name, *[args...]*, *[done]*)
#### Pool#runParent(name, *[args...]*, *[done]*)
#### Pool#registered(name) => `boolean`
#### Pool#useParent(pool)
#### Pool#useCtx(ctx)
#### Pool#flush(name)
#### Pool#flushAll()
#### Pool#stack(name) => `midware`
#### Pool#pool = { ...name: midware }
#### pool.midware => [midware](https://github.com/h2non/midware)
#### pool.Pool => Pool

## License

[MIT](LICENSE)

Copyright (c) 2015 [Tomas Aparicio](https://github.com/h2non)
