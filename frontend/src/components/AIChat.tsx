import { FileText, MessageSquareText, Send, Sparkles } from "lucide-react"
import { useState, type KeyboardEvent } from "react"
import { Link } from "react-router-dom"

import { askChat, type ChatSource } from "@/api/chat"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

type ChatMessage = {
  question: string
  answer: string
  sources: ChatSource[]
}

type AIChatProps = {
  compact?: boolean
}

function getErrorMessage(caughtError: unknown) {
  return caughtError instanceof Error ? caughtError.message : "提问失败"
}

export function AIChat({ compact = false }: AIChatProps) {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isAsking, setIsAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleAsk() {
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion) {
      return
    }

    setIsAsking(true)
    setError(null)
    try {
      const response = await askChat(trimmedQuestion)
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          question: trimmedQuestion,
          answer: response.answer,
          sources: response.sources,
        },
      ])
      setQuestion("")
    } catch (caughtError) {
      setError(getErrorMessage(caughtError))
    } finally {
      setIsAsking(false)
    }
  }

  function handleQuestionKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void handleAsk()
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-start justify-between gap-3 border-b p-4">
        <div>
          <CardTitle className="flex items-center gap-2 text-base">
            <MessageSquareText className="size-4 text-primary" />
            论文助手
          </CardTitle>
          <p className="mt-1 text-xs text-muted-foreground">
            基于已解析和建立索引的论文回答
          </p>
        </div>
        {compact ? (
          <Link className="text-xs font-medium text-primary hover:underline" to="/ai-chat">
            展开
          </Link>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-3 p-4">
        <div
          aria-live="polite"
          className={cn(
            "space-y-3 overflow-y-auto rounded-md bg-muted/35 p-3",
            compact ? "max-h-72 min-h-28" : "max-h-[560px] min-h-72",
          )}
          role="log"
        >
          {messages.length === 0 ? (
            <div className="flex min-h-24 flex-col items-center justify-center text-center">
              <Sparkles className="size-5 text-primary" />
              <p className="mt-2 text-sm font-medium">从论文中寻找答案</p>
              <p className="mt-1 max-w-64 text-xs leading-5 text-muted-foreground">
                可以询问研究方法、变量关系、核心发现或论文之间的异同。
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div className="space-y-2" key={`${message.question}-${index}`}>
                <div className="ml-6 rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground">
                  {message.question}
                </div>
                <div className="mr-3 rounded-lg border bg-background p-3 text-sm">
                  <p className="whitespace-pre-wrap leading-6">{message.answer}</p>
                  {message.sources.length > 0 ? (
                    <div className="mt-3 space-y-1.5 border-t pt-3 text-xs text-muted-foreground">
                      {message.sources.map((source) => (
                        <Link
                          className="flex items-start gap-1.5 hover:text-primary"
                          key={`${source.paper_id}-${source.chunk_index}`}
                          to={`/papers/${source.paper_id}`}
                        >
                          <FileText className="mt-0.5 size-3.5 shrink-0" />
                          <span>
                            {source.title} · 片段 {source.chunk_index}
                          </span>
                        </Link>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            ))
          )}
        </div>

        {error ? (
          <div
            className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
            role="alert"
          >
            {error}
          </div>
        ) : null}

        <div className="flex items-end gap-2">
          <textarea
            aria-label="向论文助手提问"
            className={cn(
              "min-h-16 min-w-0 flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm outline-none transition-colors placeholder:text-muted-foreground focus-visible:ring-3 focus-visible:ring-ring/30 disabled:cursor-not-allowed disabled:opacity-50",
              compact ? "max-h-28" : "max-h-40 min-h-20",
            )}
            disabled={isAsking}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleQuestionKeyDown}
            placeholder="输入问题，按 Enter 发送..."
            value={question}
          />
          <Button
            aria-label={isAsking ? "正在发送" : "发送问题"}
            disabled={isAsking || !question.trim()}
            onClick={() => void handleAsk()}
            size="icon-lg"
            title="发送问题"
          >
            <Send />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
