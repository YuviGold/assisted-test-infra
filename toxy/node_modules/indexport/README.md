# indexport [![Build Status](https://travis-ci.org/h2non/indexport.svg?branch=master)](https://travis-ci.org/h2non/indexport)

Node's `index.js` modules made DRYer. Just export all the modules in a directory in one sentence.

Not clear enough? Ok, let me give you an example:

Instead of writting the following `index.js` file:
```js
module.exports = {
  moduleA: require('./module-a'),
  moduleB: require('./module-b'),
  moduleC: require('./module-c'),
  moduleD: require('./module-d'),
  ...
}
```

With `indexport` you can do:
```js
module.exports = require('indexport')(__dirname)
```

Conclusion: the exported interface are exactly the same.

## Installation

```js
npm install indexport --save
```

## Usage

In your `index.js` JS file:
```js
module.exports = require('indexport')(__dirname)
```

## API

### indexport(directory) => `object`

Returns an object map with the exported modules.

## License

MIT - Tomas Aparicio
