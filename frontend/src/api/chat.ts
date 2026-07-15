export type ChatSource = {
  title: string
  paper_id: number
  chunk_index: number
}

export type ChatResponse = {
  answer: string
  sources: ChatSource[]
}

const CHAT_ENDPOINT = "/chat"

export async function askChat(question: string): Promise<ChatResponse> {
  const response = await fetch(CHAT_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  return response.json() as Promise<ChatResponse>
}
