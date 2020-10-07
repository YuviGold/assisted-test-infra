module.exports = [
  econnreset,
  econnrefused,
  etimedout,
  enotfound,
  eaddrinfo,
  esockettimedout
]

function econnreset(err, res) {
  return err.code === 'ECONNRESET'
}

function etimedout(err, res) {
  return err.code === 'ETIMEDOUT'
}

function eaddrinfo(err, res) {
  return err.code === 'EADDRINFO'
}

function esockettimedout(err, res) {
  return err.code === 'ESOCKETTIMEDOUT'
}

function enotfound(err, res) {
  return err.code === 'ENOTFOUND'
}

function econnrefused(err, res) {
  return err.code === 'ECONNREFUSED'
}
