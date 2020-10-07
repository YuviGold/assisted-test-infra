const isFail = require('..')
const expect = require('chai').expect

suite('isFail', function () {

  test('errors', function () {
    var cases = [
      { error: { code: 'ETIMEDOUT' }, expect: true },
      { error: { code: 'ECONNRESET' }, expect: true },
      { error: { code: 'EADDRINFO' }, expect: true },
      { error: { code: 'ESOCKETTIMEDOUT' }, expect: true },
      { error: { code: 'ENOTFOUND' }, expect: true },
      { error: { code: 'ECONNREFUSED' }, expect: true },
      { error: { code: 'custom' }, expect: false },
      { error: { code: null }, expect: false },
    ]

    cases.forEach(function (test) {
      var failed = isFail.check(isFail.errors, test.error)
      expect(failed).to.be.equal(test.expect)
    })
  })

  test('status', function () {
    var cases = [
      { res: { statusCode: 500 }, expect: true },
      { res: { statusCode: 501 }, expect: true },
      { res: { statusCode: 502 }, expect: true },
      { res: { statusCode: 503 }, expect: true },
      { res: { statusCode: 504 }, expect: true },
      { res: { statusCode: 200 }, expect: false },
      { res: { statusCode: 204 }, expect: false },
      { res: { statusCode: 100 }, expect: false },
      { res: { statusCode: null }, expect: false },
    ]

    cases.forEach(function (test) {
      var failed = isFail.check(isFail.status, null, test.res)
      expect(failed).to.be.equal(test.expect)
    })
  })

  test('isFail', function () {
    var cases = [
      { error: null, res: { statusCode: 500 }, expect: true },
      { error: null, res: { statusCode: 200 }, expect: false },
      { error: { code: 'ETIMEDOUT' }, res: null, expect: true },
      { error: { code: null }, res: null, expect: false },
    ]

    cases.forEach(function (test) {
      var failed = isFail()(test.error, test.res)
      expect(failed).to.be.equal(test.expect)
    })
  })

})
