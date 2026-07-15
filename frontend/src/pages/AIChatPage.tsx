import { Database, MessageSquareText } from "lucide-react"

import { AIChat } from "@/components/AIChat"
import { AppShell } from "@/components/AppShell"

export function AIChatPage() {
  return (
    <AppShell>
      <div className="mx-auto max-w-4xl space-y-6">
        <header className="border-b pb-6">
          <p className="flex items-center gap-2 text-sm font-medium text-primary">
            <MessageSquareText className="size-4" />
            语义检索与研究问答
          </p>
          <h1 className="mt-2 text-2xl font-semibold sm:text-3xl">和论文库对话</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            系统会先检索最相关的论文片段，再结合原文依据提供分析和合理解释。
          </p>
        </header>

        <div className="flex items-start gap-3 rounded-lg border bg-muted/20 p-4 text-sm">
          <Database className="mt-0.5 size-4 shrink-0 text-primary" />
          <p className="leading-6 text-muted-foreground">
            回答范围来自已成功解析并建立索引的 PDF。引用来源可直接进入论文详情页核对原文。
          </p>
        </div>

        <AIChat />
      </div>
    </AppShell>
  )
}
