var indexport = require('./')
var tape = require('tape')

tape('export all modules', function (t) {
  var s = indexport(__dirname)
  var keys = Object.keys(s)
  t.same(keys.length, 1, 'invalid export length')
  t.same(Object.keys(s), ['test'], 'invalid export')
  t.end()
})
