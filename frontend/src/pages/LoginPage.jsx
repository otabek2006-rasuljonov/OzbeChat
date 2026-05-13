import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import Login from '../components/auth/Login'
import Register from '../components/auth/Register'
import { useAuth } from '../context/AuthContext'

const LoginPage = () => {
  const { isAuthenticated, login, register } = useAuth()
  const [mode, setMode] = useState('login')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submit = async (form) => {
    setIsSubmitting(true)
    setError('')
    try {
      if (mode === 'login') {
        await login(form)
      } else {
        await register(form)
      }
    } catch (err) {
      setError(err?.response?.data?.error || 'Xatolik yuz berdi')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isAuthenticated) {
    return <Navigate to="/chat" replace />
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg">
        {mode === 'login' ? (
          <Login onSubmit={submit} isSubmitting={isSubmitting} error={error} />
        ) : (
          <Register onSubmit={submit} isSubmitting={isSubmitting} error={error} />
        )}
        <button
          type="button"
          className="mt-4 text-sm text-sky-500"
          onClick={() => {
            setError('')
            setMode((prev) => (prev === 'login' ? 'register' : 'login'))
          }}
        >
          {mode === 'login' ? "Akkaunt yo'qmi? Ro'yxatdan o'ting" : 'Akkauntingiz bormi? Kirish'}
        </button>
      </div>
    </main>
  )
}

export default LoginPage
