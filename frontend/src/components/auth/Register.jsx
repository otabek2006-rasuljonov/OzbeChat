import { useState } from 'react'

const Register = ({ onSubmit, isSubmitting, error }) => {
  const [form, setForm] = useState({ username: '', password: '' })

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-xl font-semibold text-slate-900">Ro'yxatdan o'tish</h2>
      <input
        className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-sky-400"
        name="username"
        placeholder="Username"
        value={form.username}
        onChange={handleChange}
        required
      />
      <input
        className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-sky-400"
        type="password"
        name="password"
        placeholder="Parol"
        value={form.password}
        onChange={handleChange}
        required
      />
      {error ? <p className="text-sm text-red-500">{error}</p> : null}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-xl bg-emerald-500 py-3 font-medium text-white disabled:opacity-70"
      >
        {isSubmitting ? 'Kutilmoqda...' : 'Ro\'yxatdan o\'tish'}
      </button>
    </form>
  )
}

export default Register
