import { createContext, useContext, useState } from 'react'
import * as api from '../services/api'

const TOKEN_KEY = 'ozbechat_access_token'
const REFRESH_KEY = 'ozbechat_refresh_token'
const USERNAME_KEY = 'ozbechat_username'

const AuthContext = createContext(null)

const getInitialAuth = () => {
  const access = localStorage.getItem(TOKEN_KEY)
  const refresh = localStorage.getItem(REFRESH_KEY)
  const username = localStorage.getItem(USERNAME_KEY)
  if (!access || !refresh || !username) {
    return null
  }
  return { access, refresh, username }
}

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(getInitialAuth)

  if (auth?.access) {
    api.setAuthToken(auth.access)
  }

  const persistAuth = (tokens, username) => {
    const next = { ...tokens, username }
    setAuth(next)
    localStorage.setItem(TOKEN_KEY, tokens.access)
    localStorage.setItem(REFRESH_KEY, tokens.refresh)
    localStorage.setItem(USERNAME_KEY, username)
    api.setAuthToken(tokens.access)
  }

  const login = async ({ username, password }) => {
    const tokens = await api.login({ username, password })
    persistAuth(tokens, username)
  }

  const register = async ({ username, password }) => {
    const tokens = await api.register({ username, password })
    persistAuth(tokens, username)
  }

  const logout = () => {
    setAuth(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USERNAME_KEY)
    api.setAuthToken(null)
  }

  const value = {
    auth,
    isAuthenticated: Boolean(auth?.access),
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
