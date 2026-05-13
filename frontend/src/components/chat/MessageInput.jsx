import { useState } from 'react'

const MessageInput = ({ onSend, disabled }) => {
  const [text, setText] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!onSend(text)) return
    setText('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 bg-white p-3">
      <input
        className="flex-1 rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-sky-400"
        placeholder="Xabar yozing..."
        value={text}
        onChange={(event) => setText(event.target.value)}
        disabled={disabled}
      />
      <button
        type="submit"
        className="rounded-xl bg-sky-500 px-4 font-medium text-white disabled:opacity-60"
        disabled={disabled || !text.trim()}
      >
        Yuborish
      </button>
    </form>
  )
}

export default MessageInput
