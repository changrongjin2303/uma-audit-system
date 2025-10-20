const TokenKey = 'uma-audit-token'
const UserKey = 'uma-audit-user'

export function getToken() {
  return localStorage.getItem(TokenKey)
}

export function setToken(token) {
  return localStorage.setItem(TokenKey, token)
}

export function removeToken() {
  return localStorage.removeItem(TokenKey)
}

export function getUser() {
  const user = localStorage.getItem(UserKey)
  return user ? JSON.parse(user) : null
}

export function setUser(user) {
  return localStorage.setItem(UserKey, JSON.stringify(user))
}

export function removeUser() {
  return localStorage.removeItem(UserKey)
}