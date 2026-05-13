const MessageBubble = ({ message, isOwnMessage }) => {
  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm shadow ${
          isOwnMessage
            ? 'rounded-br-md bg-sky-500 text-white'
            : 'rounded-bl-md bg-white text-slate-700'
        }`}
      >
        <p className={`text-xs ${isOwnMessage ? 'text-sky-100' : 'text-slate-400'}`}>{message.username}</p>
        <p className="whitespace-pre-wrap break-words">{message.message}</p>
        <p className={`mt-1 text-right text-[11px] ${isOwnMessage ? 'text-sky-100' : 'text-slate-400'}`}>{message.time}</p>
      </div>
    </div>
  )
}

export default MessageBubble
